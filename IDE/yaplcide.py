#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = "$Revision$"

import builtins
import gettext
import os
import sys

gettext.install('yaplcide')  # this is a dummy to prevent gettext falling down

_dist_folder = os.path.split(sys.path[0])[0]
_beremiz_folder = os.path.join(_dist_folder, "beremiz")
#Ensure that Beremiz things are imported before builtins and libs.
sys.path.insert(1,_beremiz_folder)

from Beremiz import *

class YAPLCIdeLauncher(BeremizIDELauncher):
    """
    YAPLC IDE Launcher class
    """
    def __init__(self):
        BeremizIDELauncher.__init__(self)
        self.yaplc_dir = os.path.dirname(os.path.realpath(__file__))
        self.splashPath = self.YApath("images", "splash.png")
        self.extensions.append(self.YApath("yaplcext.py"))

        import features
        # Let's import nucleron yaplcconnectors
        import yaplcconnectors
        import connectors

        connectors.connectors.update(yaplcconnectors.connectors)

        # Import Nucleron yaplctargets
        import yaplctargets
        import targets

        targets.toolchains.update(yaplctargets.toolchains)
        targets.targets.update(yaplctargets.yaplctargets)

        features.libraries = [
	    ('Native', 'NativeLib.NativeLibrary'),
	    ('LibIT', 'LibIT.LibIT'),
            ('LibIT_SYS', 'LibIT_SYS.LibIT_SYS'),
	    ('LibIT_EEPROM', 'LibIT_EEPROM.LibIT_EEPROM'),
	    ('LibIT_MBRTU_MASTER', 'LibIT_MBRTU_MASTER.LibIT_MBRTU_MASTER'),
	    ('LibIT_DI', 'LibIT_DI.LibIT_DI'),
            ('LibIT_AI', 'LibIT_AI.LibIT_AI'),
            ('LibIT_DT', 'LibIT_DT.LibIT_DT'),
	    ('LibIT_PT', 'LibIT_PT.LibIT_PT'),
            ('LibIT_DO', 'LibIT_DO.LibIT_DO'),
            ('LibIT_AO', 'LibIT_AO.LibIT_AO'),
            ('LibIT_STEPPER_MOTOR', 'LibIT_STEPPER_MOTOR.LibIT_STEPPER_MOTOR')]#,
            #('Python', 'py_ext.PythonLibrary'),
        #('SVGUI', 'svgui.SVGUILibrary')]
        
        features.catalog.append(('yaplcconfig',
                                 _('YAPLC Configuration Node'),
                                 _('Adds template located variables'),
                                 'yaplcconfig.yaplcconfig.YAPLCNodeConfig'))

    def YApath(self, *args):
        return os.path.join(self.yaplc_dir, *args)


"""
#-------------------test------------------------
import wx
import wx.lib.agw.hypertreelist as HTL
import wx.lib.agw.floatspin as FSP

class MyFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, -1, "HELP", size=(1000,500))


        self.tree=HTL.HyperTreeList(self, style=wx.TR_HAS_BUTTONS | wx.TR_EDIT_LABELS | wx.TR_HAS_VARIABLE_ROW_HEIGHT | wx.TR_FULL_ROW_HIGHLIGHT)
        self.MainWindow = self.tree.GetMainWindow()


        self.tree.AddColumn("Interfaces", width=300, flag=wx.ALIGN_LEFT)
        self.tree.AddColumn("Condition", width=150)#, flag=wx.ALIGN_CENTER)
        self.tree.AddColumn("Value", width=150)#, flag=wx.ALIGN_CENTER)
        self.tree.AddColumn("COLUMN 3", width=150)#, flag=wx.ALIGN_CENTER)

        sampleList = [">", "<", "="]

        self.tree.SetColumnEditable(0, False)
        self.tree.SetColumnEditable(1, False)
        self.tree.SetColumnEditable(2, False)
        self.tree.SetColumnEditable(3, False)

        parent = self.MainWindow.AddRoot("root")
        #parent=self.tree.AddRoot("root")

        item = self.MainWindow.AppendItem(parent, "DI1...DI8", ct_type=0)

        choice1 = wx.Choice(self.MainWindow, -1, choices=sampleList)
        choice1.SetSize(150, 20)

        spin1 = FSP.FloatSpin(self.MainWindow, min_val=0, max_val=10, increment=0.1, value=0.0, digits=1)
        spin1.SetSize(150, 20)


        self.MainWindow.SetItemWindow(item, choice1, 1)
        self.MainWindow.SetItemWindow(item, spin1, 2)
        self.MainWindow.SetItemText(item, "choice3", 3)

        checkbox = wx.CheckBox(self.MainWindow)
        self.MainWindow.SetItemWindow(item, checkbox, column=0)

        item = self.MainWindow.AppendItem(parent, "LOOOOOOOOONG TEXT")
        #self.MainWindow.SetItemText(item, "B2", 2)
        #self.MainWindow.SetItemText(item, "B3", 3)


        choice1 = wx.Choice(self.MainWindow, -1, choices=sampleList)
        choice1.SetSize(150, 20)

        choice2 = wx.Choice(self.MainWindow, -1, choices=sampleList)
        choice2.SetSize(150, 20)

        choice3 = wx.Choice(self.MainWindow, -1, choices=sampleList)
        choice3.SetSize(150, 20)
       #self.MainWindow.SetSize(choice1.GetSize())

        self.MainWindow.SetItemWindow(item, choice1, 1)
        self.MainWindow.SetItemWindow(item, choice2, 2)
        self.MainWindow.SetItemWindow(item, choice3, 3)
        checkbox = wx.CheckBox(self.MainWindow)
        self.MainWindow.SetItemWindow(item, checkbox, column=0)

        item = self.MainWindow.AppendItem(parent, "VERY LOOOOOOOOOOOOONG TEXT", on_the_right=False)
        #self.MainWindow.SetItemText(item, "C2", 2)
        #self.MainWindow.SetItemText(item, "C3", 3)
        sampleList = ['zero', 'one', 'two', 'three']

        spin1 = FSP.FloatSpin(self.MainWindow, min_val=0, max_val=10, increment=0.1, value=0.0, digits=1)
        spin1.SetSize(150, 20)

        spin2 = FSP.FloatSpin(self.MainWindow, min_val=0, max_val=10, increment=0.1, value=0.0, digits=1)
        spin2.SetSize(150, 20)

        spin3 = FSP.FloatSpin(self.MainWindow, min_val=0, max_val=10, increment=0.1, value=0.0, digits=1)
        spin3.SetSize(150, 20)

        self.MainWindow.SetItemWindow(item, spin1, 1)
        self.MainWindow.SetItemWindow(item, spin2, 2)
        self.MainWindow.SetItemWindow(item, spin3, 3)
        #self.tree.GetMainWindow().SetItemBackgroundColour(item, 'green', 0)

        checkbox = wx.CheckBox(self.MainWindow)
        self.MainWindow.SetItemWindow(item, checkbox, column=0)
        self.MainWindow.ExpandAll()





if __name__=='__main__':
    app = wx.PySimpleApp()
    frame=MyFrame()
    frame.Show()
    app.MainLoop()
#-------------------test------------------------
"""

import wx
import sys
import traceback

def show_error():
    message = ''.join(traceback.format_exception(*sys.exc_info()))
    dialog = wx.MessageDialog(None, message, 'Error!', wx.OK|wx.ICON_ERROR)
    dialog.ShowModal()

# This is where we start our application
if __name__ == '__main__':
    try:
        beremiz = YAPLCIdeLauncher()
        beremiz.Start()
    except:
        show_error()
