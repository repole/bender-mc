"""
    bender_mc.server
    ~~~~~~~~~~~~~~~~

    Built in, production ready webserver for easy access.
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
import configparser
from cheroot import wsgi
from cheroot.ssl.builtin import BuiltinSSLAdapter
import os
import logging
import threading
import sys
import subprocess

logger = logging.getLogger(__name__)

_http_server = None
_https_server = None
_snapclient = None


def run(app, root_prefix="", hostname="0.0.0.0", http_port=None,
        https_port=None, https_cert_path=None, https_certkey_path=None):
    root_prefix = root_prefix or ""
    dispatcher = wsgi.PathInfoDispatcher({root_prefix: app})
    global _http_server
    global _https_server
    http_thread = None
    https_thread = None
    if http_port:
        _http_server = wsgi.Server(
            (hostname, http_port), dispatcher)
        http_thread = threading.Thread(target=_http_server.start)
    if https_port:
        _https_server = wsgi.Server(
            (hostname, https_port), dispatcher)
        _https_server.ssl_adapter = BuiltinSSLAdapter(
            https_cert_path, https_certkey_path)
        https_thread = threading.Thread(target=_https_server.start)
    if http_thread is not None:
        http_thread.start()
    if https_thread is not None:
        https_thread.start()
    snapclient_cmd = (
        "C:\\Users\\repole\\Projects\\snapcast\\bin\\Release\\snapclient.exe "
        "-h 192.168.1.98 "
        "-p 1704").split(" ")
    subprocess.Popen(snapclient_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def run_wsgi_servers(app, user_data_path):
    config_file = os.path.join(user_data_path, 'config.ini')
    config_parser = configparser.RawConfigParser()
    config_parser.read(config_file)
    try:
        http_port = config_parser.getint('api_server', 'http_port')
    except (ValueError, TypeError):
        http_port = None
    try:
        https_port = config_parser.getint('api_server', 'https_port')
    except (ValueError, TypeError):
        https_port = None
    hostname = config_parser.get('api_server', 'hostname').strip("'").strip('"')
    hostname = None if hostname == "None" else hostname
    root_prefix = config_parser.get('api_server', 'root').strip('"').strip("'")
    root_prefix = None if root_prefix == "None" else root_prefix
    https_cert_path = os.path.join(user_data_path, 'keys', 'server.crt')
    https_certkey_path = os.path.join(user_data_path, 'keys', 'server.crtkey')
    run(app, root_prefix, hostname, http_port, https_port, https_cert_path,
        https_certkey_path)


def stop_wsgi_servers():
    global _http_server
    global _https_server
    if _http_server is not None:
        _http_server.stop()
    if _https_server is not None:
        _https_server.stop()


def restart_wsgi_servers():
    logger.debug("Entering restart_wsgi_servers()")
    args = sys.argv
    args[0] = '"' + args[0] + '"'
    os.execl(sys.executable, sys.executable, * args)
