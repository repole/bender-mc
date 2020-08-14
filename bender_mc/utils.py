"""
    bender_mc.utils
    ~~~~~~~~~~~~~~~

    Utility tools for bender-mc.
"""
# :copyright: (c) 2020 by Nicholas Repole.
# :license: MIT - See LICENSE for more details.

def deformat_title(formatted_title):
    return formatted_title.replace(
        "__COLON__", ":").replace(
        "__DOT__", ".").replace(
        "__DASH__", "-").replace(
        "__SPACE__", " ").replace(
        "__APOSTROPHE__", "'").replace(
        "__UNDERSCORE__", "_")
