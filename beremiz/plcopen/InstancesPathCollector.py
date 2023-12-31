#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of Beremiz.
# See COPYING file for copyrights details.

from .XSLTModelQuery import XSLTModelQuery
#from __future__ import absolute_import


class InstancesPathFactory:
    """Helpers object for generating instances path list"""
    def __init__(self, instances):
        self.Instances = instances

    def AddInstance(self, context, *args):
        self.Instances.append(args[0][0])

class InstancesPathCollector(XSLTModelQuery):
    """ object for collecting instances path list"""
    def __init__(self, controller):

        self.Instances = []

        XSLTModelQuery.__init__(self,
                                controller,
                                "instances_path.xslt",
                                [("AddInstance", self.AddInstance)])

    def AddInstance(self, context, *args):
        self.Instances.append(args[0][0])

    def Collect(self, root,  name, debug):
        factory = InstancesPathFactory(self.Instances)

        # print("      vvvvvvvvvvvvvvvvv    " + str(root) + "     " + str(debug) + "      " + str(name))
        self._process_xslt(root, debug, instance_type=name)
        if self.Instances is not None:
            res = self.Instances
            self.Instances = []
            return res