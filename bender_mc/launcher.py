"""
    bender_mc.launcher
    ~~~~~~~~~~~~~~~~~~

    Entry points for the bender-mc api.
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
import ast
import configparser
import logging
from logging.handlers import TimedRotatingFileHandler
import os
import click
import flask
from .api import (
    video_api_blueprint, slots_blueprint, media_center_api_blueprint,
    set_db_engine)
from .server import run_wsgi_servers


def initialize_logger(log_input, user_data_path):
    """Set up logging output to file and console.

    :param str log_input: User provided log level.
    :param user_data_path: Path to folder containing any user data,
        such as the config file. Logs will be stored at
        `{user_data_path}/logs/`.
    :return: None

    """
    log_input = log_input.upper()
    logger = logging.getLogger("kodi_api")
    # Set log level for kodi_api
    logging_level = "DEBUG" if log_input == "SQL" else log_input
    logger.setLevel(getattr(logging, logging_level))
    # Set up line formatter to be used by all handlers
    log_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_formatter.default_msec_format = '%s.%03d'
    # Set up console stream handler
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)
    # Set up file handler
    log_file_name = "kodi-api.log"
    try:
        os.mkdir(os.path.join(user_data_path, "logs"))
    except FileExistsError:
        pass
    log_file_path = os.path.join(user_data_path, "logs", log_file_name)
    file_handler = TimedRotatingFileHandler(
        filename=log_file_path,
        when="D",
        interval=1)
    file_handler.setFormatter(log_formatter)
    logger.addHandler(file_handler)
    # Handle if we want to capture SQLAlchemy output as well
    if log_input == "SQL":
        logging.getLogger('sqlalchemy').addHandler(stream_handler)
        logging.getLogger('sqlalchemy').addHandler(file_handler)
        logging.getLogger('sqlalchemy').setLevel(logging.INFO)


def get_app(user_data_path):
    app = flask.Flask(__name__)
    app_config = app.config
    config = configparser.ConfigParser()
    config.read(os.path.join(user_data_path, "config.ini"))
    for section in config.sections():
        app_config[section] = {}
        for item in config.items(section):
            try:
                app_config[section][item[0]] = ast.literal_eval(item[1])
            except ValueError:
                app_config[section][item[0]] = None
    # Set up database(s)
    if "global" in app_config:
        set_db_engine("video", app_config["global"]["video_db_connect_string"])
        set_db_engine("music", app_config["global"]["music_db_connect_string"])
    else:
        raise ValueError(
            "Must specify a [global] section in your config.")
    # Set up ports and hostname info
    if "api_server" not in app_config:
        app_config["api_server"] = {}
    if "http_port" not in app_config["api_server"]:
        app_config["api_server"]["http_port"] = 5000
    if "https_port" not in app_config["api_server"]:
        app_config["api_server"]["https_port"] = None
    if "https_forced" not in app_config["api_server"]:
        app_config["api_server"]["https_forced"] = False
    if not "root" not in app_config["api_server"]:
        app_config["api_server"]["root"] = ""
    print("Kodi Assistant is now running.")
    http_url = None
    https_url = None
    hostname = app_config["api_server"].get("hostname") or "localhost"
    root = ""
    if app_config["api_server"]["root"]:
        root = app_config["api_server"]["root"]
        if root.startswith("/"):
            root = root[1:]
        if root.endswith("/"):
            root = root[:-1]
    if isinstance(app_config["api_server"].get("https_port"), int):
        port = app_config["api_server"].get("https_port")
        protocol = "https"
        if root:
            https_url = f"{protocol}://{hostname}:{port}/{root}/api"
        else:
            https_url = f"{protocol}://{hostname}:{port}/api"
    else:
        if isinstance(app_config["api_server"].get("https_port"), int):
            port = app_config["api_server"].get("http_port")
        else:
            port = 5000
        protocol = "http"
        if root:
            http_url = f"{protocol}://{hostname}:{port}/{root}/api"
        else:
            http_url = f"{protocol}://{hostname}:{port}/api"
    if http_url and https_url:
        print(f"API up and running at {http_url} and {https_url}")
    elif http_url:
        print(f"API up and running at {http_url}.")
    elif https_url:
        print(f"API up and running at {https_url}.")
    # set global config
    if "global" not in app_config:
        app_config["global"] = {}
    app_config["global"]["user_data_path"] = user_data_path
    app.register_blueprint(video_api_blueprint, url_prefix="/api/video")
    app.register_blueprint(media_center_api_blueprint, url_prefix="/api/mediaCenter")
    app.register_blueprint(slots_blueprint, url_prefix="/slots")
    return app


@click.command()
@click.option('--log',
              type=click.Choice(["fatal", "critical", "error", "warning",
                                 "info", "debug", "sql"]),
              default="info",
              help="Logging level to use.")
def run(log):
    """Initializes logging, launches an instance of our Kodi API.

    :param log:
    :return:

    """
    # TODO - figure out the right way to do this across OS...
    user_data_path = os.getcwd()
    initialize_logger(log, user_data_path)
    app = get_app(user_data_path)
    # app.run(host="192.168.1.99", debug=True)
    run_wsgi_servers(app=app, user_data_path=user_data_path)
