#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Beremiz.
# See COPYING file for copyrights details.

import os
import util.paths as paths
from lxml import etree
import datetime
ScriptDirectory = paths.AbsDir(__file__)
class XSLTransform(object):
    """ a class to handle XSLT queries on project and libs """
    def __init__(self, xsltpath, xsltext):
        # print(xsltpath + "   " )
        #
        # for name, call in xsltext:
        #     print(str(call) + "    " + str(name) )
        # parse and compile. "beremiz" arbitrary namespace for extensions
        self.xslt = etree.XSLT(
            etree.parse(
                xsltpath,
                etree.XMLParser()),
            extensions={("var_infos_ns", name): call for name, call in xsltext})

    def transform(self, root, profile_run=False, **kwargs):
        # print( "{7}, {8}, {9}, {10}", datetime.datetime.now(),  root, profile_run, kwargs.items())
        # print("{10}, {11}, {12}, {13}")
        res = self.xslt(root, profile_run=profile_run, **{k: etree.XSLT.strparam(tree) for k, tree in kwargs.items()})
       # print(self.xslt.error_log)
        return res


    def get_error_log(self):
        return self.xslt.error_log