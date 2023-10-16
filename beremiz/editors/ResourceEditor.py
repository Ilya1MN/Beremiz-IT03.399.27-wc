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

import wx
import wx.lib.buttons
import wx.grid
import wx.lib.scrolledpanel
import re

from graphics.GraphicCommons import REFRESH_HIGHLIGHT_PERIOD, ERROR_HIGHLIGHT
from controls import CustomGrid, CustomTable, DurationCellEditor
from dialogs.DurationEditorDialog import IEC_TIME_MODEL
from .EditorPanel import EditorPanel
from util.BitmapLibrary import GetBitmap
from plcopen.structures import LOCATIONDATATYPES, TestIdentifier, IEC_KEYWORDS, DefaultType
from util.TranslationCatalogs import NoTranslate
from dialogs.BrowseFastTasks import BrowseFastTasks

# -------------------------------------------------------------------------------
#                          Configuration Editor class
# -------------------------------------------------------------------------------


[
    ID_CONFIGURATIONEDITOR,
] = [wx.NewId() for _init_ctrls in range(1)]


class ConfigurationEditor(EditorPanel):

    ID = ID_CONFIGURATIONEDITOR
    VARIABLE_PANEL_TYPE = "config"

    def GetBufferState(self):
        return self.Controler.GetBufferState()

    def Undo(self):
        self.Controler.LoadPrevious()
        self.ParentWindow.CloseTabsWithoutModel()

    def Redo(self):
        self.Controler.LoadNext()
        self.ParentWindow.CloseTabsWithoutModel()

    def HasNoModel(self):
        return self.Controler.GetEditedElement(self.TagName) is None


# -------------------------------------------------------------------------------
#                            Resource Editor class
# -------------------------------------------------------------------------------

def GetTasksTableColnames():
    _ = NoTranslate
    return [_("Name"), _("Triggering"), _("Single"), _("Interval"), _("Priority")]


def GetTaskTriggeringOptions():
    _ = NoTranslate
    return [_("Interrupt"), _("Cyclic")]


TASKTRIGGERINGOPTIONS_DICT = dict([(_(option), option) for option in GetTaskTriggeringOptions()])


def SingleCellEditor(*x):
    return wx.grid.GridCellChoiceEditor([])


def CheckSingle(single, varlist):
    return single in varlist


def GetInstancesTableColnames():
    _ = NoTranslate
    return [_("Name"), _("Type"), _("Task")]


class ResourceTable(CustomTable):

    """
    A custom wx.grid.Grid Table using user supplied data
    """
    def __init__(self, parent, data, colnames):
        # The base class must be initialized *first*
        CustomTable.__init__(self, parent, data, colnames)
        self.ColAlignements = []
        self.ColSizes = []

    def GetColAlignements(self):
        return self.ColAlignements

    def SetColAlignements(self, list):
        self.ColAlignements = list

    def GetColSizes(self):
        return self.ColSizes

    def SetColSizes(self, list):
        self.ColSizes = list

    def GetValue(self, row, col):
        if row < self.GetNumberRows():
            colname = self.GetColLabelValue(col, False)
            value = self.data[row].get(colname, "")
            if colname == "Triggering":
                return _(value)
            return value

    def SetValue(self, row, col, value):
        if col < len(self.colnames):
            colname = self.GetColLabelValue(col, False)
            if colname == "Triggering":
                value = TASKTRIGGERINGOPTIONS_DICT[value]
            self.data[row][colname] = value

    def _updateColAttrs(self, grid):
        """
        wx.grid.Grid -> update the column attributes to add the
        appropriate renderer given the column name.

        Otherwise default to the default renderer.
        """

        for col in range(self.GetNumberCols()):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(self.ColAlignements[col], wx.ALIGN_CENTRE)
            grid.SetColAttr(col, attr)
            grid.SetColSize(col, self.ColSizes[col])

        for row in range(self.GetNumberRows()):
            row_highlights = self.Highlights.get(row, {})
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                error = False
                colname = self.GetColLabelValue(col, False)
                grid.SetReadOnly(row, col, False)
                if colname == "Name":
                    editor = wx.grid.GridCellTextEditor()
                    renderer = wx.grid.GridCellStringRenderer()
                elif colname == "Interval":
                    editor = DurationCellEditor(self, colname)
                    renderer = wx.grid.GridCellStringRenderer()
                    if self.GetValueByName(row, "Triggering") != "Cyclic":
                        grid.SetReadOnly(row, col, True)
                    interval = self.GetValueByName(row, colname)
                    if interval != "" and IEC_TIME_MODEL.match(interval.upper()) is None:
                        error = True
                elif colname == "Single":
                    editor = SingleCellEditor(self, colname)
                    editor.SetParameters(self.Parent.VariableList)
                    if self.GetValueByName(row, "Triggering") != "Interrupt":
                        grid.SetReadOnly(row, col, True)
                    single = self.GetValueByName(row, colname)
                    if single != "" and not CheckSingle(single, self.Parent.VariableList):
                        error = True
                elif colname == "Triggering":
                    editor = wx.grid.GridCellChoiceEditor([])
                    editor.SetParameters(",".join(map(_, GetTaskTriggeringOptions())))
                elif colname == "Type":
                    editor = wx.grid.GridCellChoiceEditor([])
                    editor.SetParameters(self.Parent.TypeList)
                elif colname == "Priority":
                    editor = wx.grid.GridCellNumberEditor()
                    editor.SetParameters("0,65535")
                elif colname == "Task":
                    editor = wx.grid.GridCellChoiceEditor([])
                    editor.SetParameters(self.Parent.TaskList)

                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)

                if error:
                    highlight_colours = ERROR_HIGHLIGHT
                else:
                    highlight_colours = row_highlights.get(colname.lower(), [(wx.WHITE, wx.BLACK)])[-1]
                grid.SetCellBackgroundColour(row, col, highlight_colours[0])
                grid.SetCellTextColour(row, col, highlight_colours[1])
            self.ResizeRow(grid, row)

    # -------------------------------------------------------------------------------
    #                        Highlights showing functions
    # -------------------------------------------------------------------------------

    def AddHighlight(self, infos, highlight_type):
        row_highlights = self.Highlights.setdefault(infos[0], {})
        col_highlights = row_highlights.setdefault(infos[1], [])
        col_highlights.append(highlight_type)

    def ClearHighlights(self, highlight_type=None):
        if highlight_type is None:
            self.Highlights = {}
        else:
            for row, row_highlights in self.Highlights.items():
                row_items = list(row_highlights.items())
                for col, col_highlights in row_items:
                    if highlight_type in col_highlights:
                        col_highlights.remove(highlight_type)
                    if len(col_highlights) == 0:
                        row_highlights.pop(col)


# -------------------------------------------------------------------------------
#                            Fast task table class
# -------------------------------------------------------------------------------

def GetFastTasksTableColnames():
    _ = NoTranslate
    return [_("Name"), _("Mode"), _("Event"), _("Priority")]


def GetFastTaskTriggeringOptions():
    _ = NoTranslate
    return [_("Interrupt"), _("Cyclic")]


FASTTASKTRIGGERINGOPTIONS_DICT = dict([(_(option), option) for option in GetFastTaskTriggeringOptions()])

class FastTaskTable(CustomTable):

    """
    A custom wx.grid.Grid Table using user supplied data
    """
    def __init__(self, parent, data, colnames):
        # The base class must be initialized *first*
        CustomTable.__init__(self, parent, data, colnames)
        self.ColAlignements = []
        self.ColSizes = []
        self.InfosDict = parent.InputInterfaceDict
        self.MaxValue = ""
        self.MinValue = ""

    def GetSource(self):
        return self.InfosDict.keys()

    def GetModes(self, source):
        res = self.InfosDict.get(source, list())
        if isinstance(res, dict):
            return res.keys()
        elif isinstance(res, list):
            if len(res) > 1:
                return [res_list["name_mode"] for res_list in res]
            return list()

    def GetLimitVar(self, source, mode_name):
        max_limit = 0
        min_limit = 0
        if source == "":
            return "", ""
        values_limits = self.InfosDict.get(source, list())
        if len(values_limits) == 1:
            value_dict = values_limits[0]
            try:
                max_limit = int(value_dict['max'])
                min_limit = int(value_dict['min'])
            except ValueError:
                return value_dict['max'], value_dict['min']
        else:
            for mode_infos in values_limits:
                if mode_infos['name_mode'] == mode_name:
                    if len(mode_infos["Children"]) == 1:
                        value_infos = mode_infos["Children"][0].get("variable", False)
                        if value_infos:
                            try:
                                max_limit = int(value_infos['max'])
                                min_limit = int(value_infos['min'])
                            except ValueError:
                                return value_infos['max'], value_infos['min']
                    break
        return [max_limit, min_limit]

    def GetColAlignements(self):
        return self.ColAlignements

    def SetColAlignements(self, list):
        self.ColAlignements = list

    def GetColSizes(self):
        return self.ColSizes

    def SetColSizes(self, list):
        self.ColSizes = list

    def GetValue(self, row, col):
        if row < self.GetNumberRows():
            colname = self.GetColLabelValue(col, False)
            value = self.data[row].get(colname, "")
            if colname == "Triggering":
                return _(value)
            return value

    def SetValue(self, row, col, value):
        if col < len(self.colnames):
            colname = self.GetColLabelValue(col, False)
            if colname == "Triggering":
                value = FASTTASKTRIGGERINGOPTIONS_DICT[value]
            self.data[row][colname] = value

    def _updateColAttrs(self, grid):
        """
        wx.grid.Grid -> update the column attributes to add the
        appropriate renderer given the column name.

        Otherwise default to the default renderer.
        """

        for col in range(self.GetNumberCols()):
            attr = wx.grid.GridCellAttr()
            attr.SetAlignment(self.ColAlignements[col], wx.ALIGN_CENTRE)
            grid.SetColAttr(col, attr)
            grid.SetColSize(col, self.ColSizes[col])

        for row in range(self.GetNumberRows()):
            row_highlights = self.Highlights.get(row, {})
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                error = False
                colname = self.GetColLabelValue(col, False)
                grid.SetReadOnly(row, col, False)
                if colname == "Name":
                    editor = wx.grid.GridCellChoiceEditor([])
                    used_type = [_type[colname] for _type in self.GetData()
                                 if _type[colname] is not self.GetValueByName(row, colname)]
                    type_list = [_type for _type in self.Parent.TypeList.split(",")[1:] if _type not in used_type]
                    editor.SetParameters(",".join(type_list))
                elif colname == "Source":
                    editor = wx.grid.GridCellChoiceEditor([])
                    editor.SetParameters(",".join(self.GetSource()))
                elif colname == "Mode":
                    editor = grid.SetReadOnly(row, col, True)
                elif colname == "Event":
                    grid.SetReadOnly(row, col, True)
                    pass
                elif colname == "Value":
                    min_max_value = self.GetLimitVar(source=self.GetValueByName(row, "Source"),
                                                            mode_name=self.GetValueByName(row, "Mode"))
                    if isinstance(min_max_value[0], str):
                        self.SetValueByName(row, colname, min_max_value[0])
                        grid.SetReadOnly(row, col, True)
                    else:
                        min_max_value.sort()
                        editor = wx.grid.GridCellNumberEditor()
                        limit_str = ("%d,%d") % (min_max_value[0], min_max_value[1])
                        editor.SetParameters(limit_str)
                elif colname == "Priority":
                    self.SetValueByName(row, colname, row)
                    grid.SetReadOnly(row, col, True)
                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)

                if error:
                    highlight_colours = ERROR_HIGHLIGHT
                else:
                    highlight_colours = row_highlights.get(colname.lower(), [(wx.WHITE, wx.BLACK)])[-1]
                grid.SetCellBackgroundColour(row, col, highlight_colours[0])
                grid.SetCellTextColour(row, col, highlight_colours[1])
            self.ResizeRow(grid, row)

    # -------------------------------------------------------------------------------
    #                        Highlights showing functions
    # -------------------------------------------------------------------------------

    def AddHighlight(self, infos, highlight_type):
        row_highlights = self.Highlights.setdefault(infos[0], {})
        col_highlights = row_highlights.setdefault(infos[1], [])
        col_highlights.append(highlight_type)

    def ClearHighlights(self, highlight_type=None):
        if highlight_type is None:
            self.Highlights = {}
        else:
            for row, row_highlights in self.Highlights.items():
                row_items = list(row_highlights.items())
                for col, col_highlights in row_items:
                    if highlight_type in col_highlights:
                        col_highlights.remove(highlight_type)
                    if len(col_highlights) == 0:
                        row_highlights.pop(col)

class ResourceEditor(EditorPanel):

    VARIABLE_PANEL_TYPE = "resource"

    def _init_Editor(self, parent):
        self.Editor = wx.Panel(parent, style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL | wx.HSCROLL)

        main_sizer = wx.GridBagSizer(hgap=5, vgap=5)

        tasks_sizer = wx.FlexGridSizer(cols=1, hgap=0, rows=2, vgap=5)
        tasks_sizer.AddGrowableCol(0)
        tasks_sizer.AddGrowableRow(1)

        main_sizer.Add(tasks_sizer, pos=(0, 0), flag=wx.EXPAND)

        fast_tasks_sizer = wx.FlexGridSizer(cols=1, hgap=0, rows=2, vgap=5)
        fast_tasks_sizer.AddGrowableCol(0)
        fast_tasks_sizer.AddGrowableRow(1)
        main_sizer.Add(fast_tasks_sizer, pos=(0, 1), span=(2, 1), flag=wx.EXPAND)

        fast_tasks_button_sizer = wx.FlexGridSizer(cols=5, hgap=5, rows=1, vgap=0)
        fast_tasks_button_sizer.AddGrowableCol(0)
        fast_tasks_button_sizer.AddGrowableRow(0)
        fast_tasks_sizer.Add(fast_tasks_button_sizer, flag=wx.GROW)
        fast_tasks_label = wx.StaticText(self.Editor, label=_('Tasks by event:'))
        fast_tasks_button_sizer.Add(fast_tasks_label, flag=wx.ALIGN_BOTTOM)
        for name, bitmap, help in [
            ("AddFastTaskButton", "add_element", _("Add fast task")),
            ("DeleteFastTaskButton", "remove_element", _("Remove fast task")),
            ("UpFastTaskButton", "up", _("Move fast task up")),
            ("DownFastTaskButton", "down", _("Move fast task down"))]:
            button = wx.lib.buttons.GenBitmapButton(self.Editor,
                                                    bitmap=GetBitmap(bitmap),
                                                    size=wx.Size(28, 28),
                                                    style=wx.NO_BORDER)
            button.SetToolTip(help)
            setattr(self, name, button)
            fast_tasks_button_sizer.Add(button)

        tasks_buttons_sizer = wx.FlexGridSizer(cols=5, hgap=5, rows=1, vgap=0)
        tasks_buttons_sizer.AddGrowableCol(0)
        tasks_buttons_sizer.AddGrowableRow(0)
        tasks_sizer.Add(tasks_buttons_sizer, flag=wx.GROW)

        tasks_label = wx.StaticText(self.Editor, label=_('Tasks:'))
        tasks_buttons_sizer.Add(tasks_label, flag=wx.ALIGN_BOTTOM)

        for name, bitmap, help in [
                ("AddTaskButton", "add_element", _("Add task")),
                ("DeleteTaskButton", "remove_element", _("Remove task")),
                ("UpTaskButton", "up", _("Move task up")),
                ("DownTaskButton", "down", _("Move task down"))]:
            button = wx.lib.buttons.GenBitmapButton(self.Editor,
                                                    bitmap=GetBitmap(bitmap),
                                                    size=wx.Size(28, 28),
                                                    style=wx.NO_BORDER)
            button.SetToolTip(help)
            setattr(self, name, button)
            tasks_buttons_sizer.Add(button)

        self.TasksGrid = CustomGrid(self.Editor, style=wx.VSCROLL)
        self.TasksGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnTasksGridCellChange)
        tasks_sizer.Add(self.TasksGrid, flag=wx.EXPAND)

        self.FastTasksGrid = CustomGrid(self.Editor, style=wx.VSCROLL)
        self.FastTasksGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnFastTasksGridCellChange)
        self.FastTasksGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_DCLICK, self.OnCellLeftDClick)
        fast_tasks_sizer.Add(self.FastTasksGrid, flag=wx.EXPAND)#, flag=wx.GROW)

        instances_sizer = wx.FlexGridSizer(cols=1, hgap=0, rows=2, vgap=5)
        instances_sizer.AddGrowableCol(0)
        instances_sizer.AddGrowableRow(1)
        main_sizer.Add(instances_sizer, pos=(1, 0), flag=wx.EXPAND)
        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableCol(1)
        main_sizer.AddGrowableRow(0)
        main_sizer.AddGrowableRow(1)
        instances_buttons_sizer = wx.FlexGridSizer(cols=5, hgap=5, rows=1, vgap=0)
        instances_buttons_sizer.AddGrowableCol(0)
        instances_buttons_sizer.AddGrowableRow(0)
        instances_sizer.Add(instances_buttons_sizer, flag=wx.GROW)

        instances_label = wx.StaticText(self.Editor, label=_('Instances:'))
        instances_buttons_sizer.Add(instances_label, flag=wx.ALIGN_BOTTOM)

        for name, bitmap, help in [
                ("AddInstanceButton", "add_element", _("Add instance")),
                ("DeleteInstanceButton", "remove_element", _("Remove instance")),
                ("UpInstanceButton", "up", _("Move instance up")),
                ("DownInstanceButton", "down", _("Move instance down"))]:
            button = wx.lib.buttons.GenBitmapButton(
                self.Editor, bitmap=GetBitmap(bitmap),
                size=wx.Size(28, 28), style=wx.NO_BORDER)
            button.SetToolTip(help)
            setattr(self, name, button)
            instances_buttons_sizer.Add(button)

        self.InstancesGrid = CustomGrid(self.Editor, style=wx.VSCROLL)
        self.InstancesGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnInstancesGridCellChange)
        instances_sizer.Add(self.InstancesGrid, flag=wx.GROW)

        self.Editor.SetSizer(main_sizer)
        #self.Editor.SetSizer(MainSizer)

    def __init__(self, parent, tagname, window, controler):
        EditorPanel.__init__(self, parent, tagname, window, controler)
        self.InputInterfaceDict = dict()
        self.SetInputInterfaceList()

        self.RefreshHighlightsTimer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnRefreshHighlightsTimer, self.RefreshHighlightsTimer)

        self.TasksDefaultValue = {"Name": "", "Triggering": "", "Single": "", "Interval": "", "Priority": 0}
        self.TasksTable = ResourceTable(self, [], GetTasksTableColnames())
        self.TasksTable.SetColAlignements([wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT])
        self.TasksTable.SetColSizes([200, 100, 100, 100, 100])
        self.TasksGrid.SetTable(self.TasksTable)

        self.TasksGrid.SetButtons({"Add": self.AddTaskButton,
                                   "Delete": self.DeleteTaskButton,
                                   "Up": self.UpTaskButton,
                                   "Down": self.DownTaskButton})

        self.FastTaskDefaultValue = {"Name": "", "Mode": "", "Event": "", "Priority": "0"}
        self.FastTaskTable = FastTaskTable(self, [], GetFastTasksTableColnames())
        self.FastTaskTable.SetColAlignements([wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT])
        self.FastTaskTable.SetColSizes([100, 100, 400, 100])
        self.FastTasksGrid.SetTable(self.FastTaskTable)

        self.FastTasksGrid.SetButtons({"Add": self.AddFastTaskButton,
                                       "Delete": self.DeleteFastTaskButton,
                                       "Up": self.UpFastTaskButton,
                                       "Down": self.DownFastTaskButton})

        def _AddTask(new_row, name=None, type=None, Save=True):
            self.TasksTable.InsertRow(new_row, self.TasksDefaultValue.copy())
            self.RefreshModel()
            return new_row
        setattr(self.TasksGrid, "_AddRow", _AddTask)

        def _DeleteTask(row):
            self.TasksTable.RemoveRow(row)
            self.RefreshModel()
            self.RefreshView()
        setattr(self.TasksGrid, "_DeleteRow", _DeleteTask)

        def _MoveTask(row, move):
            new_row = self.TasksTable.MoveRow(row, move)
            if new_row != row:
                self.RefreshModel()
                self.RefreshView()
            return new_row
        setattr(self.TasksGrid, "_MoveRow", _MoveTask)

        def _AddFastTask(new_row, name=None, type=None, Save=True):
            self.FastTaskTable.InsertRow(new_row, self.FastTaskDefaultValue.copy())
            self.RefreshFastTask()
            self.RefreshView()
            return new_row
        setattr(self.FastTasksGrid, "_AddRow", _AddFastTask)

        def _DeleteFastTask(row):
            self.FastTaskTable.RemoveRow(row)
            self.RefreshFastTask()
            self.RefreshView()
        setattr(self.FastTasksGrid, "_DeleteRow", _DeleteFastTask)

        def _MoveFastTask(row, move):
            new_row = self.FastTaskTable.MoveRow(row, move)
            if new_row != row:
                self.RefreshFastTask()
                self.RefreshView()
            return new_row
        setattr(self.FastTasksGrid, "_MoveRow", _MoveFastTask)

        self.FastTasksGrid.SetRowLabelSize(0)
        self.FastTaskTable.ResetView(self.FastTasksGrid)
        self.FastTasksGrid.RefreshButtons()

        self.TasksGrid.SetRowLabelSize(0)
        self.TasksTable.ResetView(self.TasksGrid)
        self.TasksGrid.RefreshButtons()

        self.InstancesDefaultValue = {"Name": "", "Type": "", "Task": ""}
        self.InstancesTable = ResourceTable(self, [], GetInstancesTableColnames())
        self.InstancesTable.SetColAlignements([wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT])
        self.InstancesTable.SetColSizes([200, 150, 150])
        self.InstancesGrid.SetTable(self.InstancesTable)
        self.InstancesGrid.SetButtons({"Add": self.AddInstanceButton,
                                       "Delete": self.DeleteInstanceButton,
                                       "Up": self.UpInstanceButton,
                                       "Down": self.DownInstanceButton})

        def _AddInstance(new_row, name=None, type=None, Save=True):
            self.InstancesTable.InsertRow(new_row, self.InstancesDefaultValue.copy())
            self.RefreshModel()
            self.RefreshView()
            return new_row
        setattr(self.InstancesGrid, "_AddRow", _AddInstance)

        def _DeleteInstance(row):
            self.InstancesTable.RemoveRow(row)
            self.RefreshModel()
            self.RefreshView()
            self.ParentWindow.RefreshPouInstanceVariablesPanel()
        setattr(self.InstancesGrid, "_DeleteRow", _DeleteInstance)

        def _MoveInstance(row, move):
            new_row = max(0, min(row + move, self.InstancesTable.GetNumberRows() - 1))
            if new_row != row:
                if self.InstancesTable.GetValueByName(row, "Task") != self.InstancesTable.GetValueByName(new_row, "Task"):
                    return row
                self.InstancesTable.MoveRow(row, move)
                self.RefreshModel()
                self.RefreshView()
            return new_row
        setattr(self.InstancesGrid, "_MoveRow", _MoveInstance)

        def _RefreshInstanceButtons():
            if self:
                rows = self.InstancesTable.GetNumberRows()
                row = self.InstancesGrid.GetGridCursorRow()
                self.DeleteInstanceButton.Enable(rows > 0)
                self.UpInstanceButton.Enable(
                    row > 0 and
                    self.InstancesTable.GetValueByName(row, "Task") == self.InstancesTable.GetValueByName(row - 1, "Task"))
                self.DownInstanceButton.Enable(
                    0 <= row < rows - 1 and
                    self.InstancesTable.GetValueByName(row, "Task") == self.InstancesTable.GetValueByName(row + 1, "Task"))
        setattr(self.InstancesGrid, "RefreshButtons", _RefreshInstanceButtons)

        self.InstancesGrid.SetRowLabelSize(0)
        self.InstancesTable.ResetView(self.InstancesGrid)
        self.InstancesGrid.RefreshButtons()

        self.TasksGrid.SetFocus()

    def __del__(self):
        self.RefreshHighlightsTimer.Stop()

    def RefreshTypeList(self):
        self.TypeList = ""
        blocktypes = self.Controler.GetBlockResource()
        for blocktype in blocktypes:
            self.TypeList += ",%s" % blocktype

    def RefreshTaskList(self):
        self.TaskList = ""
        for row in range(self.TasksTable.GetNumberRows()):
            self.TaskList += ",%s" % self.TasksTable.GetValueByName(row, "Name")

    def RefreshVariableList(self):
        self.VariableList = ""
        for variable in self.Controler.GetEditedResourceVariables(self.TagName):
            self.VariableList += ",%s" % variable

    def RefreshModel(self):
        self.Controler.SetEditedResourceInfos(self.TagName, self.TasksTable.GetData(), self.InstancesTable.GetData())
        #24.04.2023
        #self.Controler.SetEditedFastTask(self.TagName, self.FastTaskTable.GetData())
        self.RefreshBuffer()

    def RefreshFastTask(self):
        self.Controler.SetEditedFastTask(self.TagName, self.FastTaskTable.GetData())
        self.RefreshBuffer()
        #self.FastTaskTable.ResizeRow(self.FastTasksGrid, -1)

    # Buffer the last model state
    def RefreshBuffer(self):
        self.Controler.BufferProject()
        self.ParentWindow.RefreshTitle()
        self.ParentWindow.RefreshFileMenu()
        self.ParentWindow.RefreshEditMenu()

    def GetBufferState(self):
        return self.Controler.GetBufferState()

    def Undo(self):
        self.Controler.LoadPrevious()
        self.ParentWindow.CloseTabsWithoutModel()

    def Redo(self):
        self.Controler.LoadNext()
        self.ParentWindow.CloseTabsWithoutModel()

    def HasNoModel(self):
        return self.Controler.GetEditedElement(self.TagName) is None

    def RefreshView(self, variablepanel=True):
        EditorPanel.RefreshView(self, variablepanel)

        tasks, instances = self.Controler.GetEditedResourceInfos(self.TagName)
        self.FastTaskTable.SetData(self.Controler.GetEditedFastTask(self.TagName))

        self.TasksTable.SetData(tasks)
        self.InstancesTable.SetData(instances)
        self.RefreshTypeList()
        self.RefreshTaskList()
        self.RefreshVariableList()
        self.TasksTable.ResetView(self.TasksGrid)
        self.FastTaskTable.ResetView(self.FastTasksGrid)
        self.FastTasksGrid.AutoSizeRows()
        self.InstancesTable.ResetView(self.InstancesGrid)
        self.TasksGrid.RefreshButtons()
        self.FastTasksGrid.RefreshButtons()
        self.InstancesGrid.RefreshButtons()

    def FastTaskRefreshView(self, variablepanel=True):
        EditorPanel.RefreshView(self, variablepanel)
        self.FastTaskTable.SetData(self.Controler.GetEditedFastTask(self.TagName))
        self.RefreshTypeList()
        self.RefreshTaskList()
        self.RefreshVariableList()
        self.FastTaskTable.ResetView(self.FastTasksGrid)
        self.FastTasksGrid.AutoSizeRows()
        self.FastTasksGrid.RefreshButtons()

    def ShowErrorMessage(self, message):
        dialog = wx.MessageDialog(self, message, _("Error"), wx.OK | wx.ICON_ERROR)
        dialog.ShowModal()
        dialog.Destroy()

    def OnTasksGridCellChange(self, event):
        row, col = event.GetRow(), event.GetCol()
        if self.TasksTable.GetColLabelValue(col, False) == "Name":
            value = self.TasksTable.GetValue(row, col)
            message = None

            if not TestIdentifier(value):
                message = _("\"%s\" is not a valid identifier!") % value
            elif value.upper() in IEC_KEYWORDS:
                message = _("\"%s\" is a keyword. It can't be used!") % value
            elif value.upper() in [var["Name"].upper() for i, var in enumerate(self.TasksTable.data) if i != row]:
                message = _("A task with the same name already exists!")
            if message is not None:
                event.Veto()
                wx.CallAfter(self.ShowErrorMessage, message)
                return

            tasklist = [name for name in self.TaskList.split(",") if name != ""]
            for i in range(self.TasksTable.GetNumberRows()):
                task = self.TasksTable.GetValueByName(i, "Name")
                if task in tasklist:
                    tasklist.remove(task)
            if len(tasklist) > 0:
                old_name = tasklist[0].upper()
                new_name = self.TasksTable.GetValue(row, col)
                for i in range(self.InstancesTable.GetNumberRows()):
                    name = self.InstancesTable.GetValueByName(i, "Task").upper()
                    if old_name == name:
                        self.InstancesTable.SetValueByName(i, "Task", new_name)
        self.RefreshModel()
        colname = self.TasksTable.GetColLabelValue(col, False)
        if colname in ["Triggering", "Name", "Single", "Interval"]:
            wx.CallAfter(self.RefreshView, False)
        event.Skip()

    def OnFastTasksGridCellChange(self, event):
        row, col = event.GetRow(), event.GetCol()
        self.RefreshFastTask()
        colname = self.FastTaskTable.GetColLabelValue(col, False)
        if colname == "Name":
            wx.CallAfter(self.FastTaskRefreshView, False)
        event.Skip()

    def OnCellLeftDClick(self, event):
        row, col = event.GetRow(), event.GetCol()
        colname = self.FastTaskTable.GetColLabelValue(col, False)
        prog_name = self.FastTaskTable.GetValueByName(row, "Name")
        events_cell = None
        if colname in ["Event", "Mode"]:
            dialog = BrowseFastTasks(self, self.TagName, self.Controler, self.Controler.GetEditedFastTaskByName(self.TagName, prog_name), prog_name)
            events_cell = dialog.GetFastTaskData()
            if dialog.ShowModal() == wx.ID_OK and events_cell is not None:
                text = "\n".join([("%(Source)s %(Condition)s %(Value)s") %
                                {"Source": event_cell["Source"], "Condition": event_cell["Condition"],
                                 "Value": event_cell["Value"]} for event_cell in events_cell])
                self.FastTaskTable.SetValueByName(row, "Event", text)
                text = "\n".join([("%(Mode)s") %
                       {"Mode": event_cell["Mode"]
                       if event_cell["Mode"] != "" else " "}
                       for event_cell in events_cell])
                self.FastTaskTable.SetValueByName(row, "Mode", text)
                self.RefreshFastTask()
                self.Refresh()
                wx.CallAfter(self.FastTaskRefreshView, False)
                wx.CallAfter(self.RefreshView, False)
            else:
                infos = None
            dialog.Destroy()

        event.Skip()

    def OnInstancesGridCellChange(self, event):
        row, col = event.GetRow(), event.GetCol()
        if self.InstancesTable.GetColLabelValue(col, False) == "Name":
            value = self.InstancesTable.GetValue(row, col)
            message = None

            if not TestIdentifier(value):
                message = _("\"%s\" is not a valid identifier!") % value
            elif value.upper() in IEC_KEYWORDS:
                message = _("\"%s\" is a keyword. It can't be used!") % value
            elif value.upper() in [var["Name"].upper() for i, var in enumerate(self.InstancesTable.data) if i != row]:
                message = _("An instance with the same name already exists!")
            if message is not None:
                event.Veto()
                wx.CallAfter(self.ShowErrorMessage, message)
                return

        self.RefreshModel()
        self.ParentWindow.RefreshPouInstanceVariablesPanel()
        self.InstancesGrid.RefreshButtons()
        event.Skip()

    # -------------------------------------------------------------------------------
    #                        Highlights showing functions
    # -------------------------------------------------------------------------------

    def OnRefreshHighlightsTimer(self, event):
        self.RefreshView()
        event.Skip()

    def AddHighlight(self, infos, start, end, highlight_type):
        EditorPanel.AddHighlight(self, infos, start, end, highlight_type)

        if infos[0] == "task":
            self.TasksTable.AddHighlight(infos[1:], highlight_type)
        elif infos[0] == "instance":
            self.InstancesTable.AddHighlight(infos[1:], highlight_type)
        self.RefreshHighlightsTimer.Start(int(REFRESH_HIGHLIGHT_PERIOD * 1000), oneShot=True)

    def ClearHighlights(self, highlight_type=None):
        EditorPanel.ClearHighlights(self, highlight_type)

        self.TasksTable.ClearHighlights(highlight_type)
        self.InstancesTable.ClearHighlights(highlight_type)
        self.TasksTable.ResetView(self.TasksGrid)
        self.InstancesTable.ResetView(self.InstancesGrid)

    def SetInputInterfaceList(self):

        if self.Controler.InputInterfaceInfos is not None:
            for interface in self.Controler.InputInterfaceInfos:
                for key in interface.keys():
                    if key == "interface":
                        self.InputInterfaceDict[interface[key]["name"], interface[key]["Channel"]] = \
                            [ch.get("mode", False) if ch.get("mode", False)
                            else ch.get("variable",False)
                            for ch in interface[key]['Children']]



    def GetInputInterfaces(self):
        return self.InputInterfaceDict.keys()

    def GetInputInterfacesMode(self, interface_name):
        return self.InputInterfaceDict[interface_name]