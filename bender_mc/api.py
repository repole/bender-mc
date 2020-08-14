"""
    bender_mc.api
    ~~~~~~~~~~~~~

    API WSGI app, used to interact with a media center.
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
import inflect
import json
import re
import os
import subprocess
import tempfile
from contextlib import suppress
from multiprocessing import Process
from flask import request, Response, url_for, g, Blueprint, current_app
from bender_mc import playsound
from sqlalchemy import create_engine, Integer
from sqlalchemy.orm import scoped_session, sessionmaker
from drowsy.exc import (
    UnprocessableEntityError, BadRequestError, MethodNotAllowedError,
    ResourceNotFoundError
)
from drowsy.resource import ResourceCollection
from drowsy.router import ModelResourceRouter
from drowsy.exc import DrowsyError
from bender_mc.audio_controller import AudioController
from bender_mc.kodi.resources.video import *
from bender_mc.kodi.models.video import Movie, TvShow, Episode, File, Bookmark
from bender_mc.utils import deformat_title
from bender_mc.kodi.rpc_client import KodiRpcClient

# Database session/engine management.
# Basically rolling our own pseudo Flask-SQLAlchemy
db_scoped_sessions = {}
db_engines = {}


def set_db_engine(engine_name, connect_string):
    """Add a database engine connect string to a dict of engines."""
    if engine_name not in db_engines:
        db_engines[engine_name] = create_engine(connect_string, echo=False)
        db_scoped_sessions[engine_name] = scoped_session(sessionmaker(
            bind=db_engines[engine_name], autoflush=True, autocommit=False))


def get_db_engine(engine_name):
    """Get a db engine connect string based on name (if set prior)."""
    if engine_name in db_engines:
        return db_engines[engine_name]


def configure_scoped_db_session(engine_name):
    """Returns a scoped db session for this engine."""
    if engine_name in db_engines and engine_name in db_scoped_sessions:
        return db_scoped_sessions[engine_name]
    raise ValueError("No such database.")


def set_scoped_db_session(engine_name, db_session):
    if hasattr(g, "db_sessions"):
        g.db_sessions[engine_name] = db_session
    else:
        g.db_sessions = dict()
        g.db_sessions[engine_name] = db_session


def get_scoped_db_session(engine_name=None):
    if hasattr(g, "db_sessions") and isinstance(g.db_sessions, dict):
        if engine_name is not None:
            if engine_name in g.db_sessions:
                return g.db_sessions[engine_name]
            raise Exception("No such session has been "
                            "registered with this request.")
        else:
            return g.db_sessions
    else:
        return None


def load_db_sessions():
    """Loads and configures any db sessions into the request context.

    Registers these database session in the context of the current
    request. Should be run at the beginning of any request that needs
    access to the core database. The plurality of the function name
    implies that this is where any additional database sessions should
    be loaded. For now it only configures the "video" db session.

    """
    db_session = configure_scoped_db_session("video")
    set_scoped_db_session("video", db_session)


def close_db_sessions():
    """Closes all db sessions that were opened during this request."""
    db_sessions = get_scoped_db_session()
    if db_sessions is not None:
        for key in db_sessions:
            try:
                db_sessions[key].commit()
            except Exception as e:
                db_sessions[key].rollback()
                raise Exception(
                    "Problem committing db_session on request close.")
            finally:
                db_sessions[key].remove()


# Rpc Client Setup
def load_rpc_client():
    config = current_app.config
    if not hasattr(g, "rpc_client"):
        g.rpc_client = KodiRpcClient(
            base_url=config["kodirpc"]["url"],
            username=config["kodirpc"]["username"],
            password=config["kodirpc"]["password"])


def get_rpc_client():
    return getattr(g, "rpc_client", None)


# Helper functions for our API

def url_for_other_page(page):
    """Simple helper function for pagination headers."""
    args = dict(
        request.view_args.items() | request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)


def find_next_episode(db_session, tv_show=None, episode=None):
    if not episode:
        # Find the most recently played bookmarked episode
        bookmarked_file = db_session.query(File).filter(
            File.episodes.any(Episode.id_show == tv_show.id_show)
        ).filter(
            File.bookmarks.any(Bookmark.time_in_seconds > 0)
        ).order_by(
            File.last_played.desc()
        ).first()
        if bookmarked_file:
            return bookmarked_file.episodes[0]
        # If no bookmarks, try to find the earliest unplayed episode
        unplayed = db_session.query(Episode).filter(
            Episode.id_show == tv_show.id_show
        ).filter(
            Episode.file.has(File.play_count.is_(None))
        ).order_by(
            Episode.season_number.cast(Integer).asc(), Episode.episode_number.cast(Integer).asc()
        ).first()
        if unplayed:
            return unplayed
        # all episodes have been played, so find the last played episode
        # then play the episode after that
        last_played_file = db_session.query(File).filter(
            File.episodes.any(Episode.id_show == tv_show.id_show)
        ).order_by(
            File.last_played.desc()
        ).first()
    else:
        last_played_file = episode.file
    if last_played_file:
        last_played = last_played_file.episodes[0]
        next_up = db_session.query(Episode).filter(
            Episode.id_show == last_played.id_show
        ).filter(
            Episode.season_number == last_played.season_number
        ).filter(
            Episode.episode_number == (int(last_played.episode_number) + 1)
        ).first()
        if next_up:
            return next_up
        next_up = db_session.query(Episode).filter(
            Episode.id_show == last_played.id_show
        ).filter(
            Episode.season_number == (int(last_played.season_number) + 1)
        ).filter(
            Episode.episode_number == 1
        ).first()
        if next_up:
            return next_up
    # User has either watched no episodes, or watched all episodes
    # Loop back to beginning
    return db_session.query(Episode).filter(
        Episode.id_show == tv_show.id_show).filter(
        Episode.season_number == 1).filter(
        Episode.episode_number == 1).first()


def generic_drowsy_error_handler(error):
    if error:
        errors = None
        try:
            raise error
        except UnprocessableEntityError as exc:
            status = 433
            errors = exc.errors
            message = exc.message
            code = exc.code
        except MethodNotAllowedError as exc:
            status = 405
            message = exc.message
            code = exc.code
        except BadRequestError as exc:
            status = 400
            message = exc.message
            code = exc.code
        except ResourceNotFoundError as exc:
            status = 404
            message = exc.message
            code = exc.code
        if code is not None or message:
            if request.method.upper() == "HEAD":
                result = None
            else:
                result = {"message": message, "code": code}
                if errors:
                    result["errors"] = errors
            return Response(
                json.dumps(result),
                mimetype="application/json",
                status=status)


# Set up slots api flask blueprint
slots_blueprint = Blueprint('slots_blueprint', __name__)


@slots_blueprint.before_request
def before_slots_api_request():
    load_db_sessions()


@slots_blueprint.teardown_request
def teardown_slots_api_teardown_request(error):
    close_db_sessions()


@slots_blueprint.errorhandler(DrowsyError)
def slots_error_handler(error):
    return generic_drowsy_error_handler(error)


def title_to_spoken_text(title):
    inflector = inflect.engine()
    manual_mappings = {
        "50/50": "fifty fifty",
        "3:10 to Yuma": "three ten to yuma",
        "1917": "nineteen seventeen",
        "Star Wars: Episode 1 - The Phantom Menace": "star wars episode one",
        "Star Wars: Episode II - Attack of the Clones": "star wars episode two",
        "Star Wars: Episode III - Revenge of the Sith": "star wars episode three",
        "Star Wars: Episode IV - A New Hope": "star wars",
        "Star Wars: Episode V - The Empire Strikes Back": (
            "star wars the empire strikes back"),
        "Star Wars: Episode VI - Return of the Jedi": (
            "star wars return of the jedi"),
    }
    if title in manual_mappings:
        return manual_mappings[title]
    # remove anything between parenthesis
    # for things like The Office (US)
    spoken_text = re.sub(r'\([^)]*\)', '', title)
    # remove special characters and split on spaces
    spoken_text = spoken_text.replace("&", "and")
    spoken_text_tokens = [re.sub(
        r"[^\w\d']+", ' ', x).strip() for x in spoken_text.split(" ")]
    spoken_text_tokens = [t for t in spoken_text_tokens if t]
    cleaned_tokens = []
    for token in spoken_text_tokens:
        try:
            if token == "ii":
                cleaned_token = "two"
            if token == "iii":
                cleaned_token = "three"
            elif token == "iv":
                cleaned_token = "four"
            elif token == "vi":
                cleaned_token = "six"
            cleaned_token = inflector.number_to_words(token)
            cleaned_token = cleaned_token.replace("-", " ")
            if cleaned_token in ["zero", "zeroth"]:
                # A value like 13th will be converted successfully
                # A value like abcd will get converted to zero
                # if the first value of our string is a digit, we're
                # probably ok (e.g. 0th or 0)
                # If the first digit isn't an int, this will fail
                int(token[0])
            cleaned_tokens.append(cleaned_token)
        except ValueError:
            cleaned_tokens.append(token)
    if cleaned_tokens and cleaned_tokens[0] == "the":
        cleaned_tokens.pop(0)
    if cleaned_tokens and cleaned_tokens[-1] == "the":
        cleaned_tokens.pop()
    spoken_text = " ".join(cleaned_tokens).lower()
    return spoken_text


@slots_blueprint.route("/video", methods=["GET"])
def slots_video_router():
    db_session = get_scoped_db_session("video")
    results = {}
    tv_shows = db_session.query(TvShow).all()
    movies = db_session.query(Movie).all()
    output = ""
    for movie in movies:
        if movie.title not in results:
            results[movie.title] = title_to_spoken_text(movie.title)
    for tv_show in tv_shows:
        if tv_show.title not in results:
            results[tv_show.title] = title_to_spoken_text(tv_show.title)
    for key in results:
        spoken_text = results[key]
        converted_value = key
        output += f"({spoken_text}):({converted_value})\n"
    return output


def generate_video_slots(db_session):
    """Get movie, tvshow, and episode slots in tuple of dicts format.

    Key in each tuple is the spoken text, Value is an underscore
    separated combination of media_id and media_type:

        {"kill bill one": "1234_movie"}

    """
    # Always have to generate slots for all videos, even if we only
    # care about one particular type.
    # This allows us to handle and avoid collisions
    # (e.g. Spider-man (1994) tv show vs Spider-man the movie)
    all_results = {}
    movie_results = {}
    movies = db_session.query(Movie).all()
    episode_results = {}
    episodes = db_session.query(Episode).all()
    tv_show_results = {}
    tv_shows = db_session.query(TvShow).all()
    for media_type in ["movie", "tvshow", "episode"]:
        media_title_name = "title"
        if media_type == "tvshow":
            media_id_name = "id_show"
            results = tv_show_results
            media = tv_shows
        elif media_type == "episode":
            media_id_name = "id_episode"
            results = episode_results
            media = episodes
        else:
            media_id_name = "id_movie"
            results = movie_results
            media = movies
        for item in media:
            if media_type == "episode":
                # special case
                episode_title = getattr(item, media_title_name)
                tv_show_title = item.tv_show.title
                title = " ".join([tv_show_title, episode_title])
                spoken_text = title_to_spoken_text(title)
            else:
                spoken_text = title_to_spoken_text(getattr(item, media_title_name))
            while spoken_text in all_results:
                spoken_text = "the other " + spoken_text
            converted_value = "-".join([str(getattr(item, media_id_name)), media_type])
            results[spoken_text] = converted_value
            all_results[spoken_text] = converted_value
    return movie_results, tv_show_results, episode_results


@slots_blueprint.route("/movies", methods=["GET"])
def slots_movies_router():
    db_session = get_scoped_db_session("video")
    results = generate_video_slots(db_session)[0]
    output = ""
    for key in results:
        spoken_text = key
        converted_value = results[key]
        output += f"({spoken_text}):({converted_value})\n"
    return output


@slots_blueprint.route("/tvShows", methods=["GET"])
def slots_tv_shows_router():
    db_session = get_scoped_db_session("video")
    results = generate_video_slots(db_session)[1]
    output = ""
    for key in results:
        spoken_text = key
        converted_value = results[key]
        output += f"({spoken_text}):({converted_value})\n"
    return output


@slots_blueprint.route("/episodes", methods=["GET"])
def slots_episodes_router():
    db_session = get_scoped_db_session("video")
    results = generate_video_slots(db_session)[2]
    output = ""
    for key in results:
        spoken_text = key
        converted_value = results[key]
        output += f"({spoken_text}):({converted_value})\n"
    return output


media_center_api_blueprint = Blueprint('media_center_api_blueprint', __name__)


@media_center_api_blueprint.before_request
def before_media_center_api_request():
    load_db_sessions()
    load_rpc_client()


@media_center_api_blueprint.teardown_request
def teardown_media_center_api_teardown_request(error):
    close_db_sessions()


@media_center_api_blueprint.route("/speakers/play", methods=["POST"])
def media_center_speakers_play():
    tmpdir = tempfile.TemporaryDirectory()
    temp_file_path = os.path.join(tmpdir.name, "test.wav")
    with open(temp_file_path, "wb") as file:
        file.write(request.data)
    playsound.playsound(temp_file_path)
    os.remove(temp_file_path)
    tmpdir.cleanup()
    return {"result": "success"}


@media_center_api_blueprint.route("/speakers/volume", methods=["POST"])
def media_center_speakers_volume():
    # unfortunately pycaw does not want to play nicely with Flask
    # We spawn separate processes just to adjust the volume
    # incredibly inefficient, and slight delay, but it works.
    data = request.json
    value = data["volumeLevel"]
    amount = data.get("amount")
    with suppress(ValueError):
        value = int(value)
    with suppress(ValueError):
        amount = int(amount)
    p = None
    if str(value).lower() == "mute":
        p = Process(target=AudioController().mute)
    elif str(value).lower() == "unmute":
        p = Process(target=AudioController().unmute)
    else:
        if str(amount).lower() == "a lot":
            amount = 20
        else:
            amount = 10
        if str(value).lower() == "decrease":
            p = Process(target=AudioController().adjust_volume, args=(amount * -1, ))
        elif str(value).lower() == "increase":
            p = Process(target=AudioController().adjust_volume, args=(amount, ))
        elif isinstance(value, int):
            p = Process(target=AudioController().set_volume, args=(int(value), ))
    if p:
        p.start()
        p.join()
    return {"result": "success"}


@media_center_api_blueprint.route("/monitors/switch", methods=["POST"])
def media_center_switch_monitor_router():
    rpc_client = get_rpc_client()
    monitor = rpc_client.get_monitor()
    if "1" in monitor:
        monitor = monitor.replace("1", "2")
    else:
        monitor = monitor.replace("2", "1")
    rpc_client.set_fullscreen()

    import threading
    t = threading.Thread(target=rpc_client.set_monitor, args=(monitor,))
    t.start()
    # rpc_client.set_monitor(monitor)
    rpc_client.execute_action(action="green")
    rpc_client.post_rpc(method="Input.Down", params={})
    rpc_client.post_rpc(method="Input.Left", params={})
    rpc_client.post_rpc(method="Input.Select", params={})
    t.join()
    return {"result": "success"}


@media_center_api_blueprint.route("/rooms/switch", methods=["POST"])
def media_center_switch_room_router():
    data = request.json
    room_id = data.get("roomId", None)
    if room_id == "bedroom":
        arg = "external"
    else:
        arg = "extend"
    script = os.path.join(os.path.dirname(__file__), "display_switch.ps1")
    p = subprocess.Popen(
        ["powershell.exe", script, arg], stdout=subprocess.PIPE)
    p.wait()
    return {"result": "success"}


# Set up actual video api flask blueprint
video_api_blueprint = Blueprint('video_api_blueprint', __name__)


@video_api_blueprint.before_request
def before_video_api_request():
    load_db_sessions()
    load_rpc_client()


@video_api_blueprint.teardown_request
def teardown_video_api_teardown_request(error):
    close_db_sessions()


@video_api_blueprint.errorhandler(DrowsyError)
def video_api_error_handler(error):
    return generic_drowsy_error_handler(error)


@video_api_blueprint.route("/player/state", methods=["POST"])
def video_player_state_router():
    action = request.data.decode("utf-8")
    rpc_client = get_rpc_client()
    if action.lower() == "resume":
        rpc_client.play_pause_toggle()
    elif action.lower() == "pause":
        rpc_client.play_pause_toggle()
    elif action.lower() == "next":
        rpc_client.play_next()
    return {"result": "success"}


@video_api_blueprint.route("/player/queue", methods=["POST"])
def video_player_queue_router():
    num_episodes = int(request.json.get("number", 0))
    # get currently playing episode
    # find next x episodes
    pass


@video_api_blueprint.route("/player/media", methods=["POST"])
def video_player_media_router():
    db_session = get_scoped_db_session("video")
    script = os.path.join(os.path.dirname(__file__), "bring_to_front.ps1")
    p = subprocess.Popen(
        ["powershell.exe", script], stdout=subprocess.PIPE)
    p.wait()
    rpc_client = get_rpc_client()
    data = request.json
    media_id = data.get("mediaId", None)
    media_type = data.get("mediaType", None)
    media_title = data.get("mediaTitle", None)
    media_combo_id = data.get("mediaComboId", None)
    queue_next = data.get("queueNext", None)
    if queue_next:
        try:
            queue_next = int(queue_next)
        except ValueError:
            queue_next = 1
    movie = None
    tv_show = None
    episode = None
    resume_time = 0
    if media_combo_id:
        media_split = media_combo_id.split("-")
        media_id = int(media_split[0])
        media_type = media_split[1]
    if media_id and media_type:
        if media_type == "tvshow":
            tv_show = db_session.query(TvShow).filter(
                TvShow.id_show == media_id).first()
        elif media_type == "movie":
            movie = db_session.query(Movie).filter(
                Movie.id_movie == media_id).first()
        elif media_type == "episode":
            episode = db_session.query(Episode).filter(
                Episode.id_episode == media_id).first()
    elif media_id and media_title:
        tv_show = db_session.query(TvShow).filter(
            TvShow.title == media_title
        ).filter(
            TvShow.id_show == media_id
        ).first()
        movie = db_session.query(Movie).filter(
            Movie.title == media_title
        ).filter(
            Movie.id_movie == media_id
        ).first()
        episode = db_session.query(Episode).filter(
            Episode.title == media_title
        ).filter(
            Episode.id_movie == media_id
        ).first()
    elif media_id:
        raise BadRequestError(
            code="missing_input",
            message=(
                "Must provide at least one of mediaType or mediaTitle "
                "along with mediaId"
            )
        )
    elif media_title:
        media_title = deformat_title(media_title)
        if media_type == "movie" or not media_type:
            movie = db_session.query(Movie).filter(
                Movie.title == media_title).first()
        if media_type == "tvshow" or not media_type:
            tv_show = db_session.query(TvShow).filter(
                TvShow.title == media_title).first()
        if media_type == "epsidoe" or not media_type:
            episode = db_session.query(Episode).filter(
                Episode.title == media_title).first()
    # Now we should have at least one of movie/tvshow/episode
    if movie:
        media_id = movie.id_movie
        media_type = "movie"
        if movie.file is not None:
            for bookmark in movie.file.bookmarks:
                if bookmark.type == 1:
                    resume_time = bookmark.time_in_seconds
    elif tv_show:
        media_type = "episode"
        # find next episode for TV Show
        episode = find_next_episode(db_session, tv_show=tv_show)
        if episode:
            media_id = episode.id_episode
    elif episode:
        media_id = episode.id_episode
        media_type = "episode"
    # Now only have movie and/or episode
    if media_type == "episode":
        if episode is not None and episode.file is not None:
            for bookmark in episode.file.bookmarks:
                if bookmark.type == 1:
                    resume_time = bookmark.time_in_seconds
        if queue_next:
            media_id = [media_id]
            last_episode = episode
            for i in range(0, queue_next):
                # try next episode of this season
                next_up = find_next_episode(db_session, episode=last_episode)
                media_id.append(next_up)
                last_episode = next_up
        # multi episode here...
    if media_id is not None and media_type is not None:
        rpc_client.play_video(
            media_id=media_id, media_type=media_type, resume_time=resume_time)
        rpc_client.set_fullscreen()
        return {"result": "success"}
    raise BadRequestError(
        code="no_media_found",
        message="No such video found.")


@video_api_blueprint.route(
    "<path:path>",
    methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
def api_router(path):
    """Generic API router.

    You'll probably want to be more specific with your routing.

    We're using the ModelResourceRouter, which automatically routes
    based on the class name of each Resource, and handles nested
    routing, querying, and updating automatically.

    """
    # get your SQLAlchemy db session however you normally would
    db_session = get_scoped_db_session("video")
    # This should be some context related to the current request.
    # Note that context can be used by resources/schemas to help
    # handle things like permissions/access, and would typically
    # contain any user related info for this request.
    context = {}
    router = ModelResourceRouter(session=db_session, context=context)
    # query params are used to parse fields to include, embeds,
    # sorts, and filters.
    query_params = request.values.to_dict()
    status = 200
    response_headers = {}
    if request.method.upper() == "POST":
        status = 201
    result = router.dispatcher(
        request.method,
        path,
        query_params=query_params,
        data=request.json)
    if request.method.upper() == "OPTIONS":
        response_headers["Allow"] = ",".join(result)
        result = None
    if isinstance(result, ResourceCollection):
        # Handle providing prev, next, first, last page links header
        links = []
        if result.current_page is not None:
            link_template = '<{link}>; rel="{rel}"'
            if result.first_page:
                links.append(link_template.format(
                    link=url_for_other_page(result.first_page),
                    rel="first"))
            if result.previous_page:
                links.append(link_template.format(
                    link=url_for_other_page(result.previous_page),
                    rel="prev"))
            if result.next_page:
                links.append(link_template.format(
                    link=url_for_other_page(result.next_page),
                    rel="next"))
            if result.last_page:
                links.append(link_template.format(
                    link=url_for_other_page(result.last_page),
                    rel="last"))
        links_str = ",".join(links)
        if links_str:
            response_headers["Link"] = links_str
        # Handle successful HEAD requests
        if request.method.upper() == "HEAD":
            result = None
    if result is not None:
        result = json.dumps(result)
    return Response(
        result,
        headers=response_headers,
        mimetype="application/json",
        status=status
    )
