import os
import subprocess
import tempfile
from contextlib import suppress
from flask import request, Blueprint
from bender_mc import playsound
from bender_mc.api.utils import (
    audio_controller, close_db_sessions, get_rpc_client, load_db_sessions,
    load_rpc_client)


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
def media_center_speakers_volume_set():
    data = request.json
    value = data["volumeLevel"]
    amount = data.get("amount")
    with suppress(ValueError):
        value = int(value)
    with suppress(ValueError, TypeError):
        amount = int(amount)
    if str(value).lower() == "mute":
        audio_controller.mute()
    elif str(value).lower() == "unmute":
        audio_controller.unmute()
    elif str(value).lower() == "dim":
        audio_controller.dim()
    elif str(value).lower() == "undim":
        audio_controller.undim()
    else:
        if str(amount).lower() == "a lot":
            amount = 20
        else:
            amount = 10
        if audio_controller.volume is not None:
            if str(value).lower() == "decrease":
                audio_controller.volume = audio_controller.volume - amount
            elif str(value).lower() == "increase":
                audio_controller.volume = audio_controller.volume + amount
            elif isinstance(value, int):
                audio_controller.volume = value
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
    script = os.path.join(os.path.dirname(__file__), "..", "scripts", "display_switch.ps1")
    p = subprocess.Popen(
        ["powershell.exe", script, arg], stdout=subprocess.PIPE)
    p.wait()
    if arg == "external":
        audio_controller.switch_device("HDMI")
    else:
        audio_controller.switch_device("Speakers")
    return {"result": "success"}
