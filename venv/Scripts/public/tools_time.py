#!/usr/bin/env python
# -*- coding: utf-8 -*-

def getHourMiniSecDes(fTime):
    iHour = int(fTime / 60 / 60)
    iMin = int(fTime % 3600 / 60)
    iSec = int(fTime % 60)
    return "{hour}时{min}分{sec}秒".format(hour=iHour, min = iMin, sec = iSec)