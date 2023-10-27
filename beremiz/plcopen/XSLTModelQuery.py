#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Beremiz.
# See COPYING file for copyrights details.


import os
from lxml import etree
import util.paths as paths
from plcopen.structures import StdBlckLibs
from XSLTransform import XSLTransform
import datetime
from copy import deepcopy
ScriptDirectory = paths.AbsDir(__file__)
#region Класс Преобразование элементов (Библиотека решений)
class LibraryResolver(etree.Resolver):
    """Helper object for loading library in xslt stylesheets"""

    def __init__(self, controller, debug=False):
        self.Controller = controller
        self.Debug = debug

    def resolve(self, url, pubid, context):
        lib_name = os.path.basename(url)
        if lib_name in ["project", "stdlib", "extensions"]:
            lib_el = etree.Element(lib_name)
            if lib_name == "project":
                lib_el.append(deepcopy(self.Controller.GetProject(self.Debug)))
            elif lib_name == "stdlib":
                for lib in list(StdBlckLibs.values()):
                    lib_el.append(deepcopy(lib))
            else:
                for ctn in self.Controller.ConfNodeTypes:
                    lib_el.append(deepcopy(ctn["types"]))
            return self.resolve_string(etree.tostring(lib_el), context)
#endregion

class XSLTModelQuery(XSLTransform):
    """ a class to handle XSLT queries on project and libs """
    def __init__(self, controller, xsltpath, ext=None):
        # arbitrary set debug to false, updated later
        self.debug = False
        parser = etree.XMLParser()
        parser.resolvers.add(LibraryResolver(controller, False))
        # print( "  1g  " + str(parser) + "    " + str(xsltpath) + "     " + str(ext))
        XSLTransform.__init__(self,
                              os.path.join(ScriptDirectory, xsltpath),
                              ext,
                              parser)
    def _process_xslt(self, root,  debug, **name):
        self.debug = debug
        # print("      ssssssssssssss    " + str(root) + "     " + str(debug) + "      " + str(name))
        return self.transform(root, **name)
        # print("{4}, {5}, {6}, {7}, {8}, {9}",datetime.datetime.now(), root, debug, name, extens, parser)
        # return self.transform(root, name)

# -------------------------------------------------------------------------------
#           Helpers functions for translating list of arguments
#                       from xslt to valid arguments
# -------------------------------------------------------------------------------


def _StringValue(x):
    return x


def _BoolValue(x):
    return x in ["true", "0"]


def _translate_args(translations, args):
    # print(str(translations) + "      " + str(args) +  "       _translate_args(translations, args)")
    return [translate(arg[0]) if len(arg) > 0 else None
            for translate, arg in
            zip(translations, args)]
