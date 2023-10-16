"""
Beremiz YAPLC Targets

- Target are python packages, containing at least one "XSD" file
- Target class may inherit from a toolchain_(toolchainname)
- The target folder's name must match to name define in the XSD for TargetType
"""

from os import listdir, path
from targets import _GetTargets
import sys

_base_path = path.split(__file__)[0]
sys.path.insert(1, _base_path)


def _GetLocalTargetClassFactory(name):
    return lambda: getattr(__import__(name, globals(), locals()), str(name)+"_target")

yaplctargets = _GetTargets(_base_path)
"""yaplctargets = dict([(name, {"xsd":   path.join(_base_path, name, "XSD"),
                            "class": _GetLocalTargetClassFactory(name),
                            "code":  {fname: path.join(_base_path, name, fname)
                                  for fname in listdir(path.join(_base_path, name))
                                  if fname.startswith("plc_%s_main" % name) and
                                   fname.endswith(".c")}})
                for name in listdir(_base_path)
                    if path.isdir(path.join(_base_path, name))
                       and not name.startswith("__")])"""

toolchains = {"yaplc":  path.join(_base_path, "XSD_toolchain_yaplc")}

def GetTargetsNames():
    return [name for name in listdir(_base_path)
            if path.isdir(path.join(_base_path, name)) and not name.startswith("__")]

def GetBuilder(targetname):
    return yaplctargets[targetname]["class"]()

def GetTargetChoices():
    DictXSD_toolchain = {}
    targetchoices = ""

    # Get all xsd toolchains
    for toolchainname, xsdfilename in toolchains.items():
         if path.isfile(xsdfilename):
             DictXSD_toolchain["toolchain_"+toolchainname] = open(xsdfilename).read()

    # Get all xsd yaplctargets
    for targetname,nfo in yaplctargets.items():
        xsd_string = open(nfo["xsd"]).read()
        targetchoices += xsd_string % DictXSD_toolchain

    return targetchoices


def GetTargetCode(targetname):
    codedesc = yaplctargets[targetname]["code"]
    code = "\n".join([open(fpath).read() for fname, fpath in sorted(codedesc.items())])
    return code


def GetHeader():
    filename = path.join(path.split(__file__)[0],"beremiz.h")
    return open(filename).read()


def GetCode(name):
    filename = path.join(path.split(__file__)[0],name)
    return open(filename).read()
