import inflect
import re
from drowsy.exc import DrowsyError
from flask import Blueprint
from bender_mc.api.utils import (
    close_db_sessions, get_scoped_db_session, generic_drowsy_error_handler,
    load_db_sessions)
from bender_mc.kodi.models.video import Movie, TvShow, Episode


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
