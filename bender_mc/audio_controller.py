"""
    bender_mc.audio_controller
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Crudely controls the audio on a media center.

    Depends on SoundVolumeView.exe being in your path.

"""
# :copyright: (c) 2022 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
import json
import os
import shutil
import subprocess
import tempfile


class AudioController(object):

    def __init__(self):
        self._volume = None
        self._pre_dim_volume = None
        self.device = "Speakers"
        # determine the currently active device
        with tempfile.TemporaryDirectory() as tmpdirname:
            audio_json = os.path.join(tmpdirname, "audio.json")
            exe_path = shutil.which("SoundVolumeView.exe")
            p = subprocess.Popen(
                [exe_path, "/sjson", audio_json], stdout=subprocess.PIPE)
            p.wait()
            with open(audio_json, "rb") as f:
                data = json.load(f)
            for row in data:
                if row["Default"] == "Render":
                    self.device = row["Name"]

    def switch_device(self, device):
        self.device = device
        p = subprocess.Popen(
            ["SoundVolumeView.exe", "/SetDefault", device],
            stdout=subprocess.PIPE)
        p.wait()

    def dim(self):
        self._pre_dim_volume = self.volume
        self.volume = 10

    def undim(self):
        self.volume = self._pre_dim_volume

    def mute(self):
        p = subprocess.Popen(
            ["SoundVolumeView.exe", "/Mute", self.device],
            stdout=subprocess.PIPE)
        p.wait()

    def unmute(self):
        p = subprocess.Popen(
            ["SoundVolumeView.exe", "/Unmute", self.device],
            stdout=subprocess.PIPE)
        p.wait()

    @property
    def volume(self):
        if self._volume is not None:
            self._volume = .1 * int(
                subprocess.check_output(
                    ["getvolume.bat", self.device],  # TODO - script loc
                    shell=True
                ).decode().split("\r\n")[-2]
            )
        return self._volume

    @volume.setter
    def volume(self, value):
        p = subprocess.Popen(
            ["SoundVolumeView.exe", "/SetVolume", self.device, value],
            stdout=subprocess.PIPE)
        p.wait()
        self._volume = value
