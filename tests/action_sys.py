#!/usr/bin/python3
# -*- coding: UTF-8 -*-
from enum import IntEnum, auto

# import mp3play


class SysTyp(IntEnum):
    WIN = auto()
    LIN = auto()
    MAC = auto()
    UNKOWN = auto()


class ActTyp(IntEnum):
    SPEECH_TEXT = auto()
    PLAY_MP3 = auto()
    DRIPPING_WATER = auto()
    LOCK_SCREEN = auto()
    SHUTDOWN = auto()
    NOACTION = auto()
