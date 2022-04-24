import json
from flask import request, url_for, g, current_app, Response
from drowsy.exc import (
    UnprocessableEntityError, BadRequestError, MethodNotAllowedError,
    ResourceNotFoundError
)
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from bender_mc.audio_controller import AudioController
from bender_mc.browser_controller import BrowserController
from bender_mc.kodi.rpc_client import KodiRpcClient


# Database session/engine management.
# Basically rolling our own pseudo Flask-SQLAlchemy
db_scoped_sessions = {}
db_engines = {}
audio_controller = AudioController()
browser_registry = []


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


# browser controller setup
def load_browser_controller():
    if not browser_registry:
        config = current_app.config
        ublock_path = config["browser"]["ublock_path"]
        browser_registry.append(
            BrowserController(extension_paths=[ublock_path]))
    g.browser_controller = browser_registry[-1]


def get_browser_controller():
    return getattr(g, "browser_controller", None)


def ensure_kodi():
    """Make sure Kodi is running and bring to front of screen."""
    pass


def url_for_other_page(page):
    """Simple helper function for pagination headers."""
    args = dict(
        request.view_args.items() | request.args.to_dict().items())
    args['page'] = page
    return url_for(request.endpoint, **args)

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
