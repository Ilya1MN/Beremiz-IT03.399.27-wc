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
import wx.grid
from natsort import natsorted


class CustomGrid(wx.grid.Grid):

    def __init__(self, *args, **kwargs):
        wx.grid.Grid.__init__(self, *args, **kwargs)

        self.Editable = True

        self.AddButton = None
        self.DeleteButton = None
        self.UpButton = None
        self.DownButton = None

        self.SetFont(wx.Font(12, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Sans'))
        self.SetLabelFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.NORMAL, False, 'Sans'))
        self.DisableDragRowSize()

        self.Bind(wx.grid.EVT_GRID_CELL_LEFT_CLICK, self.OnLeftClickCell)
        self.Bind(wx.grid.EVT_GRID_SELECT_CELL, self.OnSelectCell)
        self.Bind(wx.grid.EVT_GRID_EDITOR_HIDDEN, self.OnEditorHidden)

        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.selected_cols = []
        self.Bind(wx.grid.EVT_GRID_LABEL_LEFT_DCLICK, self.on_label_left_dclick)
        self.SelectSortColumn = None
        #self.Bind(wx.grid.EVT_GRID_CELL_RIGHT_CLICK, self.on_cell_right_click)

    def SetFocus(self):
        if self:
            wx.grid.Grid.SetFocus(self)

    def SetDefaultValue(self, default_value):
        self.DefaultValue = default_value

    def SetEditable(self, editable=True):
        self.Editable = editable
        self.RefreshButtons()

    def SetButtons(self, buttons):
        for name in ["Add", "Delete", "Up", "Down"]:
            button = buttons.get(name, None)
            setattr(self, "%sButton" % name, button)
            if button is not None:
                button.Bind(wx.EVT_BUTTON, getattr(self, "On%sButton" % name))

    def RefreshButtons(self):
        if self:
            rows = self.Table.GetNumberRows()
            row = self.GetGridCursorRow()
            if self.AddButton is not None:
                self.AddButton.Enable(self.Editable)
            if self.DeleteButton is not None:
                self.DeleteButton.Enable(self.Editable and rows > 0)
            if self.UpButton is not None:
                self.UpButton.Enable(self.Editable and row > 0)
            if self.DownButton is not None:
                self.DownButton.Enable(self.Editable and 0 <= row < rows - 1)

    def CloseEditControl(self):
        row, col = self.GetGridCursorRow(), self.GetGridCursorCol()
        if row != -1 and col != -1:
            self.SetGridCursor(row, col)

    def AddRow(self, Name=None, type=None, Save=True):
        self.CloseEditControl()
        new_row = self.GetGridCursorRow() + 1
        col = max(self.GetGridCursorCol(), 0)
        if getattr(self, "_AddRow", None) is not None:
            new_row = self._AddRow(new_row, Name, type, Save)
        else:
            self.Table.InsertRow(new_row, self.DefaultValue.copy())
            self.Table.ResetView(self)
        if new_row is not None:
            self.SetSelectedCell(new_row, col)

    def DeleteRow(self):
        #self.CloseEditControl()
        row = self.GetGridCursorRow()
        if row >= 0:
            col = self.GetGridCursorCol()
            if getattr(self, "_DeleteRow", None) is not None:
                self._DeleteRow(row)
            else:
                self.Table.RemoveRow(row)
                self.Table.ResetView(self)
            if self.Table.GetNumberRows() > 0:
                self.SetSelectedCell(min(row, self.Table.GetNumberRows() - 1), col)

    def MoveRow(self, row, move):
        self.CloseEditControl()
        col = self.GetGridCursorCol()
        if getattr(self, "_MoveRow", None) is not None:
            new_row = self._MoveRow(row, move)
        else:
            new_row = self.Table.MoveRow(row, move)
            if new_row != row:
                self.Table.ResetView(self)
        if new_row != row:
            self.SetSelectedCell(new_row, col)

    def SetSelectedCell(self, row, col):
        self.SetGridCursor(row, col)
        self.MakeCellVisible(row, col)
        self.RefreshButtons()

    def OnAddButton(self, event):
        self.AddRow()
        self.SetFocus()
        event.Skip()

    def OnDeleteButton(self, event):
        self.DeleteRow()
        self.SetFocus()
        event.Skip()

    def OnUpButton(self, event):
        self.MoveRow(self.GetGridCursorRow(), -1)
        self.SetFocus()
        event.Skip()

    def OnDownButton(self, event):
        self.MoveRow(self.GetGridCursorRow(), 1)
        self.SetFocus()
        event.Skip()

    def OnSelectCell(self, event):
        wx.CallAfter(self.RefreshButtons)
        self.SelectRow(event.GetRow(), False)
        event.Skip()

    def OnLeftClickCell(self, event):
        if self.GetSelectionMode() != self.GridSelectRows:
            self.SetSelectionMode(self.GridSelectRows)
        self.SelectRow(event.GetRow(), False)
        event.Skip()

    def OnEditorHidden(self, event):
        wx.CallAfter(self.SetFocus)
        event.Skip()

    def OnKeyDown(self, event):
        key_handled = False
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_TAB:
            row = self.GetGridCursorRow()
            col = self.GetGridCursorCol()
            if event.ShiftDown():
                if row < 0 or col == 0:
                    self.Navigate(wx.NavigationKeyEvent.IsBackward)
                    key_handled = True
            elif row < 0 or col == self.Table.GetNumberCols() - 1:
                self.Navigate(wx.NavigationKeyEvent.IsForward)
                key_handled = True
        elif keycode in (wx.WXK_ADD, wx.WXK_NUMPAD_ADD) and self.Editable:
            self.AddRow()
            key_handled = True
        elif keycode in (wx.WXK_DELETE, wx.WXK_NUMPAD_DELETE) and self.Editable:
            self.DeleteRow()
            key_handled = True
        elif keycode == wx.WXK_UP and event.ShiftDown() and self.Editable:
            self.MoveRow(self.GetGridCursorRow(), -1)
            key_handled = True
        elif keycode == wx.WXK_DOWN and event.ShiftDown() and self.Editable:
            self.MoveRow(self.GetGridCursorRow(), 1)
            key_handled = True

        if not key_handled:
            event.Skip()


    def get_selection(self):
        """
        Returns selected range's start_row, start_col, end_row, end_col
        If there is no selection, returns selected cell's start_row=end_row, start_col=end_col
        """
        if not len(self.GetSelectionBlockTopLeft()):
            selected_columns = self.GetSelectedCols()
            selected_rows = self.GetSelectedRows()
            if selected_columns:
                start_col = selected_columns[0]
                end_col = selected_columns[-1]
                start_row = 0
                end_row = self.GetNumberRows() - 1
            elif selected_rows:
                start_row = selected_rows[0]
                end_row = selected_rows[-1]
                start_col = 0
                end_col = self.GetNumberCols() - 1
            else:
                start_row = end_row = self.GetGridCursorRow()
                start_col = end_col = self.GetGridCursorCol()
        elif len(self.GetSelectionBlockTopLeft()) > 1:
            wx.MessageBox(_("Multiple selections are not supported"), _("Warning"))
            return []
        else:
            start_row, start_col = self.GetSelectionBlockTopLeft()[0]
            end_row, end_col = self.GetSelectionBlockBottomRight()[0]

        return [start_row, start_col, end_row, end_col]

    def get_selected_cells(self):
        # returns a list of selected cells
        selection = self.get_selection()
        if not selection:
            return

        start_row, start_col, end_row, end_col = selection
        for row in range(start_row, end_row + 1):
            for col in range(start_col, end_col + 1):
                yield [row, col]

    def CopyTableLine(self):
        pass

    def PasteTableLine(self):
        pass

    def SortColumn(self, col):
        """
        col -> sort the data based on the column indexed by col
        """
        self.SelectSortColumn = col
        RowTableSz = self.GetNumberRows()
        ColTableSz = self.GetNumberCols()
        _data = self.GetTableDArray()
        _data = natsorted(_data, key=lambda x: x[col].lower())

        if _data[RowTableSz-1][col] != '':
            while _data[0][col] == '':
                element = _data.pop(0)
                _data.append(element)

        for rows in range(RowTableSz):
            for cols in range(ColTableSz):
                self.SetCellValue(rows, cols, _data[rows][cols])

    def GetTableDArray(self):
        _data = []
        for row in range(self.GetNumberRows()):
            ColsLine = []
            for col in range(self.GetNumberCols()):
                ColsLine.append(self.GetCellValue(row, col))
            _data.append(ColsLine)
        return _data

    def on_label_rigth_click(self, event):
        """
        Displays a message dialog to the user which displays which row
        label the user clicked on
        """
        # Note that rows are zero-based

        row = event.GetRow()

        if row != -1:
            self.SetSelectedCell(row, 0)

    def on_label_left_dclick(self, event):
        """
        Displays a message dialog to the user which displays which row
        label the user clicked on
        """
        # Note that rows are zero-based
        col = event.GetCol()
        if col != -1:
            self.SortColumn(col)