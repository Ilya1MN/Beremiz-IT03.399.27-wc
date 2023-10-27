#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Beremiz, a Integrated Development Environment for
# programming IEC 61131-3 automates supporting plcopen standard and CanFestival.
#
# Copyright (C) 2007: Edouard TISSERANT and Laurent BESSARD
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
import re
#from types import TupleType, StringType, UnicodeType

import wx
import wx.grid
import wx.lib.buttons

from plcopen.structures import LOCATIONDATATYPES, TestIdentifier, IEC_KEYWORDS, DefaultType
from graphics.GraphicCommons import REFRESH_HIGHLIGHT_PERIOD, ERROR_HIGHLIGHT
from dialogs.ArrayTypeDialog import ArrayTypeDialog
from .CustomGrid import CustomGrid
from .CustomTable import CustomTable
from .LocationCellEditor import LocationCellEditor
from util.BitmapLibrary import GetBitmap
from plcopen.VariableInfoCollector import _VariableInfos
from util.TranslationCatalogs import NoTranslate
from threading import Thread

# -------------------------------------------------------------------------------
#                                 Helpers
# -------------------------------------------------------------------------------


[
    TITLE, EDITORTOOLBAR, FILEMENU, EDITMENU, DISPLAYMENU, PROJECTTREE,
    POUINSTANCEVARIABLESPANEL, LIBRARYTREE, SCALING, PAGETITLES, VARIABLETREE
] = list(range(11))

[
    VARIABLEPANEL_LOCAL, VARIABLEPANEL_GLOBAL, VARIABLEPANEL_FB
] = list(range(3))

def GetVariableTableColnames(location, group):
    _ = NoTranslate
    cols = ["#",
            _("Name"),
            _("Group"),
            _("Class"),
            _("Type"),
            _("Location"),
            _("Initial Value"),
            _("Option"),
            _("Documentation")]
    if not group and not location:
        del cols[2]  # remove 'Group' column
        del cols[4]  # remove 'Location' column
    elif not group:
        del cols[2]  # remove 'Group' column
    elif not location:
        del cols[5]  # remove 'Location' column
    return cols


def GetGlobalVariableTableColnames(location):
    _ = NoTranslate
    cols = ["#",
            _("Group"),
            _("Name"),
            _("Class"),
            _("Type"),
            _("Location"),
            _("Initial Value"),
            _("Option"),
            _("Documentation")]
    if not location:
        del cols[5]  # remove 'Location' column
    return cols

def GetOptions(constant=True, retain=True, non_retain=True):
    _ = NoTranslate
    options = [""]
    if constant:
        options.append(_("Constant"))
    if retain:
        options.append(_("Retain"))
    if non_retain:
        options.append(_("Non-Retain"))
    return options

GLOBAL_VAR_NAME_DEFAULT = "    "

OPTIONS_DICT = dict([(_(option), option) for option in GetOptions()])

def GetFilterChoiceTransfer():
    _ = NoTranslate
    return {_("All"): _("All"), _("Interface"): _("Interface"),
            _("   Input"): _("Input"), _("   Output"): _("Output"), _("   InOut"): _("InOut"),
            _("   External"): _("External"), _("Variables"): _("Variables"), _("   Local"): _("Local"),
            _("   Temp"): _("Temp"), _("Global"): _("Global")}  # , _("Access") : _("Access")}


VARIABLE_CHOICES_DICT = dict([(_(_class), _class) for _class in GetFilterChoiceTransfer().keys()])
VARIABLE_CLASSES_DICT = dict([(_(_class), _class) for _class in GetFilterChoiceTransfer().values()])

CheckOptionForClass = {
    "Local": lambda x: x,
    "Temp": lambda x: "",
    "Input": lambda x: {"Retain": "Retain", "Non-Retain": "Non-Retain"}.get(x, ""),
    "InOut": lambda x: "",
    "Output": lambda x: {"Retain": "Retain", "Non-Retain": "Non-Retain"}.get(x, ""),
    "Global": lambda x: {"Constant": "Constant", "Retain": "Retain"}.get(x, ""),
    "External": lambda x: {"Constant": "Constant"}.get(x, "")
}

LOCATION_MODEL = re.compile("((?:%[IQM](?:\*|(?:[XBWLD]?[0-9]+(?:\.[0-9]+)*)))?)$")
VARIABLE_NAME_SUFFIX_MODEL = re.compile("([0-9]*)$")


# -------------------------------------------------------------------------------
#                            Variables Panel Table
# -------------------------------------------------------------------------------
from datetime import datetime
import time

class VariableTable(CustomTable):

    """
    A custom wx.grid.Grid Table using user supplied data
    """
    def __init__(self, parent, data, colnames):
        # The base class must be initialized *first*
        CustomTable.__init__(self, parent, data, colnames)
        self.old_value = None
        self.GroupList = None

    def GetValueByName(self, row, colname):
        if row < self.GetNumberRows():
            return getattr(self.data[row], colname)

    def SetValueByName(self, row, colname, value):
        if row < self.GetNumberRows():
            setattr(self.data[row], colname, value)

    def GetValue(self, row, col):
        if row < self.GetNumberRows():
            if col == 0:
                return self.data[row].Number
            colname = self.GetColLabelValue(col, False)
            if colname == "Initial Value":
                colname = "InitialValue"
            value = getattr(self.data[row], colname, "")
            if colname == "Type" and isinstance(value, tuple):
                if value[0] == "array":
                    return "ARRAY [%s] OF %s" % (",".join(["..".join(x) for x in value[2]]), value[1])
            if not isinstance(value, str):
                value = str(value)
            if colname in ["Class", "Option"]:
                return _(value)
            return value

    def SetValue(self, row, col, value):

        if col < len(self.colnames):
            colname = self.GetColLabelValue(col, False)
            if colname == "Name":
                self.old_value = getattr(self.data[row], colname)
            elif colname == "Class":
                value = VARIABLE_CLASSES_DICT[value]
                self.SetValueByName(row, "Option", CheckOptionForClass[value](self.GetValueByName(row, "Option")))
                if value == "External":
                    self.SetValueByName(row, "InitialValue", "")
            elif colname == "Option":
                value = OPTIONS_DICT[value]
            elif colname == "Initial Value":
                colname = "InitialValue"
            elif colname == "#":
                return
            setattr(self.data[row], colname, value)

    def GetOldValue(self):
        return self.old_value

    def _GetRowEdit(self, row):
        row_edit = self.GetValueByName(row, "Edit")
        var_type = self.Parent.GetTagName()
        bodytype = self.Parent.Controler.GetEditedElementBodyType(var_type)
        if bodytype in ["ST", "IL"]:
            row_edit = True
        return row_edit

    def _updateColAttrs(self, grid, group=''):
        """
        wx.grid.Grid -> update the column attributes to add the
        appropriate renderer given the column name.

        Otherwise default to the default renderer.
        """
        if self.GroupList is not None:
            try:
                self.GroupList.remove((_("All")))
            except:
                pass

        for row in range(self.GetNumberRows()):
            var_class = self.GetValueByName(row, "Class")
            var_type = self.GetValueByName(row, "Type")
            row_highlights = self.Highlights.get(row, {})
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                colname = self.GetColLabelValue(col, False)
                if self.Parent.Debug:
                    grid.SetReadOnly(row, col, True)
                else:
                    if colname == "Option":
                        options = GetOptions(constant=var_class in ["Local", "External", "Global"],
                                             retain=self.Parent.ElementType != "function" and var_class in ["Local", "Input", "Output", "Global"],
                                             non_retain=self.Parent.ElementType != "function" and var_class in ["Local", "Input", "Output"])
                        if len(options) > 1:
                            editor = wx.grid.GridCellChoiceEditor([])
                            editor.SetParameters(",".join(map(_, options)))
                        else:
                            grid.SetReadOnly(row, col, True)
                    elif col != 0 and self._GetRowEdit(row):
                        grid.SetReadOnly(row, col, False)
                        if colname == "Name":
                            editor = wx.grid.GridCellTextEditor()
                            renderer = wx.grid.GridCellStringRenderer()
                        elif colname == "Group":
                            if var_class in ["Global", "Resource"]:
                                if self.GroupList is not None:
                                    editor = wx.grid.GridCellChoiceEditor([])
                                    editor.SetParameters(",".join(self.GroupList))
                                    if self.GetValue(row, col) == '':
                                        self.SetValue(row, col, (_("Default")))
                        elif colname == "Initial Value":
                            if var_class not in ["External", "InOut"]:
                                if self.Parent.Controler.IsEnumeratedType(var_type):
                                    editor = wx.grid.GridCellChoiceEditor([])
                                    editor.SetParameters(",".join([""] + self.Parent.Controler.GetEnumeratedDataValues(var_type)))
                                else:
                                    editor = wx.grid.GridCellTextEditor()
                                renderer = wx.grid.GridCellStringRenderer()
                            else:
                                grid.SetReadOnly(row, col, True)
                        elif colname == "Location":
                            if var_class in ["Local", "Global"] and self.Parent.Controler.IsLocatableType(var_type):
                                editor = LocationCellEditor(self, self.Parent.Controler)
                                renderer = wx.grid.GridCellStringRenderer()
                            else:
                                grid.SetReadOnly(row, col, True)
                        elif colname == "Class":
                            if len(self.Parent.ClassList) == 1:
                                grid.SetReadOnly(row, col, True)
                            else:
                                editor = wx.grid.GridCellChoiceEditor([])
                                excluded = []
                                if self.Parent.IsFunctionBlockType(var_type):
                                    excluded.extend(["Local", "Temp"])
                                editor.SetParameters(",".join([_(choice) for choice in self.Parent.ClassList if choice not in excluded]))
                    elif colname != "Documentation":
                        grid.SetReadOnly(row, col, True)

                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)

                if colname == "Location" and LOCATION_MODEL.match(self.GetValueByName(row, colname)) is None:
                    highlight_colours = ERROR_HIGHLIGHT
                else:
                    highlight_colours = row_highlights.get(colname.lower(), [(wx.WHITE, wx.BLACK)])[-1]
                grid.SetCellBackgroundColour(row, col, highlight_colours[0])
                grid.SetCellTextColour(row, col, highlight_colours[1])
            self.ResizeRow(grid, row)


# -------------------------------------------------------------------------------
#                         Variable Panel Drop Target
# -------------------------------------------------------------------------------


class VariableDropTarget(wx.TextDropTarget):
    '''
    This allows dragging a variable location from somewhere to the Location
    column of a variable row.

    The drag source should be a TextDataObject containing a Python tuple like:
        ('%ID0.0.0', 'location', 'REAL')

    c_ext/CFileEditor.py has an example of this (you can drag a C extension
    variable to the Location column of the variable panel).
    '''
    def __init__(self, parent):
        wx.TextDropTarget.__init__(self)
        self.ParentWindow = parent

    def OnDropText(self, x, y, data):
        self.ParentWindow.ParentWindow.Select()
        x, y = self.ParentWindow.VariablesGrid.CalcUnscrolledPosition(x, y)
        col = self.ParentWindow.VariablesGrid.XToCol(x)
        row = self.ParentWindow.VariablesGrid.YToRow(y)
        message = None
        element_type = self.ParentWindow.ElementType
        try:
            values = eval(data)
        except Exception:
            message = _("Invalid value \"%s\" for variable grid element") % data
            values = None
        if not isinstance(values, tuple):
            message = _("Invalid value \"%s\" for variable grid element") % data
            values = None
        if values is not None:
            if col != wx.NOT_FOUND and row != wx.NOT_FOUND:
                colname = self.ParentWindow.Table.GetColLabelValue(col, False)
                if (colname == "Location") and (values[1] == "location"):
                    if not self.ParentWindow.Table.GetValueByName(row, "Edit"):
                        message = _("Can't give a location to a function block instance")
                    elif self.ParentWindow.Table.GetValueByName(row, "Class") not in ["Local", "Global"]:
                        message = _("Can only give a location to local or global variables")
                    else:
                        location = values[0]
                        variable_type = self.ParentWindow.Table.GetValueByName(row, "Type")
                        base_type = self.ParentWindow.Controler.GetBaseType(variable_type)

                        if values[2] is not None:
                            base_location_type = self.ParentWindow.Controler.GetBaseType(values[2])
                            if values[2] != variable_type and base_type != base_location_type:
                                message = _("Incompatible data types between \"{a1}\" and \"{a2}\"").\
                                          format(a1=values[2], a2=variable_type)

                        if message is None:
                            if not location.startswith("%"):
                                if location[0].isdigit() and base_type != "BOOL":
                                    message = _("Incompatible size of data between \"%s\" and \"BOOL\"") % location
                                elif location[0] not in LOCATIONDATATYPES:
                                    message = _("Unrecognized data size \"%s\"") % location[0]
                                elif base_type not in LOCATIONDATATYPES[location[0]]:
                                    message = _("Incompatible size of data between \"{a1}\" and \"{a2}\"").\
                                              format(a1=location, a2=variable_type)
                                else:
                                    dialog = wx.SingleChoiceDialog(
                                        self.ParentWindow.ParentWindow.ParentWindow,
                                        _("Select a variable class:"),
                                        _("Variable class"),
                                        [_("Input"), _("Output"), _("Memory")],
                                        wx.DEFAULT_DIALOG_STYLE | wx.OK | wx.CANCEL)
                                    if dialog.ShowModal() == wx.ID_OK:
                                        selected = dialog.GetSelection()
                                    else:
                                        selected = None
                                    dialog.Destroy()
                                    if selected is None:
                                        return
                                    if selected == 0:
                                        location = "%I" + location
                                    elif selected == 1:
                                        location = "%Q" + location
                                    else:
                                        location = "%M" + location

                            if message is None:
                                self.ParentWindow.Table.SetValue(row, col, location)
                                self.ParentWindow.Table.ResetView(self.ParentWindow.VariablesGrid)
                                self.ParentWindow.SaveValues()
                elif colname == "Initial Value" and values[1] == "Constant":
                    if not self.ParentWindow.Table.GetValueByName(row, "Edit"):
                        message = _("Can't set an initial value to a function block instance")
                    else:
                        self.ParentWindow.Table.SetValue(row, col, values[0])
                        self.ParentWindow.Table.ResetView(self.ParentWindow.VariablesGrid)
                        self.ParentWindow.SaveValues()
            elif (element_type not in ["config", "resource", "function"] and values[1] == "Global" and
                  self.ParentWindow.Filter in ["All", "Interface", "External"] or
                  element_type != "function" and values[1] in ["location", "NamedConstant"]):
                if values[1] in ["location", "NamedConstant"]:
                    var_name = values[3]
                else:
                    var_name = values[0]
                tagname = self.ParentWindow.GetTagName()
                dlg = wx.TextEntryDialog(
                    self.ParentWindow.ParentWindow.ParentWindow,
                    _("Confirm or change variable name"),
                    _('Variable Drop'), var_name)
                dlg.SetValue(var_name)
                var_name = dlg.GetValue() if dlg.ShowModal() == wx.ID_OK else None
                dlg.Destroy()
                if var_name is None:
                    return
                elif var_name.upper() in [
                        name.upper() for name in
                        self.ParentWindow.Controler.GetProjectPouNames(self.ParentWindow.Debug)]:
                    message = _("\"%s\" pou already exists!") % var_name
                elif not var_name.upper() in [
                        name.upper()
                        for name in self.ParentWindow.Controler.
                        GetEditedElementVariables(tagname, self.ParentWindow.Debug)]:
                    var_infos = self.ParentWindow.DefaultValue.copy()
                    var_infos.Name = var_name
                    var_infos.Type = values[2]
                    var_infos.Documentation = values[4]
                    if values[1] == "location":
                        location = values[0]
                        if not location.startswith("%"):
                            dialog = wx.SingleChoiceDialog(
                                self.ParentWindow.ParentWindow.ParentWindow,
                                _("Select a variable class:"),
                                _("Variable class"),
                                [_("Input"), _("Output"), _("Memory")],
                                wx.DEFAULT_DIALOG_STYLE | wx.OK | wx.CANCEL)
                            if dialog.ShowModal() == wx.ID_OK:
                                selected = dialog.GetSelection()
                            else:
                                selected = None
                            dialog.Destroy()
                            if selected is None:
                                return
                            if selected == 0:
                                location = "%I" + location
                            elif selected == 1:
                                location = "%Q" + location
                            else:
                                location = "%M" + location
                        if element_type == "functionBlock":
                            configs = self.ParentWindow.Controler.GetProjectConfigNames(
                                                                self.ParentWindow.Debug)
                            if len(configs) == 0:
                                return
                            if not var_name.upper() in [
                                    name.upper() for name in
                                    self.ParentWindow.Controler.GetConfigurationVariableNames(configs[0])]:
                                self.ParentWindow.Controler.AddConfigurationGlobalVar(
                                    configs[0], values[2], var_name, location, "")
                            var_infos.Class = "External"
                        else:
                            if element_type == "program":
                                var_infos.Class = "Local"
                            else:
                                var_infos.Class = "Global"
                            var_infos.Location = location
                    elif values[1] == "NamedConstant":
                        if element_type in ["functionBlock", "program"]:
                            var_infos.Class = "Local"
                            var_infos.InitialValue = values[0]
                        else:
                            return
                    else:
                        var_infos.Class = "External"
                    var_infos.Number = len(self.ParentWindow.Values)
                    self.ParentWindow.Values.append(var_infos)
                    self.ParentWindow.SaveValues()
                    self.ParentWindow.RefreshValues()
                else:
                    message = _("\"%s\" element for this pou already exists!") % var_name

        if message is not None:
            wx.CallAfter(self.ShowMessage, message)
            return False
        else:
            return True

    def ShowMessage(self, message):
        message = wx.MessageDialog(self.ParentWindow, message, _("Error"), wx.OK | wx.ICON_ERROR)
        message.ShowModal()
        message.Destroy()


# -------------------------------------------------------------------------------
#                               Variable Panel
# -------------------------------------------------------------------------------

class VariablePanel(wx.Panel):

    def __init__(self, parent, window, controler, element_type, debug=False, notebookPage=0):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)
        self.ParentWindow = window
        self.Controler = controler
        self.ElementType = element_type
        self.Debug = debug

        if element_type == "config":
            self.MainSizer = wx.FlexGridSizer(cols=1, hgap=10, rows=3, vgap=0)
            self.MainSizer.AddGrowableCol(0)
            self.MainSizer.AddGrowableRow(2)
        else:
            self.MainSizer = wx.FlexGridSizer(cols=1, hgap=10, rows=2, vgap=0)

            self.MainSizer.AddGrowableCol(0)
            self.MainSizer.AddGrowableRow(1)

        self.SelectGroup = None
        self.listBox = None

        controls_sizer = wx.FlexGridSizer(cols=10, hgap=5, rows=1, vgap=5)
        controls_sizer.AddGrowableCol(5)
        controls_sizer.AddGrowableRow(0)
        self.MainSizer.Add(controls_sizer, border=5, flag=wx.GROW | wx.ALL)



        self.ReturnTypeLabel = wx.StaticText(self, label=_('Return Type:'))
        controls_sizer.Add(self.ReturnTypeLabel, flag=wx.ALIGN_CENTER_VERTICAL)

        self.ReturnType = wx.ComboBox(self,
                                      size=wx.Size(145, -1), style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnReturnTypeChanged, self.ReturnType)
        controls_sizer.Add(self.ReturnType)

        self.DescriptionLabel = wx.StaticText(self, label=_('Description:'))
        controls_sizer.Add(self.DescriptionLabel, flag=wx.ALIGN_CENTER_VERTICAL)

        self.Description = wx.TextCtrl(self,
                                       size=wx.Size(250, -1), style=wx.TE_PROCESS_ENTER)
        self.Bind(wx.EVT_TEXT_ENTER, self.OnDescriptionChanged, self.Description)
        self.Description.Bind(wx.EVT_KILL_FOCUS, self.OnDescriptionChanged)
        controls_sizer.Add(self.Description)

        class_filter_label = wx.StaticText(self, label=_('Class Filter:'))
        controls_sizer.Add(class_filter_label, flag=wx.ALIGN_CENTER_VERTICAL)

        self.ClassFilter = wx.ComboBox(self,
                                       size=wx.Size(145, -1), style=wx.CB_READONLY)
        self.Bind(wx.EVT_COMBOBOX, self.OnClassFilter, self.ClassFilter)
        controls_sizer.Add(self.ClassFilter)

        self.NotebookPage = notebookPage

        for name, bitmap, help in [
                ("AddButton", "add_element", _("Add variable")),
                ("DeleteButton", "remove_element", _("Remove variable")),
                ("UpButton", "up", _("Move variable up")),
                ("DownButton", "down", _("Move variable down"))]:
            button = wx.lib.buttons.GenBitmapButton(self, bitmap=GetBitmap(bitmap),
                                                    size=wx.Size(28, 28), style=wx.NO_BORDER)
            button.SetToolTip(help)
            setattr(self, name, button)
            controls_sizer.Add(button)

        self.VariablesGrid = CustomGrid(self, style=wx.VSCROLL | wx.HSCROLL)

        self.VariablesGrid.SetDropTarget(VariableDropTarget(self))
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED,
                                self.OnVariablesGridCellChange)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnVariablesGridCellLeftClick)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_cell_right_click)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_cell_right_click)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_CLICK, self.on_cell_right_click)

        ctrl_C_id = wx.NewId()
        ctrl_V_id = wx.NewId()

        self.Bind(wx.EVT_MENU, self.onCtrlV, id=ctrl_V_id)
        self.Bind(wx.EVT_MENU, self.onCtrlC, id=ctrl_C_id)

        acce1_tb1 = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('C'), ctrl_C_id),
                                        (wx.ACCEL_CTRL, ord('V'), ctrl_V_id)])

        self.SetAcceleratorTable(acce1_tb1)


        self.MainSizer.Add(self.VariablesGrid, flag=wx.GROW)
        self.SetSizer(self.MainSizer)


        self.RefreshHighlightsTimer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnRefreshHighlightsTimer,
                  self.RefreshHighlightsTimer)

        self.Filter = "All"
        self.FilterChoices = []
        self.FilterChoiceTransfer = GetFilterChoiceTransfer()

        self.DefaultValue = _VariableInfos("", "", "", "", "", True, "", (_("Default")), DefaultType, ([], []), 0)

        if element_type in ["config", "resource"]:
            self.DefaultTypes = {"All": "Global"}
        elif element_type in ["functionBlock", "program"]:
            if notebookPage == VARIABLEPANEL_LOCAL:
                self.DefaultTypes = {"All": "Local", "Interface": "Input", "Variables": "Local"}
            elif notebookPage == VARIABLEPANEL_GLOBAL:
                self.DefaultTypes = {"All": "External", "Interface": "External", "Variables": "Local"}
            elif notebookPage == VARIABLEPANEL_FB:
                self.DefaultTypes = {"All": "Local", "Interface": "Input", "Variables": "Local"}
        else:
            self.DefaultTypes = {"All": "Local", "Interface": "Input", "Variables": "Local"}

        if element_type in ["config", "resource"] \
           or element_type in ["transition", "action"]:
           #or element_type in ["program", "transition", "action"]:
            # this is an element that can have located variables
            self.Table = VariableTable(self, [], GetVariableTableColnames(True, True))

            if element_type in ["config", "resource"]:
                self.FilterChoices = ["All", "Global"]  # ,"Access"]
            else:
                self.FilterChoices = ["All",
                                      "Interface", "   Input", "   Output", "   InOut", "   External",
                                      "Variables", "   Local", "   Temp"]  # ,"Access"]

            # these condense the ColAlignements list
            left = wx.ALIGN_LEFT
            center = wx.ALIGN_CENTER

            #                       Num      Group   Name    Class   Type    Loc     Init    Option   Doc
            self.ColSettings = {
                "size":             [40,      100,    80,     100,    80,     110,    120,    100,     160],
                "alignement":       [center, left,   left,   left,   left,   left,   left,   left,    left],
                "fixed_size":       [True,   False,  False,  True,   False,  True,   True,   True,    False],
            }

        else:
            # this is an element that cannot have located variables
            self.Table = VariableTable(self, [], GetVariableTableColnames(False, True))

            if element_type == "function":
                self.FilterChoices = ["All",
                                      "Interface", "   Input", "   Output", "   InOut",
                                      "Variables", "   Local"]
            elif element_type in ["program", "functionBlock"]:
                if notebookPage in [VARIABLEPANEL_LOCAL, VARIABLEPANEL_FB]:
                    self.FilterChoices = ["All",
                                          "Interface", "   Input", "   Output", "   InOut",
                                          "Variables", "   Local", "   Temp"]
                elif notebookPage == VARIABLEPANEL_GLOBAL:
                    self.FilterChoices = ["All",
                                          "Interface", "   External"
                                          ]
            else:
                self.FilterChoices = ["All",
                                      "Interface", "   Input", "   Output", "   InOut", "   External",
                                      "Variables", "   Local", "   Temp"]

            # these condense the alignements list
            left = wx.ALIGN_LEFT
            center = wx.ALIGN_CENTER
            self.Table = VariableTable(self, [], GetVariableTableColnames(False, False))
            #                        Num      Name    Class   Type    Init    Option   Doc
            self.ColSettings = {
                "size":             [0,       80,     100,    80,     120,    100,     160],
                "alignement":       [center,  left,   left,   left,   left,   left,    left],
                "fixed_size":       [True,    False,  True,   False,  True,   True,    False],
            }

        if self.listBox is not None:
            self.Table.GroupList = self.listBox.GetStrings()

        self.PanelWidthMin = sum(self.ColSettings["size"])

        self.ElementType = element_type
        self.BodyType = None

        for choice in self.FilterChoices:
            self.ClassFilter.Append(_(choice))

        reverse_transfer = {}
        for filter, choice in list(self.FilterChoiceTransfer.items()):
            reverse_transfer[choice] = filter
        self.ClassFilter.SetStringSelection(_(reverse_transfer[self.Filter]))
        self.RefreshTypeList()

        self.VariablesGrid.SetTable(self.Table)
        self.VariablesGrid.SetButtons({"Add": self.AddButton,
                                       "Delete": self.DeleteButton,
                                       "Up": self.UpButton,
                                       "Down": self.DownButton})
        self.VariablesGrid.SetEditable(not self.Debug)

        def _AddVariable(new_row, Name=None, type=None, Save=True):
            if type is None:
                if self.ElementType in ["functionBlock", "program"] and self.NotebookPage == VARIABLEPANEL_FB:
                    type = self.Controler.GetFunctionBlockTypes()[0]
            if new_row > 0:
                test = self.Table.GetValueByName(new_row - 1, "Name")
                for index, variable in enumerate(self.Values):
                    if variable.Name == test:
                        new_row = index
                row_content = self.Values[new_row - 1].copy()
                if self.SelectGroup is not None:
                    if not(self.SelectGroup in [(_("All")), (_("Default"))]):
                        row_content.Group = self.SelectGroup
                # IT::START 14.01.2022
                if Name is not None:
                    result = VARIABLE_NAME_SUFFIX_MODEL.search(Name)
                else:
                # IT::END 14.01.2022
                    result = VARIABLE_NAME_SUFFIX_MODEL.search(row_content.Name)
                if result is not None:
                    name = row_content.Name[:result.start(1)]
                    if Name is not None:
                        name = Name[:result.start(1)]
                    suffix = result.group(1)
                    if suffix != "":
                        start_idx = int(suffix)
                    else:
                        start_idx = 0
                else:
                    name = row_content.Name
                    start_idx = 0
            else:
                row_content = None
                start_idx = 0
                name = "LocalVar"
                if self.DefaultTypes["All"] == "Global":
                    name = "GlobalVar"


            if row_content is not None and row_content.Edit:
                row_content = self.Values[new_row - 1].copy()
                if self.SelectGroup is not None:
                    if not(self.SelectGroup in [(_("All")), (_("Default"))]):
                        row_content.Group = self.SelectGroup
                if type is not None:
                    row_content.Type = type
            else:
                row_content = self.DefaultValue.copy()
                if self.SelectGroup is not None:
                    if not(self.SelectGroup in [(_("All")), (_("Default"))]):
                        row_content.Group = self.SelectGroup

                if type is not None:
                    row_content.Type = type

                if self.Filter in self.DefaultTypes:
                    row_content.Class = self.DefaultTypes[self.Filter]
                else:
                    row_content.Class = self.Filter

            row_content.Name = self.Controler.GenerateNewName(
                    self.TagName, None, name + "%d", start_idx)

            if self.Filter == "All" and len(self.Values) > 0:
                self.Values.insert(new_row, row_content)
            else:
                self.Values.append(row_content)
                new_row = self.Table.GetNumberRows()
            if Save:
                self.SaveValues()
            if self.ElementType == "resource":
                self.ParentWindow.RefreshView(variablepanel=False)
            self.RefreshValues()
            return new_row
        setattr(self.VariablesGrid, "_AddRow", _AddVariable)

        def _DeleteVariable(row):
            if _GetRowEdit(row):
                self.Values.remove(self.Table.GetRow(row))
                self.SaveValues()
                if self.ElementType == "resource":
                    self.ParentWindow.RefreshView(variablepanel=False)
                self.RefreshValues()
        setattr(self.VariablesGrid, "_DeleteRow", _DeleteVariable)

        def _MoveVariable(row, move):
            if self.Filter == "All":
                new_row = max(0, min(row + move, len(self.Values) - 1))
                if new_row != row:
                    self.Values.insert(new_row, self.Values.pop(row))
                    self.SaveValues()
                    self.RefreshValues()
                return new_row
            return row
        setattr(self.VariablesGrid, "_MoveRow", _MoveVariable)

        def _GetRowEdit(row):
            row_edit = False
            if self:
                row_edit = self.Table.GetValueByName(row, "Edit")
                bodytype = self.Controler.GetEditedElementBodyType(self.TagName)
                row_edit = row_edit or (bodytype in ["ST", "IL"])
            return row_edit

        def _RefreshButtons():
            if self:
                table_length = len(self.Table.data)
                row_class = None
                row_edit = True
                row = 0
                if table_length > 0:
                    row = self.VariablesGrid.GetGridCursorRow()
                    row_edit = _GetRowEdit(row)
                bodytype = self.Controler.GetEditedElementBodyType(self.TagName)
                AddButtonEnabled = self.NotebookPage != VARIABLEPANEL_FB or (bodytype in ["ST", "IL"])
                self.AddButton.Enable(not self.Debug and AddButtonEnabled)
                self.DeleteButton.Enable(not self.Debug and (table_length > 0 and row_edit))
                self.UpButton.Enable(not self.Debug and (table_length > 0 and row > 0 and self.Filter == "All"))
                self.DownButton.Enable(not self.Debug and (table_length > 0 and row < table_length - 1 and self.Filter == "All"))
        setattr(self.VariablesGrid, "RefreshButtons", _RefreshButtons)

        panel_width = window.Parent.ScreenRect.Width - 35
        if panel_width > self.PanelWidthMin:
            stretch_cols_width = panel_width
            stretch_cols_sum = 0
            for col in range(len(self.ColSettings["fixed_size"])):
                if self.ColSettings["fixed_size"][col]:
                    stretch_cols_width -= self.ColSettings["size"][col]
                else:
                    stretch_cols_sum += self.ColSettings["size"][col]

        self.VariablesGrid.SetRowLabelSize(0)

        for col in range(self.Table.GetNumberCols()):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(self.ColSettings["alignement"][col], wx.ALIGN_CENTRE)
            self.VariablesGrid.SetColAttr(col, attr)
            self.VariablesGrid.SetColMinimalWidth(col, self.ColSettings["size"][col])
            if (panel_width > self.PanelWidthMin) and not self.ColSettings["fixed_size"][col]:
                self.VariablesGrid.SetColSize(col, int((float(self.ColSettings["size"][col])/stretch_cols_sum)*stretch_cols_width))
            else:
                self.VariablesGrid.SetColSize(col, self.ColSettings["size"][col])

    def __del__(self):
        self.RefreshHighlightsTimer.Stop()

    def RefreshView(self):
        pass


    def SetTagName(self, tagname):
        self.TagName = tagname
        self.BodyType = self.Controler.GetEditedElementBodyType(self.TagName)

    def GetTagName(self):
        return self.TagName

    def IsFunctionBlockType(self, name):
        if isinstance(name, tuple) or \
           self.ElementType != "function" and self.BodyType in ["ST", "IL"]:
            return False
        else:
            return self.Controler.GetBlockType(name, debug=self.Debug) is not None

    def OnReturnTypeChanged(self, event):
        words = self.TagName.split("::")
        self.Controler.SetPouInterfaceReturnType(words[1], self.ReturnType.GetStringSelection())
        self.Controler.BufferProject()
        self.ParentWindow.RefreshView(variablepanel=False)
        self.ParentWindow._Refresh(TITLE, FILEMENU, EDITMENU, POUINSTANCEVARIABLESPANEL, LIBRARYTREE)
        event.Skip()

    def OnDescriptionChanged(self, event):
        words = self.TagName.split("::")
        old_description = self.Controler.GetPouDescription(words[1])
        new_description = self.Description.GetValue()
        if new_description != old_description:
            self.Controler.SetPouDescription(words[1], new_description)
            self.ParentWindow._Refresh(TITLE, FILEMENU, EDITMENU, PAGETITLES, POUINSTANCEVARIABLESPANEL, LIBRARYTREE)
        event.Skip()

    def OnClassFilter(self, event):
        self.Filter = self.FilterChoiceTransfer[VARIABLE_CHOICES_DICT[self.ClassFilter.GetStringSelection()]]
        self.RefreshTypeList()
        self.RefreshValues()
        self.VariablesGrid.RefreshButtons()
        event.Skip()

    def RefreshTypeList(self):
        if self.Filter == "All":
            self.ClassList = [self.FilterChoiceTransfer[choice] for choice in self.FilterChoices if self.FilterChoiceTransfer[choice] not in ["All", "Interface", "Variables"]]
        elif self.Filter == "Interface":
            self.ClassList = ["Input", "Output", "InOut", "External"]
        elif self.Filter == "Variables":
            self.ClassList = ["Local", "Temp"]
        else:
            self.ClassList = [self.Filter]

    def ShowErrorMessage(self, message):
        dialog = wx.MessageDialog(self, message, _("Error"), wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()
        dialog.Destroy()

    def SetFormalParamInPou(self, pou, value, old_value):
        tagname = self.Controler.ComputePouName(pou.getname())
        if self.ElementType != "function":
            if self.Controler.PouIsUsedBy(self.TagName.split("::")[1], tagname.split("::")[1]):
                self.Controler.SetFormalParameter(tagname, old_value, value,
                                                  self.TagName.split("::")[1])
        else:
            self.Controler.SetFormalParameter(tagname, old_value, value,
                                              self.TagName.split("::")[1])

    def SetNameEditedVariablePou(self, value, old_value, tagname):
        var_name_pou = self.Controler.GetEditedElementVariables(tagname, self.Debug)
        if old_value in var_name_pou:
            i = var_name_pou.index(old_value)
            Values = self.Controler.GetEditedElementInterfaceVars(tagname, debug=self.Debug)
            if Values[i].Name == old_value:
                Values[i].Name = value
            else:
                print("\nError in Variable Panel rename values\n")
            self.Controler.SetPouInterfaceVars(tagname.split("::")[1], Values)

    def OnVariablesGridCellChange(self, event, row=None, col=None):
        if row is None or col is None:
            row, col = event.GetRow(), event.GetCol()
        colname = self.Table.GetColLabelValue(col, False)
        value = self.Table.GetValue(row, col)
        message = None
        message_warn = None
        if not self.ParentWindow.CheckPouInOut:
            if colname == "Class" and self.ElementType == "functionBlock":
                if self.Table.GetValueByName(row, "Class") in ["Input", "Output", "InOut"]:
                    fb_list_name = self.Controler.GetPouNamesIsUsedFB(self.TagName.split("::")[1])
                    if len(fb_list_name) > 0:
                        message_warn = "WARNING: Check function block \'" + self.TagName.split("::")[1] + "\' in program/function blocks : \n" + ", ".join(
                    fb_list_name)

            if colname == "Class" and self.ElementType == "function":
                if self.Table.GetValueByName(row, "Class") in ["Input", "Output", "InOut"]:
                    func_name = self.TagName.split("::")[1]
                    instance_func = self.Controler.GetFbNameIsFuncUsed(func_name, self.Debug)
                    if len(instance_func) > 0:
                        message_warn = "WARNING: Check function \'" + func_name + "\' in program/function blocks : \n" + ", ".join(
                            instance_func)

        if colname == "Name" and value != "":
            if not TestIdentifier(value):
                message = _("\"%s\" is not a valid identifier!") % value
            elif value.upper() in IEC_KEYWORDS:
                message = _("\"%s\" is a keyword. It can't be used!") % value
            elif value.upper() in self.PouNames:
                message = _("A POU named \"%s\" already exists!") % value
            elif value.upper() in [var.Name.upper() for var in self.Values if var != self.Table.data[row]]:
                message = _("A variable with \"%s\" as name already exists in this pou!") % value
            else:
                old_value = self.Table.GetOldValue()
                if old_value != "":
                    self.Controler.UpdateEditedElementUsedVariable(self.TagName, old_value, value)
                    if self.TagName == "C::config":
                        project = self.Controler.GetProject(self.Debug)
                        oldVal_tagname = []
                        for pou in project.getpous():
                            tagname = self.Controler.ComputePouName(pou.getname())
                            oldVal_tagname.append(tagname)
                            self.SetNameEditedVariablePou(value, old_value, tagname)
                            #th = Thread(target=self.SetNameEditedVariablePou, args=(value, old_value, tagname, ))
                            #th.start()
                        for tagname in oldVal_tagname:
                            self.Controler.UpdateEditedElementUsedVariable(tagname, old_value, value)
                    else:
                        project = self.Controler.GetProject(self.Debug)
                        for pou in project.getpous():
                            self.SetFormalParamInPou(pou, value, old_value)
                            #th = Thread(target=self.SetFormalParamInPou, args=(pou, value, old_value, ))
                            #th.start()
                self.Controler.BufferProject()
                self.SaveValues()
                wx.CallAfter(self.ParentWindow.RefreshView, False)
                self.ParentWindow._Refresh(TITLE, FILEMENU, EDITMENU, PAGETITLES, POUINSTANCEVARIABLESPANEL, LIBRARYTREE, VARIABLETREE)
        else:
            if colname == "Initial Value":
                if "," in value:
                    message = _("The value of a constant must not contain the character") + " \',\'"
            if message is None:
                self.SaveValues()
            if colname == "Class":
                self.ClearLocation(row, col, value)
                wx.CallAfter(self.ParentWindow.RefreshView)
            elif colname == "Location":
                wx.CallAfter(self.ParentWindow.RefreshView)
            elif colname == "Group":
                wx.CallAfter(self.ParentWindow.RefreshView)
        if message_warn is not None:
            self.ParentWindow.CheckPouInOut = True
            self.Controler.logger.flush()
            self.Controler.logger.write_warning(message_warn)
        if message is not None:
            wx.CallAfter(self.ShowErrorMessage, message)
            event.Veto()
        else:
            event.Skip()

    def ClearLocation(self, row, col, value):
        if self.Values[row].Location != '':
            if self.Table.GetColLabelValue(col, False) == 'Class' and value not in ["Local", "Global"] or \
               self.Table.GetColLabelValue(col, False) == 'Type' and not self.Controler.IsLocatableType(value):
                self.Values[row].Location = ''
                self.RefreshValues()
                self.SaveValues()

    def BuildStdIECTypesMenu(self, type_menu):
            # build a submenu containing standard IEC types
            base_menu = wx.Menu(title='')
            for base_type in self.Controler.GetBaseTypes():
                new_id = wx.NewId()
                base_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=base_type)
                self.Bind(wx.EVT_MENU, self.GetVariableTypeFunction(base_type), id=new_id)

            type_menu.Append(wx.NewId(), _("Base Types"), base_menu)

    def BuildUserTypesMenu(self, type_menu):
            # build a submenu containing user-defined types
            datatype_menu = wx.Menu(title='')
            datatypes = self.Controler.GetDataTypes(basetypes=False, confnodetypes=False)
            for datatype in datatypes:
                new_id = wx.NewId()
                datatype_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=datatype)
                self.Bind(wx.EVT_MENU, self.GetVariableTypeFunction(datatype), id=new_id)

            type_menu.Append(wx.NewId(), _("User Data Types"), datatype_menu)

    def BuildGlobalVarTypesMenu(self, type_menu, Variables=None, Resource=False):
        datatype_menu = wx.Menu(title='')
        pouVar_name = []
        for var in self.Values:
            pouVar_name.append(var.Name)
        if Variables is None:
            Variables = sorted(self.Controler.GetConfigurationGlobalVars('config'), key=lambda x: x.Group)
        if Resource:
            lastGroup = _("Resources")
        else:
            if Variables: #len(Variables) == 0:
                return
            lastGroup = Variables[0].Group

        for num, var in enumerate(Variables):
            if var.Group != lastGroup and not Resource:
                if lastGroup == '':
                    lastGroup = (_("Default"))
                new_id = wx.NewId()
                type_menu.Append(new_id, lastGroup, datatype_menu)
                if datatype_menu.GetMenuItemCount() <= 0:
                    type_menu.Enable(id=new_id, enable=False)

                self.BuildGlobalVarTypesMenu(type_menu, Variables[num:], Resource)
                return
            else:
                if var.Name not in pouVar_name:
                    new_id = wx.NewId()
                    datatype_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=var.Name)
                    self.Bind(wx.EVT_MENU, self.GetVariableNameTypeFunction(var.Name, var.Type), id=new_id)

        if(lastGroup == ''):
            lastGroup = (_("Default"))
        new_id = wx.NewId()
        type_menu.Append(new_id, lastGroup, datatype_menu)
        if datatype_menu.GetMenuItemCount() <= 0:
            type_menu.Enable(id=new_id, enable=False)


    def BuildLibsTypesMenu(self, type_menu):
        for category in self.Controler.GetConfNodeDataTypes():
            if len(category["list"]) > 0:
                # build a submenu containing confnode types
                confnode_datatype_menu = wx.Menu(title='')
                for datatype in category["list"]:
                    new_id = wx.NewId()
                    confnode_datatype_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=datatype)
                    self.Bind(wx.EVT_MENU, self.GetVariableTypeFunction(datatype), id=new_id)

                type_menu.Append(wx.NewId(), category["name"], confnode_datatype_menu)

    def BuildProjectTypesMenu(self, type_menu, classtype):
        # build a submenu containing function block types
        bodytype = self.Controler.GetEditedElementBodyType(self.TagName)
        pouname, poutype = self.Controler.GetEditedElementType(self.TagName)
        if classtype in ["Input", "Output", "InOut", "External", "Global"] or \
           poutype != "function" and bodytype in ["ST", "IL"]:
            functionblock_menu = wx.Menu(title='')
            fbtypes = self.Controler.GetFunctionBlockTypes(self.TagName)
            for functionblock_type in fbtypes:
                new_id = wx.NewId()
                functionblock_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=functionblock_type)
                self.Bind(wx.EVT_MENU, self.GetVariableTypeFunction(functionblock_type), id=new_id)

            type_menu.Append(wx.NewId(), _("Function Block Types"), functionblock_menu)

    def BuildArrayTypesMenu(self, type_menu):
        new_id = wx.NewId()
        type_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=_("Array"))
        self.Bind(wx.EVT_MENU, self.VariableArrayTypeFunction, id=new_id)

    def SetTypeEditedVariablePou(self, pou, base_type, old_TypeValue, variable_name):
        tagname = self.Controler.ComputePouName(pou.getname())
        var_name_pou = self.Controler.GetEditedElementVariables(tagname, self.Debug)
        if variable_name in var_name_pou:
            i = var_name_pou.index(variable_name)
            Values = self.Controler.GetEditedElementInterfaceVars(tagname, debug=self.Debug)
            if Values[i].Type == old_TypeValue and Values[i].Name == variable_name:
                Values[i].Type = base_type
            else:
                print("\nError in Variable Panel rename values\n")
            self.Controler.SetPouInterfaceVars(tagname.split("::")[1], Values)

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            row = self.VariablesGrid.GetGridCursorRow()
            col = self.VariablesGrid.GetGridCursorCol()
            old_TypeValue = self.Table.GetValueByName(row, "Type")
            self.Table.SetValueByName(row, "Type", base_type)
            variable_name = self.Table.GetValueByName(row, "Name")
            #return VariableTypeFunction
            if old_TypeValue != "" and base_type != old_TypeValue:
                if "config" in self.TagName:
                    project = self.Controler.GetProject(self.Debug)
                    for pou in project.getpous():
                        th = Thread(target=self.SetTypeEditedVariablePou, args=(pou, base_type, old_TypeValue, variable_name, ))
                        th.start()
            self.Table.ResetView(self.VariablesGrid)
            self.SaveValues(False)
            self.ParentWindow.RefreshView(variablepanel=False)
            self.Controler.BufferProject()
            self.ParentWindow._Refresh(TITLE, FILEMENU, EDITMENU, PAGETITLES, POUINSTANCEVARIABLESPANEL, LIBRARYTREE)
        return VariableTypeFunction

    def GetVariableNameTypeFunction(self, base_name, base_type):
        def VariableNameFunction(event):
            row = self.VariablesGrid.GetGridCursorRow()
            col = self.VariablesGrid.GetGridCursorCol()
            old_value = self.Table.GetValueByName(row, "Name")
            self.Table.SetValueByName(row, "Name", base_name)
            self.Table.SetValueByName(row, "Type", base_type)
            self.Table.ResetView(self.VariablesGrid)

            self.Controler.BufferProject()
            if old_value != "":
                self.Controler.UpdateEditedElementUsedVariable(self.TagName, old_value, base_name)
            self.Controler.BufferProject()
            self.SaveValues()
            wx.CallAfter(self.ParentWindow.RefreshView, False)
            #self.OnVariablesGridCellChange(event, col=col, row=row)
            self.ParentWindow._Refresh(TITLE, FILEMENU, EDITMENU, PAGETITLES, POUINSTANCEVARIABLESPANEL, LIBRARYTREE, VARIABLETREE)
        return VariableNameFunction

    def VariableArrayTypeFunction(self, event):
        row = self.VariablesGrid.GetGridCursorRow()
        dialog = ArrayTypeDialog(self,
                                 self.Controler.GetDataTypes(self.TagName),
                                 self.Table.GetValueByName(row, "Type"))
        if dialog.ShowModal() == wx.ID_OK:
            dialog.OnOK(None)
            self.Table.SetValueByName(row, "Type", dialog.GetValue())
            self.Table.ResetView(self.VariablesGrid)
            self.SaveValues(False)
            self.ParentWindow.RefreshView(variablepanel=False)
            self.Controler.BufferProject()
            self.ParentWindow._Refresh(TITLE, FILEMENU, EDITMENU, PAGETITLES, POUINSTANCEVARIABLESPANEL, LIBRARYTREE)
        dialog.Destroy()


    def OnVariablesGridCellLeftClick(self, event):
        row = event.GetRow()

        if not self.Debug and (event.GetCol() == 0 and self.Table.GetValueByName(row, "Edit")):
            var_name = self.Table.GetValueByName(row, "Name")
            var_class = self.Table.GetValueByName(row, "Class")
            var_type = self.Table.GetValueByName(row, "Type")
            data = wx.TextDataObject(str((var_name, var_class, var_type, self.TagName)))
            dragSource = wx.DropSource(self.VariablesGrid)
            dragSource.SetData(data)
            dragSource.DoDragDrop()
        event.Skip()

    def RefreshValueByGroup(self):
        data = []
        for num, variable in enumerate(self.Values):
            if variable.Group == "":
                variable.Group = _("Default")
            if variable.Group == self.SelectGroup:
                variable.Number = num + 1
                data.append(variable)
        self.Table.SetData(data)
        self.Table.ResetView(self.VariablesGrid)

    def SetGroupNameVariables(self, name, renamed):
        data = []
        for num, variable in enumerate(self.Values):
            if variable.Group == name:
                variable.Group = renamed
                variable.Number = num + 1
                data.append(variable)
            elif variable.Group == renamed:
                variable.Number = num + 1
                data.append(variable)

        self.Table.SetData(data)
        self.Table.ResetView(self.VariablesGrid)

    def RefreshValues(self):
        data = []
        for num, variable in enumerate(self.Values):
            if variable.Class in self.ClassList:
                variable.Number = num + 1
                data.append(variable)
        self.Table.SetData(data)
        if self.VariablesGrid.SelectSortColumn is not None:
            self.VariablesGrid.SortColumn(self.VariablesGrid.SelectSortColumn)
        self.Table.ResetView(self.VariablesGrid)

    def SaveValues(self, buffer=True):
        words = self.TagName.split("::")
        if self.ElementType == "config":
            self.Controler.SetConfigurationGlobalVars(words[1], self.Values)
        elif self.ElementType == "resource":
            self.Controler.SetConfigurationResourceGlobalVars(words[1], words[2], self.Values)
        else:
            if self.ReturnType.IsEnabled():
                self.Controler.SetPouInterfaceReturnType(words[1], self.ReturnType.GetStringSelection())
            if self.ElementType != "function":
                self.ParentWindow.SaveValues(words[1])
            else:
                self.Controler.SetPouInterfaceVars(words[1], self.Values)
        if buffer:
            self.Controler.BufferProject()
            self.ParentWindow._Refresh(TITLE, FILEMENU, EDITMENU, PAGETITLES, POUINSTANCEVARIABLESPANEL, LIBRARYTREE,
                                       VARIABLETREE)
        else:
            self.ParentWindow._Refresh(VARIABLETREE)

    # -------------------------------------------------------------------------------
    #                        Highlights showing functions
    # -------------------------------------------------------------------------------

    def OnRefreshHighlightsTimer(self, event):
        self.Table.ResetView(self.VariablesGrid)
        event.Skip()

    def AddVariableHighlight(self, infos, highlight_type):
        if isinstance(infos[0], tuple):
            for i in range(*infos[0]):
                self.Table.AddHighlight((i,) + infos[1:], highlight_type)
            cell_visible = infos[0][0]
        else:
            self.Table.AddHighlight(infos, highlight_type)
            cell_visible = infos[0]
        colnames = [colname.lower() for colname in self.Table.colnames]
        self.VariablesGrid.MakeCellVisible(cell_visible, colnames.index(infos[1]))
        self.RefreshHighlightsTimer.Start(int(REFRESH_HIGHLIGHT_PERIOD * 1000), oneShot=True)

    def RemoveVariableHighlight(self, infos, highlight_type):
        if isinstance(infos[0], tuple):
            for i in range(*infos[0]):
                self.Table.RemoveHighlight((i,) + infos[1:], highlight_type)
        else:
            self.Table.RemoveHighlight(infos, highlight_type)
        self.RefreshHighlightsTimer.Start(int(REFRESH_HIGHLIGHT_PERIOD * 1000), oneShot=True)

    def ClearHighlights(self, highlight_type=None):
        self.Table.ClearHighlights(highlight_type)
        self.Table.ResetView(self.VariablesGrid)


    def on_cell_right_clickGrid(self, event):
        menus = [(wx.NewId(), _("Copy"), self.copyGrid),
                 (wx.NewId(), _("Paste"), self.pasteGrid),
                 (wx.NewId(), _("Delete"), self.deleteRow)]
        popup_menu = wx.Menu()
        for menu in menus:
            if menu is None:
                popup_menu.AppendSeparator()
                continue
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.VariablesGrid.PopupMenu(popup_menu, event.GetPosition())
        popup_menu.Destroy()

    def on_cell_right_click(self, event):
        menus = [(wx.NewId(), _("Copy"), self.copyGrid),
                 (wx.NewId(), _("Paste"), self.pasteGrid),
                 (wx.NewId(), _("Delete"), self.deleteRow)]
        popup_menu = wx.Menu()
        for menu in menus:
            if menu is None:
                popup_menu.AppendSeparator()
                continue
            popup_menu.Append(menu[0], menu[1])
            self.Bind(wx.EVT_MENU, menu[2], id=menu[0])

        self.PopupMenu(popup_menu, event.GetPosition())
        popup_menu.Destroy()

    def deleteRow(self, event):
        self.VariablesGrid.DeleteRow()

    def copyGrid(self, event):
        """
        Copies range of selected cells to clipboard.
        """

        selection = self.VariablesGrid.get_selection()
        if not selection:
            return []
        start_row, start_col, end_row, end_col = selection

        data = u''

        rows = range(start_row, end_row + 1)
        columns = range(start_col, end_col + 1)

        for idx, column in enumerate(columns, 1):
            data += self.VariablesGrid.GetColLabelValue(column)
            if idx == len(columns):
                # if we are at the last cell of the row, add new line instead
                data += "\n"
            else:
                data += "\t"

        for row in rows:
            for idx, column in enumerate(columns, 1):
                if idx == len(columns):
                    # if we are at the last cell of the row, add new line instead
                    data += self.VariablesGrid.GetCellValue(row, column) + "\n"
                else:
                    data += self.VariablesGrid.GetCellValue(row, column) + "\t"

        text_data_object = wx.TextDataObject()
        text_data_object.SetText(data)

        if wx.TheClipboard.Open():
            wx.TheClipboard.SetData(text_data_object)
            wx.TheClipboard.Close()
        else:
            wx.MessageBox("Can't open the clipboard", "Warning")

    def pasteGrid(self, event):

        for col in self.VariablesGrid.selected_cols:
            self.VariablesGrid.InsertCols(col)

        if not wx.TheClipboard.Open():
            wx.MessageBox("Can't open the clipboard", "Warning")
            return False

        clipboard = wx.TextDataObject()
        wx.TheClipboard.GetData(clipboard)
        wx.TheClipboard.Close()
        data = clipboard.GetText()
        KeyNames = []
        KeyName = ""
        listKeyName = ["#",
                    _("Name"),
                    _("Group"),
                    _("Class"),
                    _("Type"),
                    _("Location"),
                    _("Initial Value"),
                    _("Option"),
                    _("Documentation")]

        end_first_row = data.find('\n')
        if end_first_row > 70 or end_first_row < 0:
            return
        for index in range(data.find('\n')):
            if data[index] != "\t":
                KeyName += data[index]
            else:
                if KeyName not in listKeyName:
                    return
                KeyNames.append(KeyName)
                KeyName = ""
        if KeyName != "":
            KeyNames.append(KeyName)

        datatable = []
        _data = data.split("\n")
        for row in _data:
            datatable.append(row.split("\t"))

        TableDict = {}
        for col in range(len(KeyNames)):
            colline = []
            for row in range(1, len(datatable) - 1):
                colline.append(datatable[row][col])
            TableDict[KeyNames[col]] = colline

        for row in range(len(_data) - 2):
            if TableDict.get(_("Name")) is None:
                self.VariablesGrid.AddRow()
            else:
                self.VariablesGrid.AddRow(TableDict[_("Name")][row])
            select_row = self.VariablesGrid.GetGridCursorRow()
            for key in TableDict:
                for col in range(self.VariablesGrid.GetNumberCols()):
                    if key == self.VariablesGrid.GetColLabelValue(col):
                        if key == "#" or key == _("Name"):
                            break
                        elif key == _("Group"):
                            if self.ElementType in ["config", "resource"]:
                                if TableDict[key][row] != self.SelectGroup and self.SelectGroup != (_("All")):
                                    TableDict[key][row] = self.SelectGroup
                        elif key == _("Class"):
                            if self.ElementType in ["config", "resource"]:
                                if TableDict[key][row] != _("Global"):
                                    TableDict[key][row] = _("Global")
                            elif self.ElementType in ["functionBlock", "program"]:
                                if self.NotebookPage == VARIABLEPANEL_GLOBAL:
                                    TableDict[key][row] = _("External")
                                elif self.NotebookPage in [VARIABLEPANEL_LOCAL, VARIABLEPANEL_FB]:
                                    if TableDict[key][row] not in self.FilterChoices:
                                        TableDict[key][row] = _("Local")
                        elif key == _("Type"):
                            if self.ElementType in ["functionBlock", "program"]:
                                if self.NotebookPage == VARIABLEPANEL_FB:
                                    if self.Controler.IsLocatableType(TableDict[key][row]):
                                        TableDict[key][row] = self.Controler.GetFunctionBlockTypes()[0]
                        try:
                            self.VariablesGrid.SetCellValue(select_row, col, TableDict[key][row])
                            break
                        except:
                            print("Table paste Error!")
                            break

    def GetTableFromClipboard(self):
        for col in self.VariablesGrid.selected_cols:
            self.VariablesGrid.InsertCols(col)

        if not wx.TheClipboard.Open():
            wx.MessageBox("Can't open the clipboard", "Warning")
            return False

        clipboard = wx.TextDataObject()
        wx.TheClipboard.GetData(clipboard)
        wx.TheClipboard.Close()
        data = clipboard.GetText()
        KeyNames = []
        KeyName = ""
        listKeyName = [ "",
                        "#",
                       _("Name"),
                       _("Group"),
                       _("Class"),
                       _("Type"),
                       _("Location"),
                       _("Initial Value"),
                       _("Option"),
                       _("Documentation")]

        end_first_row = data.find('\n')
        if end_first_row > 70 or end_first_row < 0:
            return
        for index in range(data.find('\n')):
            if data[index] != "\t":
                KeyName += data[index]
            else:
                if KeyName not in listKeyName:
                    return
                KeyNames.append(KeyName)
                KeyName = ""
        if KeyName != "":
            KeyNames.append(KeyName)
        if len(KeyNames) > 0:
            return KeyNames, data

    def onCtrlC(self, event):
        self.copyGrid(event)

    def onCtrlV(self, event):
        self.pasteGrid(event)

    def NoDataInsertDialog(self):
        dialog = wx.MessageDialog(self, _("No data to insert"), _("Error"), style=wx.OK)
        res = dialog.ShowModal()
        if dialog.IsModal():
            dialog.EndModal(res)
        else:
            dialog.Destroy()

    def CopyProgressDialog(self):
        dialog = wx.ProgressDialog(_("Progress"),
                                   _("Progress") + "...", 100, parent=self,
                                   style=wx.PD_AUTO_HIDE | wx.PD_APP_MODAL | wx.PD_SMOOTH)
        dialog.Pulse()
        return dialog