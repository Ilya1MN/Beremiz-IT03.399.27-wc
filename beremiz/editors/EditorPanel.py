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
import wx.aui

from controls import VariablePanelFB, VariablePanelConfiguration, VariablePanelGlobal, VariablePanelLocal


class EditorPanel(wx.SplitterWindow):

    VARIABLE_PANEL_TYPE = None

    def _init_Editor(self, prnt):
        self.Editor = None

    def _init_MenuItems(self):
        self.MenuItems = []

    def _init_ctrls(self, parent):

        wx.SplitterWindow.__init__(self, parent, size=wx.Size(1,1))
        self.SetMinimumPaneSize(1)
        self._init_MenuItems()
        self.CheckPouInOut = False
        if self.VARIABLE_PANEL_TYPE is not None:
            if self.VARIABLE_PANEL_TYPE not in ["functionBlock", "program", "function"]:
                self.VariableEditor = VariablePanelConfiguration(self, self, self.Controler, self.VARIABLE_PANEL_TYPE, self.Debug)
            else:
                self.VariableEditor = VariablePanelLocal(self, self, self.Controler, self.VARIABLE_PANEL_TYPE, self.Debug)
            self.VariableEditor.SetTagName(self.TagName)
            self.VariableEditorTwo = None
            self.VariableEditorThree = None
            self.Notebook = None
            self.RadioBox = None
            if self.VARIABLE_PANEL_TYPE in ["functionBlock", "program"]:
                self.Notebook = wx.aui.AuiNotebook(self, 0,
                                                   style=(wx.aui.AUI_NB_TOP |
                                                          wx.aui.AUI_NB_TAB_SPLIT |
                                                          wx.aui.AUI_NB_TAB_MOVE |
                                                          wx.aui.AUI_NB_SCROLL_BUTTONS |
                                                          wx.aui.AUI_NB_TAB_EXTERNAL_MOVE))

                self.VariableEditorTwo = VariablePanelGlobal(self, self, self.Controler, self.VARIABLE_PANEL_TYPE, self.Debug)
                self.VariableEditorTwo.SetTagName(self.TagName)
                self.VariableEditorThree = VariablePanelFB(self, self, self.Controler, self.VARIABLE_PANEL_TYPE, self.Debug)
                self.VariableEditorThree.SetTagName(self.TagName)
                self.Notebook.AddPage(self.VariableEditorTwo, _("Global Variables"))
                self.Notebook.AddPage(self.VariableEditor, _("Local Variables"))
                self.Notebook.AddPage(self.VariableEditorThree, _("Function blocks variables"))


        else:
            self.Notebook = None
            self.VariableEditor = None
        self._init_Editor(self)

        if self.Editor is not None and self.Notebook is not None:
            self.SplitHorizontally(self.Notebook, self.Editor, 200)
        elif self.Notebook is not None:
            self.Initialize(self.Notebook)
        elif self.Editor is not None and self.VariableEditor is not None:
            self.SplitHorizontally(self.VariableEditor,self.Editor, 200)
        elif self.VariableEditor is not None:
            self.Initialize(self.VariableEditor)
        elif self.Editor is not None:
            self.Initialize(self.Editor)


    def __init__(self, parent, tagname, window, controler, debug=False):
        self.ParentWindow = window
        self.Controler = controler
        self.TagName = tagname
        self.Icon = None
        self.Debug = debug

        self._init_ctrls(parent)

    def SetTagName(self, tagname):
        self.TagName = tagname
        if self.VARIABLE_PANEL_TYPE is not None:
            self.VariableEditor.SetTagName(tagname)
            if self.Notebook is not None:
                self.VariableEditorTwo.SetTagName(tagname)
                self.VariableEditorThree.SetTagName(tagname)

    def GetTagName(self):
        return self.TagName

    def Select(self):
        self.ParentWindow.EditProjectElement(None, self.GetTagName(), True)

    def GetTitle(self):
        return ".".join(self.TagName.split("::")[1:])

    def GetIcon(self):
        return self.Icon

    def SetIcon(self, icon):
        self.Icon = icon

    def IsViewing(self, tagname):
        return self.GetTagName() == tagname

    def IsDebugging(self):
        return self.Debug

    def SetMode(self, mode):
        pass

    def ResetBuffer(self):
        pass

    def IsModified(self):
        return False

    def CheckSaveBeforeClosing(self):
        return True

    def Save(self):
        pass

    def SaveAs(self):
        pass

    def GetBufferState(self):
        if self.Controler is not None:
            return self.Controler.GetBufferState()
        return False, False

    def Undo(self):
        if self.Controler is not None:
            self.Controler.LoadPrevious()
            self.RefreshView()

    def Redo(self):
        if self.Controler is not None:
            self.Controler.LoadNext()
            self.RefreshView()

    def Find(self, direction, search_params):
        pass

    def HasNoModel(self):
        return False

    def RefreshView(self, variablepanel=True):
        if variablepanel:
            self.RefreshVariablePanel()

    def RefreshVariablePanel(self):
        if self.Notebook is not None:
            SelectedPage = self.Notebook.GetCurrentPage()
            if SelectedPage is not None:
                SelectedPage.RefreshView()
        elif self.VariableEditor is not None:
            self.VariableEditor.RefreshView()

    def GetConfNodeMenuItems(self):
        return self.MenuItems

    def RefreshConfNodeMenu(self, confnode_menu):
        pass

    def _Refresh(self, *args):
        self.ParentWindow._Refresh(*args)

    def RefreshScaling(self, refresh=True):
        pass

    def AddHighlight(self, infos, start, end, highlight_type):
        if self.VariableEditor is not None and infos[0] in ["var_local", "var_input", "var_output", "var_inout"]:
            if self.Notebook is not None:
                lst_infos = list(infos)
                highlight_values = self.Controler.GetEditedElementInterfaceVars(self.TagName, self.Debug)[infos[1]]
                if highlight_values.Class == "External":
                    NotebookPage = 0
                    selected_page = self.VariableEditorTwo
                elif highlight_values.Type not in self.Controler.GetBaseTypes():
                    NotebookPage = 2
                    selected_page = self.VariableEditorThree
                else:
                    NotebookPage = 1
                    selected_page = self.VariableEditor
                if selected_page != self.Notebook.GetCurrentPage():
                    self.Notebook.ChangeSelection(NotebookPage)
                    selected_page.RefreshView()
                try:
                    Values_in_class = selected_page.Values[infos[1]]
                except:
                    Values_in_class = selected_page.Values[0]
                if Values_in_class.Name != highlight_values.Name:
                    for var in selected_page.Values:
                        if highlight_values.Name == var.Name:
                            lst_infos[1] = var.Number - 1
                else:
                    lst_infos[1] = Values_in_class.Number - 1
                    print("queck search\n")
                infos = tuple(lst_infos)
                selected_page.AddVariableHighlight(infos[1:], highlight_type)
                return
            else:
                self.VariableEditor.AddVariableHighlight(infos[1:], highlight_type)


    def RemoveHighlight(self, infos, start, end, highlight_type):
        if self.Notebook is not None:
            page = self.Notebook.GetCurrentPage()
            if page is not None and infos[0] in ["var_local", "var_input", "var_output", "var_inout"]:
                page.RemoveVariableHighlight(infos[1:], highlight_type)
        elif self.VariableEditor is not None and infos[0] in ["var_local", "var_input", "var_output", "var_inout"]:
            self.VariableEditor.RemoveVariableHighlight(infos[1:], highlight_type)

    def ClearHighlights(self, highlight_type=None):
        if self.Notebook is not None:
            page = self.Notebook.GetCurrentPage()
            page.ClearHighlights(highlight_type)
        elif self.VariableEditor is not None:
            self.VariableEditor.ClearHighlights(highlight_type)

    def SaveValues(self, word):
        values = []
        for editor in [self.VariableEditor, self.VariableEditorTwo, self.VariableEditorThree]:
            if editor.Values is None:
                editor.RefreshView()
            values += editor.Values
        self.Controler.SetPouInterfaceVars(word, values)