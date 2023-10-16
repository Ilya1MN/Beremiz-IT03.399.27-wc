#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def getFreeMemory(UsedMemoryIn, MaxMemoryIn, AssignBytesIn):
    Start   = -1
    End     = -1
    Pos     = 0
    UsedMem = -1
    Sz      = 0
    if UsedMemoryIn is not None:
        Sz = len(UsedMemoryIn)
    i = 0
    j = 0
    for i in range(0, MaxMemoryIn):
        if Pos < Sz:
            UsedMem = UsedMemoryIn[Pos]
        if (i != UsedMem and Pos < Sz) or (Pos >= Sz):
            # unused
            j = j+1
            if j == AssignBytesIn:
                Start = (i - j + 1)
                End = i
                break
        else:
            # used
            Pos = Pos+1
            j = 0
    return Start, End, Pos

def assignMemory():
    UsedMemory  = [0, 1, 2, 3, 4, 5, 7, 9, 14, 15, 18, 19, 20, 30]
    AssignBytes = [1, 2, 4, 8]
    for i in range(0, len(AssignBytes)):
        Start, End, Pos = getFreeMemory(UsedMemory, 100, AssignBytes[i])
        print((str(Start) + "..." + str(End) + " pos=" + str(Pos)))
        if Start > -1 and End > -1:
            for a in range(0, AssignBytes[i]):
                UsedMemory.insert((Pos+a), (Start+a))
                print(UsedMemory)


assignMemory()
