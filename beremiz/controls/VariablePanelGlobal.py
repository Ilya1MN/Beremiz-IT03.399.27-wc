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
from .CustomGrid import CustomGrid
from util.BitmapLibrary import GetBitmap
from PLCControler import _VariableInfos
from util.TranslationCatalogs import NoTranslate
from .VariablePanel import VariablePanel, VariableDropTarget, VariableTable, GLOBAL_VAR_NAME_DEFAULT

VARIABLE_NAME_SUFFIX_MODEL = re.compile("([0-9]*)$")
# -------------------------------------------------------------------------------
#                                 Helpers
# -------------------------------------------------------------------------------


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

def GetFilterChoiceTransfer():
    _ = NoTranslate
    return {_("All"): _("All"), _("Interface"): _("Interface"),
            _("   Input"): _("Input"), _("   Output"): _("Output"), _("   InOut"): _("InOut"),
            _("   External"): _("External"), _("Variables"): _("Variables"), _("   Local"): _("Local"),
            _("   Temp"): _("Temp"), _("Global"): _("Global")}  # , _("Access") : _("Access")}

class VariablePanelGlobal(VariablePanel):
    def __init__(self, parent, window, controler, element_type, debug=False):
        wx.Panel.__init__(self, parent, style=wx.TAB_TRAVERSAL)

        self.ParentWindow = window
        self.Controler = controler
        self.ElementType = element_type
        self.Debug = debug

        self.Values = None

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
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_LABEL_RIGHT_CLICK, self.on_cell_right_clickGrid)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_cell_right_clickGrid)
        self.VariablesGrid.Bind(wx.grid.EVT_GRID_CMD_LABEL_RIGHT_CLICK, self.on_cell_right_clickGrid)
        # self.VariablesGrid.Bind(wx.grid.EVT_GRID_EDITOR_SHOWN,
        #                         self.OnVariablesGridEditorShown)
        self.Bind(wx.EVT_RIGHT_UP, self.on_cell_right_click)
        # self.VariablesGrid.Bind(wx.EVT_KEY_DOWN, self.)

        ctrl_C_id = wx.NewId()
        ctrl_V_id = wx.NewId()

        self.ParentWindow.Bind(wx.EVT_MENU, self.onCtrlV, id=ctrl_V_id)
        self.ParentWindow.Bind(wx.EVT_MENU, self.onCtrlC, id=ctrl_C_id)

        acce1_tb1 = wx.AcceleratorTable([(wx.ACCEL_CTRL, ord('C'), ctrl_C_id),
                                         (wx.ACCEL_CTRL, ord('V'), ctrl_V_id)])

        self.VariablesGrid.SetAcceleratorTable(acce1_tb1)

        self.MainSizer.Add(self.VariablesGrid, flag=wx.GROW)
        self.SetSizer(self.MainSizer)

        self.RefreshHighlightsTimer = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnRefreshHighlightsTimer,
                  self.RefreshHighlightsTimer)

        self.Filter = "All"
        self.FilterChoices = []
        self.FilterChoiceTransfer = GetFilterChoiceTransfer()

        self.DefaultValue = _VariableInfos("", "", "", "", "", True, "", (_("Default")), DefaultType, ([], []), 0)

        self.DefaultTypes = {"All": "External", "Interface": "External", "Variables": "Local"}

        # this is an element that cannot have located variables
        self.Table = VariableTable(self, [], GetVariableTableColnames(False, True))

        if element_type in ["program", "functionBlock"]:
            self.FilterChoices = ["All",
                                      "Interface", "   External"]

        # these condense the alignements list
        left = wx.ALIGN_LEFT
        center = wx.ALIGN_CENTER
        self.Table = VariableTable(self, [], GetVariableTableColnames(False, False))
        #                        Num        Name    Class   Type    Init    Option  Doc
        self.ColSettings = {
            "size":             [40,         80,     100,    80,     120,    100,    160],
            "alignement":       [center,    left,   left,   left,   left,   left,   left],
            "fixed_size":       [True,      False,  True,   False,  True,   True,   False],
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
            #Name = GLOBAL_VAR_NAME_DEFAULT
            if new_row > 0:
                row_content = self.Values[new_row - 1].copy()
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
                row_content = None
                if Name is not None:
                    name = Name
                else:
                    name = "ExternalVar"

            if row_content is not None and row_content.Edit:
                row_content = self.Values[new_row - 1].copy()
                if type is not None:
                    row_content.Type = type
            else:
                row_content = self.DefaultValue.copy()
                if type is not None:
                    row_content.Type = type
                if self.Filter in self.DefaultTypes:
                    row_content.Class = self.DefaultTypes[self.Filter]
                else:
                    row_content.Class = self.Filter
            if Name is not None:
                names = {}
                names_not_save = {}
                if self.TagName is not None:
                    names.update(dict([(varname.upper(), True)
                                       for varname in self.Controler.GetEditedElementVariables(self.TagName, debug)]))
                    names_not_save.update(dict([(varname.Name.upper(), True)
                                                for varname in self.Values]))
                if names.get(Name.upper(), False) and names_not_save.get(Name.upper(), False):
                    row_content.Name = self.Controler.GenerateNewName(
                        self.TagName, None, name + "%d", start_idx, exclude=names_not_save)
                else:
                    row_content.Name = Name
            else:
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
            selection = self.VariablesGrid.get_selection()
            if not selection:
                return []
            start_row, start_col, end_row, end_col = selection
            self.VariablesGrid.SetSelectedCell(start_row, start_col)
            if _GetRowEdit(row):
                try:
                    for i in range(abs(end_row - start_row) + 1):
                        self.Values.remove(self.Table.GetRow(i + start_row))
                except:
                    pass
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
                self.AddButton.Enable(not self.Debug)
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

    def RefreshView(self):
        self.PouNames = self.Controler.GetProjectPouNames(self.Debug)
        returnType = None
        self.Values = []
        for values in self.Controler.GetEditedElementInterfaceVars(self.TagName, debug=self.Debug):
            if values.Class == "External":
                self.Values.append(values)

        if returnType is not None:
            self.ReturnType.SetStringSelection(returnType)
            self.ReturnType.Enable(not self.Debug)
            self.ReturnTypeLabel.Show()
            self.ReturnType.Show()
        else:
            self.ReturnType.Enable(False)
            self.ReturnTypeLabel.Hide()
            self.ReturnType.Hide()

        self.Description.Enable(False)
        self.DescriptionLabel.Hide()
        self.Description.Hide()

        self.RefreshValues()
        self.VariablesGrid.RefreshButtons()
        self.MainSizer.Layout()

    def OnVariablesGridEditorShown(self, event):
        row, col = event.GetRow(), event.GetCol()
        label_value = self.Table.GetColLabelValue(col, False)
        self.EditNameVar = False
        if label_value == "Type":
            old_value = self.Values[row].Type
            classtype = self.Table.GetValueByName(row, "Class")
            type_menu = wx.Menu(title='')   # the root menu

            self.BuildStdIECTypesMenu(type_menu)
            self.BuildUserTypesMenu(type_menu)
            self.BuildLibsTypesMenu(type_menu)
            self.BuildProjectTypesMenu(type_menu, classtype)
            self.BuildArrayTypesMenu(type_menu)

            rect = self.VariablesGrid.BlockToDeviceRect((row, col), (row, col))
            corner_x = rect.x + rect.width
            corner_y = rect.y + self.VariablesGrid.GetColLabelSize()

            # pop up this new menu
            self.VariablesGrid.PopupMenu(type_menu, corner_x, corner_y)
            type_menu.Destroy()
            event.Veto()
            value = self.Values[row].Type
            if old_value != value:
                self.ClearLocation(row, col, value)
        elif label_value == "Name":
            old_value = self.Values[row].Name
            type_menu = wx.Menu(title='')  # the root menu
            self.BuildGlobalVarTypesMenu(type_menu)
            resources_variables = list()
            project = self.Controler.GetProject(self.Debug)
            if project is not None:
                for config in project.getconfigurations():
                    for resource in config.getresource():
                        resource_name = resource.getname()
                        resources_variables += self.Controler.GetConfigurationResourceGlobalVars(config.getname(), resource_name)
            if resources_variables: #len(resources_variables) > 0:
                type_menu.AppendSeparator()
                self.BuildGlobalVarTypesMenu(type_menu, Variables=resources_variables,
                                             Resource=True)

            new_id = wx.NewId()
            type_menu.Append(new_id, (_("Enter name")))
            self.Bind(wx.EVT_MENU, self.EnterNameGlobalVar, id=new_id)
            rect = self.VariablesGrid.BlockToDeviceRect((row, col), (row, col))
            corner_x = rect.x + rect.width
            corner_y = rect.y + self.VariablesGrid.GetColLabelSize()

            # pop up this new menu
            self.VariablesGrid.PopupMenu(type_menu, corner_x, corner_y)
            type_menu.Destroy()
            if self.EditNameVar:
                event.Skip()
                return
            event.Veto()
            value = self.Values[row].Name
            if old_value != value:
                self.ClearLocation(row, col, value)
        else:
            event.Skip()

    def pasteGrid(self, event):
        dialog = None
        try:
            KeyNames, data = self.GetTableFromClipboard()
        except:
            self.NoDataInsertDialog()
            return
        if not isinstance(KeyNames, list):
            self.NoDataInsertDialog()
        else:
            datatable = []
            _data = data.split("\n")
            try:
                for row in _data:
                    datatable.append(row.split("\t"))


                TableDict = {}
                for col in range(len(KeyNames)):
                    colline = []
                    for row in range(1, len(datatable) - 1):
                        colline.append(datatable[row][col])
                    TableDict[KeyNames[col]] = colline
                if _("External") not in TableDict.get(_("Class")):
                    dialog = wx.MessageDialog(self, _("No data to insert"), _("Error"), style=wx.OK)
                    res = dialog.ShowModal()
                    dialog.EndModal(res)
                    return
                select_row = None
                dialog = self.CopyProgressDialog()
                for row in (range(len(_data) - 2)):
                    if TableDict.get(_("Name")) is None:
                        self.VariablesGrid.AddRow(Save=False)
                    else:
                        self.VariablesGrid.AddRow(TableDict[_("Name")][row], Save=False)
                    if select_row is None:
                        select_row = self.VariablesGrid.GetGridCursorRow()
                TableDict.pop('#', None)
                TableDict.pop(_("Name"), None)
                TableDict.pop(_("Group"), None)
                for row in range(len(_data) - 2):
                    if select_row is None:
                        select_row = self.VariablesGrid.GetGridCursorRow()
                    for key in TableDict:
                        for col in range(self.VariablesGrid.GetNumberCols()):
                            if key == self.VariablesGrid.GetColLabelValue(col):
                                if key == _("Class"):
                                    TableDict[key][row] = _("External")
                                try:
                                    self.VariablesGrid.SetCellValue(select_row, col, TableDict[key][row])
                                    break
                                except:
                                    print("Table paste Error!")
                                    break
                    select_row += 1
                self.SaveValues()
            except:
                pass
            if dialog is not None:
                dialog.Destroy()

    def EnterNameGlobalVar(self, event):
        self.EditNameVar = True