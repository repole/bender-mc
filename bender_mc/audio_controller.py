"""
    bender_mc.audio_controller
    ~~~~~~~~~~~~~~~~~~~~~~~~~~

    Crudely controls the audio on a media center.
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# Crude mapping of 0-100 to volume level possible values
mapping = {
    0: -64.0,
    1: -56.26088715,
    2: -51.15739059,
    3: -47.34343719,
    4: -44.29706573,
    5: -41.76048279,
    6: -39.58728027,
    7: -37.68627167,
    8: -35.99679947,
    9: -34.47646713,
    10: -33.09446335,
    11: -31.82770729,
    12: -30.65844727,
    13: -29.57274055,
    14: -28.55943871,
    15: -27.60948563,
    16: -26.7154274,
    17: -25.87104416,
    18: -25.07110977,
    19: -24.31117821,
    20: -23.58743477,
    21: -22.89659309,
    22: -22.23578835,
    23: -21.60251617,
    24: -20.99457741,
    25: -20.41002083,
    26: -19.84711456,
    27: -19.30431175,
    28: -18.78022575,
    29: -18.27360916,
    30: -17.78333282,
    31: -17.30838013,
    32: -16.84781837,
    33: -16.4008007,
    34: -15.9665556,
    35: -15.5443716,
    36: -15.13359737,
    37: -14.73363304,
    38: -14.34392452,
    39: -13.96395779,
    40: -13.593256,
    41: -13.23138237,
    42: -12.87792301,
    43: -12.5324955,
    44: -12.19474506,
    45: -11.86433601,
    46: -11.5409565,
    47: -11.22431374,
    48: -10.91413307,
    49: -10.61015511,
    50: -10.3121376,
    51: -10.01985073,
    52: -9.733078003,
    53: -9.451616287,
    54: -9.175270081,
    55: -8.903860092,
    56: -8.637210846,
    57: -8.375159264,
    58: -8.117547989,
    59: -7.86423111,
    60: -7.615064621,
    61: -7.369918346,
    62: -7.128663063,
    63: -6.891177177,
    64: -6.657344818,
    65: -6.427054882,
    66: -6.200201035,
    67: -5.976684093,
    68: -5.756406307,
    69: -5.539275169,
    70: -5.325201988,
    71: -5.114102364,
    72: -4.905892372,
    73: -4.700497627,
    74: -4.497841358,
    75: -4.297851086,
    76: -4.100458145,
    77: -3.905595779,
    78: -3.713200092,
    79: -3.523207664,
    80: -3.335562229,
    81: -3.150204659,
    82: -2.967080355,
    83: -2.78613615,
    84: -2.607320309,
    85: -2.430582762,
    86: -2.255877495,
    87: -2.083157539,
    88: -1.912378073,
    89: -1.74349618,
    90: -1.576469898,
    91: -1.411258101,
    92: -1.247823596,
    93: -1.086127758,
    94: -0.9261339307,
    95: -0.76780653,
    96: -0.6111113429,
    97: -0.4560140669,
    98: -0.3024843037,
    99: -0.1504897326,
    100: 0
}


class AudioController(object):
    def __init__(self):
        self._volume_interface = None

    def _initialize_interface(self):
        # Delayed until here due to weird threading/multiprocessing
        if not self._volume_interface:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(
                IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            self._volume_interface = cast(interface, POINTER(IAudioEndpointVolume))

    def mute(self):
        self._initialize_interface()
        self._volume_interface.SetMute(1, None)

    def unmute(self):
        self._initialize_interface()
        self._volume_interface.SetMute(0, None)

    def adjust_volume(self, amount):
        self._initialize_interface()
        self.volume = self.volume + amount

    def set_volume(self, value):
        self._initialize_interface()
        if value > 100:
            value = 100
        elif value < 0:
            value = 0
        value = int(value)
        translation = mapping[value]
        self._volume_interface.SetMasterVolumeLevel(translation, None)

    @property
    def volume(self):
        self._initialize_interface()
        master_volume = self._volume_interface.GetMasterVolumeLevel()
        distance = 65
        guess = 0
        for key in mapping:
            new_distance = abs(master_volume - mapping[key])
            if new_distance < distance:
                distance = new_distance
                guess = key
            else:
                break
        return guess

    @volume.setter
    def volume(self, value):
        self.set_volume(value)
