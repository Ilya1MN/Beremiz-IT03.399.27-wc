#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Beremiz.
# See COPYING file for copyrights details.
from copy import deepcopy
import os

from lxml.etree import XSLT
from plcopen.types_enums import *
import util.paths as paths
from lxml import etree
import datetime

ScriptDirectory = paths.AbsDir(__file__)



class XSLTransform(object):
    """ a class to handle XSLT queries on project and libs """
    def __init__(self, xsltpath, xsltext, parser):
        # print("      aaaaaaaaaaaaaaaa    " + str(xsltpath) + "     " + str(xsltext))

        # for name, call in StdBlckLibs:
        #     print(str(call) + "    " + str(name) )
        # print(str(xsltext))

        # parser = etree.XMLParser()
        # parser.resolvers.add(LibraryResolverr(self, False))
        xtext = {("beremiz", name): call for name, call in xsltext}
        # print("      aaaaaaaaaaaaaaaa    " + str(xsltpath) + "     " + str(parser) + "      " + str(xsltext) + "     " + str(xtext))
        # parse and compile. "beremiz" arbitrary namespace for extensions
        self.xslt = etree.XSLT(etree.parse( xsltpath,
                                            parser),
                                            extensions=xtext)



    def transform(self, root, profile_run = False, **kwargs):
     #   print("      tttttttttttttt    " + str(root) + "     " + str(kwargs))
     #    print( "{7}, {8}, {9}, {10}", datetime.datetime.now(),  root, profile_run, kwargs.items())
     #    print("{10}, {11}, {12}, {13}")
        res = self.xslt(root, profile_run=profile_run, **{k: etree.XSLT.strparam(tree) for k, tree in kwargs.items()})#self.xslt(root,  instance_type=etre)
        # print(str(res) + "       13131313")
        return res


    def get_error_log(self):
        return self.xslt.error_log