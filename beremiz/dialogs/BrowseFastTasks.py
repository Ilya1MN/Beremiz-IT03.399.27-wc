#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of Beremiz, a Integrated Development Environment for
# programming IEC 61131-3 automates supporting plcopen standard and CanFestival.
#
# Copyright (C) 2007: Edouard TISSERANT and Laurent BESSARD
# Copyright (C) 2017: Andrey Skvortsov <andrej.skvortzov@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.#

from editors import EditorPanel

import wx
import wx.lib.buttons
import wx.grid
import wx.lib.scrolledpanel
import re


from controls import CustomGrid, CustomTable
from util.BitmapLibrary import GetBitmap
from util.TranslationCatalogs import NoTranslate

CHOICE_CONDITION_LIST = [">", "<", "="]

def GetFastTaskTriggeringOptions():
    _ = NoTranslate
    return [_("Interrupt"), _("Cyclic")]

FASTTASKTRIGGERINGOPTIONS_DICT = dict([(_(option), option) for option in GetFastTaskTriggeringOptions()])

def GetFastTasksEventsTableColnames():
    _ = NoTranslate
    return [_("Source"), _("Mode"), _("Condition"), _("Value")]

class FastTaskTable(CustomTable):

    """
    A custom wx.grid.Grid Table using user supplied data
    """
    def __init__(self, parent, data, colnames):
        # The base class must be initialized *first*
        CustomTable.__init__(self, parent, data, colnames)
        self.ColAlignements = []
        self.ColSizes = []
        self.Parent = parent
        self.InfosDict = parent.InputInterfaceDict
        self.MaxValue = ""
        self.MinValue = ""


    def GetSource(self):
        sources = [key[0] for key in self.InfosDict.keys()]
        return sources

    def GetModes(self, source):
        if source == "":
            return []
        source = re.search(r'\D+', source)
        for key in self.InfosDict.keys():
            if source[0] in key:
                res = self.InfosDict.get(key, [])
                if isinstance(res, dict):
                    return res.keys()
                elif isinstance(res, list):
                    if len(res) > 1:
                        return [res_list["name_mode"] for res_list in res]
                    return []

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
            return value

    def SetValue(self, row, col, value):
        if col < len(self.colnames):
            colname = self.GetColLabelValue(col, False)
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
            min_max_value, type_value = self.Parent.GetLimitVar(source=self.GetValueByName(row, "Source"),
                                                                mode_name=self.GetValueByName(row, "Mode"))
            modes = self.GetModes(self.GetValueByName(row, "Source"))
            for col in range(self.GetNumberCols()):
                editor = None
                renderer = None
                colname = self.GetColLabelValue(col, False)
                if colname == "Mode":
                    if len(modes) > 0:
                        grid.SetReadOnly(row, col, False)
                        editor = wx.grid.GridCellChoiceEditor([])
                        editor.SetParameters(",".join(modes))
                    else:
                        self.SetValueByName(row, colname, "")
                        grid.SetReadOnly(row, col, True)
                elif colname == "Condition":
                    if type_value in ["BOOL", "str"]:
                        choise_list = ["="]
                        condition_cell_value = self.GetValueByName(row, colname)
                        if condition_cell_value not in choise_list:
                            self.SetValueByName(row, colname, choise_list[0])
                        editor = wx.grid.GridCellChoiceEditor(choise_list)

                    elif type_value in ["REAL", "LREAL"]:
                        choise_list = [">", "<"]
                        condition_cell_value = self.GetValueByName(row, colname)
                        if condition_cell_value not in choise_list:
                            self.SetValueByName(row, colname, choise_list[0])
                        editor = wx.grid.GridCellChoiceEditor(choise_list)
                    else:
                        choise_list = [">", "<", "="]
                        condition_cell_value = self.GetValueByName(row, colname)
                        if condition_cell_value not in choise_list:
                            self.SetValueByName(row, colname, choise_list[0])
                        editor = wx.grid.GridCellChoiceEditor([">", "<", "="])
                elif colname == "Value":
                    if type_value in ["str"]:
                        if len(min_max_value) == 2:
                            if min_max_value[0] != min_max_value[1]:
                                grid.SetReadOnly(row, col, False)
                                editor = wx.grid.GridCellChoiceEditor([_(min_max_value[0]), _(min_max_value[1])])
                                self.SetValueByName(row, colname, _(min_max_value[0]))
                            else:
                                try:
                                    self.SetValueByName(row, colname, _(min_max_value[0]))
                                    grid.SetReadOnly(row, col, True)
                                except:
                                    pass
                        else:
                            grid.SetReadOnly(row, col, True)
                    else:
                        min_max_value.sort()
                        if grid.IsReadOnly(row, col):
                            self.SetValueByName(row, colname, min_max_value[0])
                            grid.SetReadOnly(row, col, False)
                        if type_value in ["REAL", "LREAL"]:
                            editor = wx.grid.GridCellFloatEditor(precision=1)
                        elif type_value == "str":
                            editor = wx.grid.GridCellChoiceEditor([_("Front"), _("Falling")])
                        else:
                            editor = wx.grid.GridCellNumberEditor()
                            limit_str = ("%d,%d") % (min_max_value[0], min_max_value[1])
                            editor.SetParameters(limit_str)
                grid.SetCellEditor(row, col, editor)
                grid.SetCellRenderer(row, col, renderer)

            self.ResizeRow(grid, row)

class BrowseFastTasks(wx.Dialog):
    def __init__(self, parent, tagname, controler, data, program_name):
        wx.Dialog.__init__(self, parent, title=_('Source selection'),
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self.SetSize(450, 300)

        main_sizer = wx.FlexGridSizer(cols=1, hgap=5, rows=2, vgap=5)
        main_sizer.AddGrowableCol(0)
        main_sizer.AddGrowableRow(0)
        fast_tasks_sizer = wx.FlexGridSizer(cols=1, hgap=5, rows=2, vgap=5)
        fast_tasks_sizer.AddGrowableCol(0)
        fast_tasks_sizer.AddGrowableRow(1)
        main_sizer.Add(fast_tasks_sizer, flag=wx.GROW)

        fast_tasks_button_sizer = wx.FlexGridSizer(cols=5, hgap=5, rows=1, vgap=0)
        fast_tasks_button_sizer.AddGrowableCol(0)
        fast_tasks_button_sizer.AddGrowableRow(0)
        fast_tasks_sizer.Add(fast_tasks_button_sizer, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.GROW)
        fast_tasks_label = wx.StaticText(self, label=_('Tasks by event:'))
        fast_tasks_button_sizer.Add(fast_tasks_label, flag=wx.ALIGN_BOTTOM)
        for name, bitmap, help in [
            ("AddFastTaskButton", "add_element", _("Add task")),
            ("DeleteFastTaskButton", "remove_element", _("Remove task")),
            ("UpFastTaskButton", "up", _("Move task up")),
            ("DownFastTaskButton", "down", _("Move task down"))]:
            button = wx.lib.buttons.GenBitmapButton(self,
                                                    bitmap=GetBitmap(bitmap),
                                                    size=wx.Size(28, 28),
                                                    style=wx.NO_BORDER)
            button.SetToolTip(help)
            setattr(self, name, button)
            fast_tasks_button_sizer.Add(button)

        self.FastTasksGrid = CustomGrid(self, style=wx.VSCROLL)
        self.FastTasksGrid.Bind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnFastTasksGridCellChange)
        self.FastTasksGrid.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.LeftClickBugFix)
        self.FastTasksGrid.Bind(wx.EVT_WINDOW_DESTROY, self.OnGridDestroy)
        #self.FastTasksGrid.Bind(wx.grid.EVT_GRID_CMD_CELL_CHANGING)

        fast_tasks_sizer.Add(self.FastTasksGrid, flag=wx.EXPAND | wx.TOP | wx.LEFT | wx.RIGHT | wx.GROW)# , flag=wx.GROW)

        self.InputInterfaceDict = parent.InputInterfaceDict

        self.TagName = tagname
        self.ProgName = program_name
        self.Controler = controler
        self.FastTaskDefaultValue = {"Source": "","Mode": "", "Condition": "", "Value": ""}
        self.FastTaskTable = FastTaskTable(self, [], GetFastTasksEventsTableColnames())
        self.FastTaskTable.SetColAlignements(
            [wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_LEFT, wx.ALIGN_RIGHT, wx.ALIGN_RIGHT])
        self.FastTaskTable.SetColSizes([100, 100, 100, 100])
        self.FastTasksGrid.SetTable(self.FastTaskTable)

        self.FastTasksGrid.SetButtons({"Add": self.AddFastTaskButton,
                                       "Delete": self.DeleteFastTaskButton,
                                       "Up": self.UpFastTaskButton,
                                       "Down": self.DownFastTaskButton})

        self.FastTasksGrid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN,
                                self.OnGridEditorShown)

        button_sizer = self.CreateButtonSizer(wx.OK | wx.CANCEL | wx.CENTRE)
        self.Bind(wx.EVT_BUTTON, self.OnOK)
        main_sizer.Add(button_sizer, flag=wx.ALIGN_RIGHT | wx.BOTTOM | wx.LEFT | wx.RIGHT)
        self.SetFastTable(data)
        self.SetSizer(main_sizer)
        #self.SetSize(main_sizer.GetSize())

        def _AddFastTask(new_row, name=None, type=None, Save=True):

            self.FastTaskTable.InsertRow(new_row, self.FastTaskDefaultValue.copy())
            self.Data = self.FastTaskTable.GetData()
            self.RefreshFastTask()
            self.RefreshView()
            return new_row

        setattr(self.FastTasksGrid, "_AddRow", _AddFastTask)

        def _DeleteFastTask(row):
            self.FastTaskTable.RemoveRow(row)
            self.Data = self.FastTaskTable.GetData()
            self.RefreshFastTask()
            self.RefreshView()

        setattr(self.FastTasksGrid, "_DeleteRow", _DeleteFastTask)

        def _MoveFastTask(row, move):
            new_row = self.FastTaskTable.MoveRow(row, move)
            if new_row != row:
                self.RefreshFastTask()
                self.RefreshView()
                self.Data = self.FastTaskTable.GetData()
            return new_row

        setattr(self.FastTasksGrid, "_MoveRow", _MoveFastTask)

        self.FastTasksGrid.SetRowLabelSize(0)
        self.FastTaskTable.ResetView(self.FastTasksGrid)
        self.FastTasksGrid.RefreshButtons()

    def OnGridDestroy(self, event):
        self.FastTaskTable._updateColAttrs(self.FastTasksGrid)
        event.Skip()
    #def __del__(self):
    #    try:
    #        self.FastTasksGrid.Unbind(wx.grid.EVT_GRID_CELL_CHANGED, self.OnFastTasksGridCellChange)
    #       self.FastTasksGrid.Unbind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.LeftClickBugFix)
    #        self.FastTasksGrid.Unbind(wx.grid.EVT_GRID_EDITOR_SHOWN, self.OnGridEditorShown)
    #        self.Unbind(wx.EVT_BUTTON, self.OnOK)
    #    except:
    #        pass

    def RefreshView(self, variablepanel=True):
        #self.FastTaskTable.SetData(self.Controler.GetEditedFastTask(self.TagName))
        self.FastTaskTable.ResetView(self.FastTasksGrid)
        self.FastTasksGrid.RefreshButtons()
        self.FastTaskTable.SetData(self.Data)

    def RefreshFastTask(self):
        pass

    def OnFastTasksGridCellChange(self, event):
        row, col = event.GetRow(), event.GetCol()
        old_value = event.GetString()
        self.RefreshFastTask()
        colname = self.FastTaskTable.GetColLabelValue(col, False)
        if colname in ["Source", "Mode"]:
            wx.CallAfter(self.RefreshView, False)
        elif colname == "Value":
            max_min_limit, type_value = self.GetLimitVar(self.FastTaskTable.GetValueByName(row, "Source"),
                             self.FastTaskTable.GetValueByName(row, "Mode"))
            if type_value in ["REAL", "LREAL"]:
                value = float(self.FastTaskTable.GetValue(row, col).replace(",","."))
                if value < min(max_min_limit) or value > max(max_min_limit):
                    self.FastTaskTable.SetValue(row, col, old_value)
                    message = wx.MessageDialog(self, _("Invalid value. Available values: %d..%d")%(max_min_limit[0], max_min_limit[1]), _("Error"), wx.OK | wx.ICON_ERROR)
                    message.ShowModal()
                    message.Destroy()
        event.Skip()

    def LeftClickBugFix(self, event):
        event.Skip()

    def GetFastTaskData(self):
        table_data = self.FastTaskTable.GetData()
        return table_data


    def SetFastTable(self, data_parent_table):

       #if "" not in data_parent_table.values():
        events = data_parent_table["Event"].split("\n")
        modes = data_parent_table["Mode"].split("\n")
        if "" not in events:
            data = [{"Source": event.split(" ")[0], "Condition": event.split(" ")[1], "Value": event.split(" ")[2], "Mode": mode}
                    for event, mode in zip(events, modes)]
            self.Data = data
            self.FastTaskTable.SetData(data)

    def CheckFastTaskSettings(self, data):
        test_other_cells = True
        test_fill_cells = "" not in [data["Source"], data["Condition"], data["Value"]]
        modes = self.FastTaskTable.GetModes(data["Source"])

        if len(modes) > 0:
            if data["Mode"] in modes:
                test_other_cells = data["Value"] in [_(limit) for limit in self.GetLimitVar(data["Source"], data["Mode"])[0]]
            else:
                test_other_cells = False
        return test_fill_cells and test_other_cells

    def OnOK(self, event):
        pressed_btn = event.GetId()
        res = False
        if pressed_btn == wx.ID_OK:
            for data in self.Data:

                if self.CheckFastTaskSettings(data):
                    res = True
                else:
                    res = False
                    break
            if res:
                self.EndModal(wx.ID_OK)
            else:
                message = wx.MessageDialog(self, "Fill in all available cells" , _("Error"), wx.OK | wx.ICON_ERROR)
                message.ShowModal()
                message.Destroy()
                return
        elif pressed_btn == wx.ID_CANCEL:
            self.EndModal(wx.ID_CANCEL)

#_("Source"), _("Mode"), _("Condition"), _("Value")
    def OnGridEditorShown(self, event):
        row, col = event.GetRow(), event.GetCol()
        label_value = self.FastTaskTable.GetColLabelValue(col, False)
        if label_value == "Source":
            datatype_menu = wx.Menu(title='')
            for key in self.InputInterfaceDict.keys():
                ch_datatype_menu = wx.Menu(title='')
                interface_min, interface_max = re.split(r'\W+', key[1])
                for i in range(int(interface_min), int(interface_max) + 1):
                    new_id = wx.NewId()
                    menu_name = key[0]+str(i)
                    ch_datatype_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=menu_name)
                    self.Bind(wx.EVT_MENU, self.GetVariableTypeFunction(menu_name), id=new_id)
                datatype_menu.Append(wx.NewId(), key[0], ch_datatype_menu)
            rect = self.FastTasksGrid.BlockToDeviceRect((row, col), (row, col))
            corner_x = rect.x + rect.width
            corner_y = rect.y + self.FastTasksGrid.GetColLabelSize()


            # pop up this new menu
            self.FastTasksGrid.PopupMenu(datatype_menu, corner_x, corner_y)
            datatype_menu.Destroy()
            event.Veto()

    def GetVariableTypeFunction(self, base_type):
        def VariableTypeFunction(event):
            row = self.FastTasksGrid.GetGridCursorRow()
            #col = self.FastTasksGrid.GetGridCursorCol()
            #old_SourceValue = self.FastTaskTable.GetValueByName(row, "Source")
            self.FastTaskTable.SetValueByName(row, "Source", base_type)
            self.FastTaskTable.ResetView(self.FastTasksGrid)
        return VariableTypeFunction
            #base_menu.Append(helpString='', id=new_id, kind=wx.ITEM_NORMAL, item=base_type)
    #type_menu.Append(wx.NewId(), _("Base Types"), base_menu)

    def GetLimitVar(self, source, mode_name):
        max_limit = 0
        min_limit = 0
        key_source = None
        type_value = ""
        if source == "":
            return ["", ""], "str"
        source = re.search(r'\D+', source)
        for key in self.InputInterfaceDict.keys():
            if source[0] in key:
                key_source = key
                break
        if key_source is not None:
            values_limits = self.InputInterfaceDict.get(key_source, list())
            if len(values_limits) == 1:
                value_dict = values_limits[0]
                try:
                    max_limit = int(value_dict['max'])
                    min_limit = int(value_dict['min'])
                    type_value = value_dict['Type']
                except ValueError:
                    return [value_dict['max'], value_dict['min']], "str"
            else:
                for mode_infos in values_limits:
                    if mode_infos['name_mode'] == mode_name:
                        if len(mode_infos["Children"]) == 1:
                            value_infos = mode_infos["Children"][0].get("variable", False)
                            if value_infos:
                                try:
                                    max_limit = int(value_infos['max'])
                                    min_limit = int(value_infos['min'])
                                    type_value = value_infos['Type']
                                except ValueError:
                                    return [value_infos['max'], value_infos['min']], "str"
                                #res = min_value + "," + max_value
                        break
        return [max_limit, min_limit], type_value