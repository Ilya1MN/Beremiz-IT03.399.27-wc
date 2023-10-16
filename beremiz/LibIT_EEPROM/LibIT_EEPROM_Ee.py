#!/usr/bin/env python
# -*- coding: utf-8 -*-

# LibIT_EEPROM / API
#
# This file is part of Beremiz, a Integrated Development Environment for
# programming IEC 61131-3 automates supporting plcopen standard and CanFestival.
#
# Copyright (C) 2020, lamsystems-it.ru
#
# See COPYING file for copyrights details.
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
from lxml import etree
from plcopen import PLCOpenParser
from .LibIT_EEPROM_Deb import LibIT_EEPROM_Debug, LibIT_EEPROM_DebugPrint

#
# EEPROM
#

# Size of EEPROM memory
LibIT_EEPROM_EeSize    = 128000

# The number of bytes of EEPROM register
LibIT_EEPROM_EeTyBytes = {"EeRegByte":1, "EeRegWord":2, "EeRegDWord":4, "EeRegLWord":8, "EeRegReal":4, "EeRegLReal":8}

# The ID of EEPROM register
LibIT_EEPROM_EeTyIDs   = {"EeRegByte":1, "EeRegWord":2, "EeRegDWord":3, "EeRegLWord":4, "EeRegReal":5, "EeRegLReal":6}

# Map of assigned EEPROM memory saved in project
# ["VariableName"] = {"Addr": number, "AddrEnd": number, "Bytes": number}
LibIT_EEPROM_EeMap     = {}

# The number of EEPROM registers
LibIT_EEPROM_EeMapSz   = 65535


# Get number of bytes for data type.
#   In: DataTypeIn - data type name.
#  Out: Number of bytes.
def LibIT_EEPROM_Ee_GetBytes(DataTypeIn):
    Res = 0
    global LibIT_EEPROM_EeTyBytes
    if DataTypeIn in LibIT_EEPROM_EeTyBytes:
        Res = LibIT_EEPROM_EeTyBytes[DataTypeIn]
    return Res


# Get ID for data type.
#   In: DataTypeIn - data type name.
#  Out: ID if data type.
def LibIT_EEPROM_Ee_GetTyID(DataTypeIn):
    Res = 0
    global LibIT_EEPROM_EeTyIDs
    if DataTypeIn in LibIT_EEPROM_EeTyIDs:
        Res = LibIT_EEPROM_EeTyIDs[DataTypeIn]
    return Res


# Calculate number of End-address.
#   In: AddrStartIn - number of Start-address,
#       BytesIn     - number of bytes for data type.
#  Out: Number if End-address.
def LibIT_EEPROM_Ee_CalcAddrEnd(AddrStartIn, BytesIn):
    Res = -1
    if (AddrStartIn > -1) and (BytesIn > 0):
        Res = (AddrStartIn + BytesIn - 1)
    return Res


# Test of EeMap item.
#   In: MapItemIn - item of EeMap.
#  Out: True if is the item, otherwise - False.
def LibIT_EEPROM_Ee_IsMapItem(MapItemIn):
    global LibIT_EEPROM_EeTyBytes
    if MapItemIn["Addr"] >= 0 and MapItemIn["AddrEnd"] >= 0 and (MapItemIn["Bytes"] > 0):
        return True
    else:
        return False


# Get list of assigned memory from EeMap.
#   In: MapIn - EeMap.
#  Out: List of assigned memory sorted by value.
def LibIT_EEPROM_Ee_GetMemList(MapIn):
    Res = []
    for key in MapIn:
        if LibIT_EEPROM_Ee_IsMapItem(MapIn[key]):
            for i in range(MapIn[key]["Addr"], MapIn[key]["AddrEnd"]+1):
                Res.append(i)
    Res.sort()
    return Res


# Search free memory in list of assigned memory.
#   In:   MemListIn - list of assigned memory,
#       BytesIn     - number of bytes for data type.
#  Out: AddrStart, AddrEnd, MemListPos.
def LibIT_EEPROM_Ee_SearchFreeMem(MemListIn, BytesIn):
    global LibIT_EEPROM_EeSize
    AddrStart  = -1
    AddrEnd    = -1
    MemListPos = 0
    MemListSz  = 0
    Mem        = -1
    if MemListIn is not None:
        MemListSz = len(MemListIn)
    i = 0
    j = 0
    for i in range(0, LibIT_EEPROM_EeSize):
        if MemListPos < MemListSz:
            Mem = MemListIn[MemListPos]
        if (i != Mem and MemListPos < MemListSz) or (MemListPos >= MemListSz):
            # free
            j = j+1
            if j == BytesIn:
                AddrStart = (i - j + 1)
                AddrEnd   = i
                break
        else:
            # not free
            MemListPos = MemListPos+1
            j = 0
    return AddrStart, AddrEnd, MemListPos


# Search variable nodes in XML project-tree.
#   In: ProjectTreeIn - tree of project.
#  Out: List of variable nodes (<variable name="Name">...</variable>).
# Note: Search in project/instances/configurations/configuration/globalVars
#                 project/instances/configurations/configuration/resource/globalVars
#                 project/types/pous/pou[@pouType='program']/interface/localVars
def LibIT_EEPROM_Ee_SearchVarNodes(ProjectTreeIn):
    Res = []
    Targets = None
    if ProjectTreeIn is not None:
        Targets = ProjectTreeIn.xpath("/ppx:project/ppx:instances/ppx:configurations/ppx:configuration/ppx:globalVars|/ppx:project/ppx:instances/ppx:configurations/ppx:configuration/ppx:resource/ppx:globalVars|/ppx:project/ppx:types/ppx:pous/ppx:pou[@pouType='program']/ppx:interface/ppx:localVars", namespaces=PLCOpenParser.NSMAP)
    if Targets is not None:
        for Target in Targets:
            Vars = Target.xpath(".//ppx:derived[@name='EeRegByte']|.//ppx:derived[@name='EeRegWord']|.//ppx:derived[@name='EeRegDWord']|.//ppx:derived[@name='EeRegLWord']|.//ppx:derived[@name='EeRegReal']|.//ppx:derived[@name='EeRegLReal']", namespaces=PLCOpenParser.NSMAP)
            if Vars is not None:
                for Var in Vars:
                    Var  = Var.getparent() #type
                    Var  = Var.getparent() #variable
                    Res.append(Var)
    return Res


# Read map of assigned EEPROM memory from XML project-tree.
#   In: ProjectTreeIn - tree of project,
#       ExtModeIn - True if add to map item a pointer to node item, otherwise - False.
#  Out: Map.
def LibIT_EEPROM_Ee_ReadMap(ProjectTreeIn, ExtModeIn):
    global LibIT_EEPROM_EeMapSz
    LibIT_EEPROM_DebugPrint("ReadMap")
    Res  = {}
    Vars = LibIT_EEPROM_Ee_SearchVarNodes(ProjectTreeIn)
    if Vars is not None:
        for Var in Vars:
            Name = None
            Map  = {"Addr":-1, "AddrEnd":-1, "Bytes":0, "Ty":0, "Name":None, "Node":None}
            #<variable name="Name">
            if "name" in Var.attrib:
                if Var.attrib["name"] is not None:
                    Name = Var.attrib["name"]
                    Map["Name"] = Name
            #<derived name="Type"/>
            Tmp = Var.xpath(".//ppx:derived", namespaces=PLCOpenParser.NSMAP)
            if Tmp is not None:
                if len(Tmp) > 0:
                    if "name" in Tmp[0].attrib:
                        Map["Bytes"] = LibIT_EEPROM_Ee_GetBytes(Tmp[0].attrib["name"])
                        Map["Ty"]    = LibIT_EEPROM_Ee_GetTyID(Tmp[0].attrib["name"])
            #<simpleValue value="Addr"/>
            Tmp = Var.xpath(".//ppx:initialValue/ppx:structValue/ppx:value[@member='Addr']/ppx:simpleValue", namespaces=PLCOpenParser.NSMAP)
            if Tmp is not None:
                if len(Tmp) > 0:
                    if "value" in Tmp[0].attrib:
                        if Tmp[0].attrib["value"].isdigit():
                            Map["Addr"] = int(Tmp[0].attrib["value"])
            if (Name is not None) and (Map["Bytes"] > 0):
                Map["AddrEnd"] = LibIT_EEPROM_Ee_CalcAddrEnd(Map["Addr"], Map["Bytes"])
                if ExtModeIn == True:
                    Map["Node"] = Var
                Res[Name] = Map
                LibIT_EEPROM_DebugPrint(Map)
                if len(Res) == LibIT_EEPROM_EeMapSz:
                    break;
    LibIT_EEPROM_DebugPrint(len(Res))
    LibIT_EEPROM_DebugPrint("ReadMap End")
    return Res


# Set address value into variable node.
#   In: VarNodeIn - variable node,
#       AddrIn    - address value.
#  Out: None.
def LibIT_EEPROM_Ee_SetVarNode(VarNodeIn, AddrIn):
    if (VarNodeIn is not None) and (AddrIn > -1):
        # test <simpleValue value="Addr"/>
        Buff = str(AddrIn)
        Node = None
        Path = ".//ppx:initialValue/ppx:structValue/ppx:value[@member='Addr']/ppx:simpleValue"
        Tmp  = VarNodeIn.xpath(Path, namespaces=PLCOpenParser.NSMAP)
        # set address value into Node
        if Tmp is not None:
            if len(Tmp) > 0:
                Node = Tmp[0]
                Node.attrib["value"] = Buff
        if Node is None:
            LibIT_EEPROM_DebugPrint("+ add simpleValue = " + str(AddrIn))
            VarNodeIn.insert(1, etree.XML('<initialValue><structValue><value member="Addr"><simpleValue value="' + str(AddrIn) + '"/></value></structValue></initialValue>'))


# Save EeMap into file (LOCATED_VARIABLES_EEREG.h).
#   In: MapIn - map,
#       PathIn - path to directory "build".
#  Out: None.
def LibIT_EEPROM_Ee_SaveToFile(MapIn, PathIn):
    if MapIn is not None and PathIn is not None:
        if os.path.exists(PathIn):
            Data = ""
            for key in MapIn:
                if LibIT_EEPROM_Ee_IsMapItem(MapIn[key]):
                    Data = Data + "__LOCATED_VAR(" + str(MapIn[key]["Addr"]) + "," + str(MapIn[key]["Ty"]) + ")\n"
            f = open(os.path.join(PathIn, "LOCATED_VARIABLES_EEREG.h"), "w")
            f.write(Data)
            f.close()


# Assign addresses by EeMap.
#   In: ProjectTreeIn - tree of project,
#       OldMapIn - old map or None,
#       PathIn - path to directory "build" or None.
#  Out: None.
def LibIT_EEPROM_Ee_AssignMem(ProjectTreeIn, OldMapIn, PathIn):
    LibIT_EEPROM_DebugPrint("AssignMem")
    LibIT_EEPROM_DebugPrint("NewMap =")
    NewMap  = LibIT_EEPROM_Ee_ReadMap(ProjectTreeIn, True)
    MemList = LibIT_EEPROM_Ee_GetMemList(OldMapIn)
    LibIT_EEPROM_DebugPrint("MemList =")
    LibIT_EEPROM_DebugPrint(MemList)
    for Name in NewMap:
        # to assign by default
        NewMap[Name]["Addr"] = -1
        # test Name for OldMap (by Name, Bytes)
        if OldMapIn is not None:
            if Name in OldMapIn:
                if NewMap[Name]["Bytes"] == OldMapIn[Name]["Bytes"]:
                    # save old address value (no assign)
                    NewMap[Name]["Addr"] = OldMapIn[Name]["Addr"]
        # assign memory
        if NewMap[Name]["Addr"] < 0:
            NewMap[Name]["Addr"], NewMap[Name]["AddrEnd"], MemListPos = LibIT_EEPROM_Ee_SearchFreeMem(MemList, NewMap[Name]["Bytes"])
            LibIT_EEPROM_DebugPrint("assigned memory: " + str(NewMap[Name]["Addr"]) + "..." + str(NewMap[Name]["AddrEnd"]) + " pos=" + str(MemListPos))
            if (NewMap[Name]["Addr"] > -1) and (NewMap[Name]["AddrEnd"] > -1) and (NewMap[Name]["Node"] is not None):
                # update list of assigned memory
                for i in range(0, NewMap[Name]["Bytes"]):
                    MemList.insert((MemListPos+i), (NewMap[Name]["Addr"]+i))
                    LibIT_EEPROM_DebugPrint(MemList)
        # set address value into node
        LibIT_EEPROM_Ee_SetVarNode(NewMap[Name]["Node"], NewMap[Name]["Addr"])
    #save into file (if PathIn is not None)
    LibIT_EEPROM_Ee_SaveToFile(NewMap, PathIn)
    LibIT_EEPROM_DebugPrint("AssignMem End")
