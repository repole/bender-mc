"""
    bender_mc.kodi.rpc_client
    ~~~~~~~~~~~~~~~~~~~~~~~~~

    Simplified RPC client for Kodi to suit my requirements.
"""
# :copyright: (c) 2020 by Nicholas Repole and contributors.
#             See AUTHORS for more details.
# :license: MIT - See LICENSE for more details.
import time
from drowsy.log import Loggable
import requests


class KodiRpcClient(Loggable):

    def __init__(self, base_url, username, password):
        """

        :param str base_url:
        :param username:
        :param password:

        """
        self.username = username
        self.password = password
        self.base_url = base_url
        self.req_counter = 140
        self.req_session = requests.Session()
        if not self.base_url.endswith("/"):
            self.base_url += "/"

    def post_rpc(self, method, params):
        data = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": self.req_counter
        }
        url = self.base_url + f"jsonrpc?{method}"
        result = self.req_session.post(
            url,
            auth=(self.username, self.password),
            headers={"Connection": "keep-alive"},
            json=[data])
        self.req_counter += 1
        return result

    def get_monitor(self):
        return self.post_rpc(
            method="Settings.GetSettingValue",
            params={"setting": "videoscreen.monitor"}
        ).json()[0]["result"]["value"]

    def set_monitor(self, value):
        current = self.get_monitor()
        if current != value:
            self.post_rpc(
                method="Settings.SetSettingValue",
                params={"setting": "videoscreen.monitor", "value": value}
            )

    def get_fullscreen(self):
        response = self.post_rpc(
            method="Settings.GetSettingValue",
            params={"setting": "videoscreen.screen"}
        ).json()
        return response[0]["result"]["value"]

    def set_fullscreen(self):
        current = self.get_fullscreen()
        if current != 0:
            return self.post_rpc(
                method="Settings.SetSettingValue",
                params={"setting": "videoscreen.screen", "value": 0}
            )

    def execute_action(self, action):
        result = self.post_rpc(
            method="Input.ExecuteAction",
            params={"action": action}
        )
        return result

    def play_pause_toggle(self):
        result = self.post_rpc(
            method="Player.PlayPause",
            params={"playerid": 1, "play": "toggle"}
        )
        return result

    def play_next(self):
        result = self.post_rpc(
            method="Player.GoTo",
            params={"playerid": 1, "to": "next"}
        )
        return result

    def play_video(self, media_id, media_type, resume_time=None):
        media_ids = []
        if isinstance(media_id, list):
            media_ids = media_id
            media_id = media_ids[0]
            media_ids.pop(0)
        # TODO - Get playlist id? Assuming 1..
        playlist_id = 1
        clear_playlist = self.post_rpc(
            method="Playlist.Clear",
            params=[playlist_id]
        )
        if media_type == "movie":
            media_id_key = "movieid"
        else:
            media_id_key = "episodeid"
        playlist_insert = self.post_rpc(
            method="Playlist.Insert",
            params=[playlist_id, 0, {media_id_key: media_id}]
        )
        player_open = self.post_rpc(
            method="Player.Open",
            params={
                "item": {
                    "position": 0,
                    "playlistid": playlist_id
                },
                "options": {
                    "resume": {"hours": 1, "minutes": 0, "seconds": 8}
                }
            }
        )
        gui_set_fullscreen = self.post_rpc(
            method="GUI.SetFullscreen",
            params=[True]
        )
        if resume_time:
            time.sleep(.5)
            player_seek = self.post_rpc(
                method="Player.Seek",
                params={
                    "playerid": 1,
                    "value":  {"seconds": int(resume_time)}
                }
            )
        for i, next_id in media_ids:
            queue_insert = self.post_rpc(
                method="Playlist.Insert",
                params=[playlist_id, (i + 1), {media_id_key: next_id}]
            )
        return

    def play_mlb(self, list_index, is_home, game_status):
        open_mlb = self.post_rpc(
            method="Addons.ExecuteAddon",
            params=["plugin.video.mlbtv"]
        )
        time.sleep(1)
        self.execute_action("pageup")
        time.sleep(.1)
        self.post_rpc(
            method="Input.down",
            params=[]
        )
        time.sleep(.1)
        select_today = self.post_rpc(
            method="Input.Select",
            params=[]
        )
        time.sleep(3)
        self.execute_action("pageup")
        for i in range(0, list_index+3):
            self.post_rpc(
                method="Input.Down",
                params=[]
            )
            time.sleep(.1)
        select_game = self.post_rpc(
            method="Input.Select",
            params=[]
        )
        time.sleep(3)
        for i in range(0, 1 + 1 if not is_home else 0):
            self.post_rpc(
                method="Input.Down",
                params=[]
            )
            time.sleep(.1)
        select_feed = self.post_rpc(
            method="Input.Select",
            params=[]
        )
        time.sleep(3)
        # select the live feed
        if game_status != "Final":
            for i in range(0, 2):
                self.post_rpc(
                    method="Input.Down",
                    params=[]
                )
                time.sleep(.1)
            select_start = self.post_rpc(
                method="Input.Select",
                params=[]
            )
        return
