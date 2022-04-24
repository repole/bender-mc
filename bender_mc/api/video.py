import json
import os
import pytz
import statsapi
import subprocess
from datetime import datetime, timedelta
from drowsy.exc import BadRequestError, DrowsyError
from drowsy.resource import ResourceCollection
from drowsy.router import ModelResourceRouter
from flask import current_app, request, Blueprint, Response
from sqlalchemy import Integer
from bender_mc.api.utils import (
    close_db_sessions, generic_drowsy_error_handler, get_browser_controller,
    get_rpc_client, get_scoped_db_session, load_browser_controller,
    load_db_sessions, load_rpc_client, url_for_other_page)
from bender_mc.kodi.resources.video import *
from bender_mc.kodi.models.video import Movie, TvShow, Episode, File, Bookmark
from bender_mc.utils import deformat_title


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


video_api_blueprint = Blueprint('video_api_blueprint', __name__)


@video_api_blueprint.before_request
def before_video_api_request():
    load_db_sessions()
    load_rpc_client()
    load_browser_controller()


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
        try:
            media_id = int(media_split[0])
        except ValueError:
            media_id = media_split[0]
        media_type = media_split[1]
    if str(media_id).lower() == "null":
        media_id = None
    browser_controller = get_browser_controller()
    if media_id and media_type:
        if media_type != "nba":
            script = os.path.join(
                os.path.dirname(__file__), "..", "scripts",
                "bring_to_front.ps1")
            p = subprocess.Popen(
                ["powershell.exe", script], stdout=subprocess.PIPE)
            p.wait()
            browser_controller.close_driver()
        if media_type == "tvshow":
            tv_show = db_session.query(TvShow).filter(
                TvShow.id_show == media_id).first()
        elif media_type == "movie":
            movie = db_session.query(Movie).filter(
                Movie.id_movie == media_id).first()
        elif media_type == "episode":
            episode = db_session.query(Episode).filter(
                Episode.id_episode == media_id).first()
        elif media_type == "mlb":
            team = media_id
            # i only watch red sox games, fuck the team logic for now
            game_info = mlb_game_info()
            home = None
            status = None
            list_index = None
            for list_index, game in enumerate(game_info):
                status = game["status"]
                if game["away_name"] == "Boston Red Sox":
                    home = False
                    break
                if game["home_name"] == "Boston Red Sox":
                    home = True
                    break
            if list_index is not None:
                rpc_client.play_mlb(list_index, is_home=home, game_status=status)
            return {"result": "success"}
        elif media_type == "nba":
            attempts = 2
            while attempts > 0:
                attempts += -1
                result = browser_controller.play_nba_game(
                    username=current_app.config["nba"]["username"],
                    password=current_app.config["nba"]["password"],
                    team=media_id
                )
                if result:
                    attempts = 0
            return {"result": "success"}
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


def mlb_game_info():
    mlb_date = datetime.now(pytz.timezone('US/Eastern'))
    mlb_hour = mlb_date.strftime('%H')
    if int(mlb_hour) < 3:
        # switch to next day only after 4am
        mlb_date = mlb_date - timedelta(days=1)
    mlb_date_str = mlb_date.strftime('%Y-%m-%d')
    sched = statsapi.schedule(start_date=mlb_date_str, end_date=mlb_date_str)
    return sched
