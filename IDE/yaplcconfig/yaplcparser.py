import shlex
import collections
import os
from lxml import etree

"""
TODO: Syntax extensions
1. Enumerated parameters split by ',' sign placed inside square brackets.
2. Regions doesn't generate all values when created, but operates with min/max ranges.
3. Single value parameters interprets like a group id.
4. Range group parameters interprets like a tuple of groups.
5. Text labels are enclosed with quotes inside square brackets after value split by a column from value.
6. Correct group id detection.
7. Use meta-class to create more accurate and extensible parameters class.
8. Locations may have descriptive name. Optional for plain locations and required for parametrized.
"""

"""
YAPLC locations: Input, Memory, Output(Q)
"""
YAPLCLocationTypes = ['I', 'M', 'Q']

YAPLCLocationTepesDict = {'input': 'I', 'output': 'Q', 'memory': 'M'}

IEC_TYPES = [
    "BOOL",
    "SINT",
    "INT",
    "DINT",
    "LINT",
    "USINT",
    "UINT",
    "UDINT",
    "ULINT",
    "REAL",
    "LREAL",
    "STRIN",
    "BYTE",
    "WORD",
    "DWORD",
    "LWORD",
    "WSTRING"
]

"""
YAPLC locations data types: bool, byte, word, double-word, long, string
"""
YAPLCLocationDataTypes = ['X', 'B', 'W', 'D', 'L', 'S']

"""
YAPLC location parameter types
"""
YAPLCParameterType = {'Number': 0, 'Range': 1, 'Items': 2}

"""
"""
YAPLCNameIllegal = ['.', ',', '"', '*', ':', '#', '@', '!', '(', ')', '{', '}']


class ParseError(BaseException):
    """ Exception reports parsing errors when processing YAPLC template files """

    def __init__(self, message=None):
        self._message = message

    def message(self):
        return self._message


class YAPLCLocationBase:

    def __init__(self):
        self._parameters = list()
        self._parametrized = False

    def addParameters(self, values, name=""):

        if values.find('..') >= 0:
            # range of channels
            bounds = values.split('..')

            if len(bounds) != 2:
                raise ParseError(_("Wrong range syntax"))

            if not bounds[0].isdigit() or not bounds[1].isdigit():
                raise ParseError(_("Incorrect bounds format %s..%s") % bounds[0] % bounds[1])

            lbound = int(bounds[0])
            rbound = int(bounds[1])

            self._parameters.append({"name": name,
                                     "type": 'Range',
                                     "min": lbound,
                                     "max": rbound
                                     })

        elif values.find(',') >= 0:
            items = values.split(',')

            self._parameters.append({"name": name,
                                     "type": 'Items',
                                     "items": items
                                     })
        else:
            self._parameters.append({"name": name,
                                     "type": 'Number',
                                     "value": values
                                     })

    def parameters(self):
        return self._parameters

    def parametrized(self):
        return self._parametrized


class YAPLCLocation(YAPLCLocationBase):
    """
    YAPLC location abstraction to represent an location described by syntax
    """

    def __init__(self, typestr, group, unique=False, *args):

        YAPLCLocationBase.__init__(self)

        self._descriptive = None

        if len(typestr) != 2:
            raise ParseError(_("Incorrect type coding %s") % typestr)

        if typestr[0] not in YAPLCLocationTypes:
            raise ParseError(_("Type %s not recognized") % typestr[0])
        else:
            self._type = typestr[0]

        if typestr[1] not in YAPLCLocationDataTypes:
            raise ParseError(_("Data type %s not recognized") % typestr[1])
        else:
            self._datatype = typestr[1]

        for p in args:
            if str(p).startswith('['):
                # this is named parameter
                param = str(p).rstrip(']').lstrip('[')
                name, value = param.split(':')
                # print name, value
                self.addParameters(value, name)
                self._parametrized = True
                if not self._descriptive:
                    raise ParseError(_("Parametrized locations requires descriptive name"))
            elif str(p).startswith('"'):
                # descriptive name of location
                self._descriptive = str(p).rstrip('"').lstrip('"')
                if any(s in self._descriptive for s in YAPLCNameIllegal):
                    raise ParseError(_("Illegal symbol in group's name: %s") % self._descriptive)
            elif str(p).isdigit():
                self.addParameters(p)
            else:
                # this is the unnamed range or items
                self.addParameters(p)

        self._unique = unique
        self._group = group  # group to this location

    def type(self):
        return self._type

    def datatype(self):
        return self._datatype

    def unique(self):
        return self._unique

    def descriptive(self):
        return self._descriptive

    def __str__(self):
        return '{0}{1}'.format(self._type, self._datatype)

    def name(self):
        return self.__str__()

    def __repr__(self):
        return self.__str__()


class YAPLCGroup(YAPLCLocationBase):
    """
    YAPLC group abstraction allow to store info about group extracted from DSL
    """

    def __init__(self, name, values=None, unique=False, parent=None, *args):

        YAPLCLocationBase.__init__(self)

        self._name = str(name).rstrip('"').lstrip('"')

        if any(s in self._name for s in YAPLCNameIllegal):
            raise ParseError(_("Illegal symbol in group's name: %s") % self._name)

        if len(values) > 1:
            raise ParseError(_("Too many parameters for group: %s") % self._name)

        for v in values:
            if str(v).startswith('['):
                param = str(v).rstrip(']').lstrip('[')
                name, value = param.split(':')
                self.addParameters(value, name)
                self._parametrized = True
            else:
                self.addParameters(v)

        self._unique = unique
        self._locations = list()
        self._parent = parent
        self._children = list()

    def name(self):
        return self._name

    def group(self):
        return None

    def append(self, location):
        self._locations.append(location)

    def locations(self):
        return self._locations

    def getlocation(self, name):
        for loc in self._locations:
            if loc.name() == name or loc.descriptive() == name:
                return loc

        return None

    def children(self):
        return self._children

    def unique(self):
        return self._unique

    def parent(self):
        return self._parent

    def hasParametrized(self):
        for child in self._children:
            if child.parametrized():
                return True
            else:
                return child.hasParametrized()

        for loc in self._locations:
            if loc.parametrized():
                return True

        return False

    def addsubgroup(self, group):
        self._children.append(group)


# YAPLC Extensions configuration parser
class YAPLCConfigParser:

    class yaplcparser(shlex.shlex):

        def __init__(self, instream=None, infile=None, posix=False):
            shlex.shlex.__init__(self, instream=instream, infile=infile, posix=posix)
            # add this tu usual shlex parser
            self.brackets = "[]"

        def read_token(self):
            quoted = False
            enclosed = False
            escapedstate = ' '
            while True:
                nextchar = self.instream.read(1)
                if nextchar == '\n':
                    self.lineno += 1
                if self.debug >= 3:
                    print("shlex: in state", repr(self.state), \
                        "I see character:", repr(nextchar))
                if self.state is None:
                    self.token = ''  # past end of file
                    break
                elif self.state == ' ':
                    if not nextchar:
                        self.state = None  # end of file
                        break
                    elif nextchar in self.whitespace:
                        if self.debug >= 2:
                            print("shlex: I see whitespace in whitespace state")
                        if self.token or (self.posix and quoted) or (self.posix and enclosed):
                            break  # emit current token
                        else:
                            continue
                    elif nextchar in self.commenters:
                        self.instream.readline()
                        self.lineno += 1
                    elif self.posix and nextchar in self.escape:
                        escapedstate = 'a'
                        self.state = nextchar
                    elif nextchar in self.wordchars:
                        self.token = nextchar
                        self.state = 'a'
                    elif nextchar in self.quotes:
                        if not self.posix:
                            self.token = nextchar
                        self.state = nextchar
                    elif self.whitespace_split:
                        self.token = nextchar
                        self.state = 'a'
                    elif nextchar in self.brackets:
                        self.token = nextchar
                        self.state = '['
                    else:
                        self.token = nextchar
                        if self.token or (self.posix and quoted) or (self.posix and enclosed):
                            break  # emit current token
                        else:
                            continue
                elif self.state in self.quotes:
                    quoted = True
                    if not nextchar:  # end of file
                        if self.debug >= 2:
                            print("shlex: I see EOF in quotes state")
                        # XXX what error should be raised here?
                        raise ValueError("No closing quotation")
                    if nextchar == self.state:
                        if not self.posix:
                            self.token = self.token + nextchar
                            self.state = ' '
                            break
                        else:
                            self.state = 'a'
                    elif self.posix and nextchar in self.escape and \
                                    self.state in self.escapedquotes:
                        escapedstate = self.state
                        self.state = nextchar
                    else:
                        self.token = self.token + nextchar
                elif self.state in self.brackets:
                    enclosed = True
                    if not nextchar:  # end of file
                        if self.debug >= 2:
                            print("shlex: I see EOF in quotes state")
                        # XXX what error should be raised here?
                        raise ValueError("No closing bracket")
                    if nextchar == ']':  # closing bracket
                        if not self.posix:
                            self.token = self.token + nextchar
                            self.state = ' '
                            break
                        else:
                            self.state = 'a'
                    elif self.posix and nextchar in self.escape and \
                                    self.state in self.escapedquotes:
                        escapedstate = self.state
                        self.state = nextchar
                    else:
                        self.token = self.token + nextchar
                elif self.state in self.escape:
                    if not nextchar:  # end of file
                        if self.debug >= 2:
                            print("shlex: I see EOF in escape state")
                        # XXX what error should be raised here?
                        raise ValueError("No escaped character")
                    # In posix shells, only the quote itself or the escape
                    # character may be escaped within quotes.
                    if escapedstate in self.quotes and \
                                    nextchar != self.state and nextchar != escapedstate:
                        self.token = self.token + self.state
                    self.token = self.token + nextchar
                    self.state = escapedstate
                elif self.state == 'a':
                    if not nextchar:
                        self.state = None  # end of file
                        break
                    elif nextchar in self.whitespace:
                        if self.debug >= 2:
                            print("shlex: I see whitespace in word state")
                        self.state = ' '
                        if self.token or (self.posix and quoted) or (self.posix and enclosed):
                            break  # emit current token
                        else:
                            continue
                    elif nextchar in self.commenters:
                        self.instream.readline()
                        self.lineno += 1
                        if self.posix:
                            self.state = ' '
                            if self.token or (self.posix and quoted) or (self.posix and enclosed):
                                break  # emit current token
                            else:
                                continue
                    elif self.posix and nextchar in self.quotes:
                        self.state = nextchar
                    elif self.posix and nextchar in self.escape:
                        escapedstate = 'a'
                        self.state = nextchar
                    elif nextchar in self.wordchars or nextchar in self.quotes \
                            or self.whitespace_split or nextchar in self.brackets:
                        self.token = self.token + nextchar
                    else:
                        self.pushback.appendleft(nextchar)
                        if self.debug >= 2:
                            print("shlex: I see punctuation in word state")
                        self.state = ' '
                        if self.token:
                            break  # emit current token
                        else:
                            continue
            result = self.token
            self.token = ''
            if self.posix and not quoted and not enclosed and result == '':
                result = None
            if self.debug > 1:
                if result:
                    print("shlex: raw token=" + repr(result))
                else:
                    print("shlex: raw token=EOF")
            return result

    @staticmethod
    def parseline(line):
        """Parse single line read from settings file

        :param line: Line of text (string) to parse
        :return: list of tokens split from line
        """
        lexer = YAPLCConfigParser.yaplcparser(line)
        lexer.commenters = '#'
        lexer.wordchars += '.():,'

        return list(lexer)

    def groups(self):
        """Get groups parsed from configuration file

        :return: list of groups keys
        """
        return list(self._groups.values())

    def getgroup(self, name):

        def findgroup(name, group):
            if name == group.name():
                return group

            for g in group.children():
                if g.name() == name:
                    return g

                if len(g.children()) > 0:
                    return findgroup(name, g)

            return None

        group = None
        if name in self._groups:
            # in root groups
            group = self._groups[name]
        else:
            # in nested groups
            for g in list(self._groups.values()):
                group = findgroup(name, g)
                if group is not None:
                    break

        return group

    def getlocations(self, group):
        """Get locations of specified group

        :param group: Group of locations
        :return: Locations list
        """
        if group in self._groups:
            return self._groups[group].locations()
        else:
            return None

    def addgroup(self, group):
        if group not in self._groups:
            self._groups[group.name()] = group

    def addlocation(self, group, location):
        if group in self._groups:
            self._groups.get(group).append(location)

    def __init__(self, dict_type=collections.defaultdict):
        self._dict = dict_type
        self._groups = self._dict()

    def fparse(self, fileName = None):
        if fileName is not None:
            try:
                with open(fileName) as f:
                    currentGroup = None
                    for line in f:
                        tokens = YAPLCConfigParser.parseline(line)

                        if tokens:
                            if tokens[0] == 'UGRP' or tokens[0] == 'GRP':
                                rest = []

                                if len(tokens) < 3:
                                    raise ParseError("Arguments number for group less than required")
                                elif len(tokens) >= 3:
                                    rest = tokens[2:]

                                # begin of the unique group/end of previous
                                if tokens[1] in self._groups:
                                    if self._groups[tokens[1]].unique():
                                        raise ParseError(_("Has the same unique group %s") % tokens[1])

                                if currentGroup is not None:
                                    grp = YAPLCGroup(tokens[1], rest, (tokens[0] == 'UGRP'), currentGroup)
                                    currentGroup.addsubgroup(grp)
                                else:
                                    grp = YAPLCGroup(tokens[1], rest, (tokens[0] == 'UGRP'), None)
                                    self.addgroup(grp)  # also add to flat root groups table

                                currentGroup = grp

                            elif tokens[0] == 'LOC' or tokens[0] == 'ULOC':
                                # non-unique location description
                                if currentGroup is None:
                                    raise ParseError(_("Location %s without group") % tokens[0])
                                if currentGroup.unique():
                                    loc = YAPLCLocation(tokens[1], currentGroup,
                                                        (tokens[0] == 'ULOC'), *tokens[2:])
                                else:
                                    # non-unique group could have no GID and parameters only
                                    loc = YAPLCLocation(tokens[1], currentGroup,
                                                        (tokens[0] == 'ULOC'), *tokens[2:])
                                currentGroup.append(loc)

                            elif tokens[0] == 'ENDGRP':
                                # close current group and try to return to parent group
                                if currentGroup is None:
                                    raise ParseError(_("Illegal end of group"))

                                currentGroup = currentGroup.parent()

                            else:
                                raise ParseError(_("Illegal instruction: %s") % tokens[0])

                    if currentGroup is not None:
                        raise ParseError(_("Group %s has not been closed properly!") % currentGroup.name())

            except IOError:
                raise ParseError(_("No template file for current target"))

    def GetPlcInputInterfaceInfos(self):
        return self.GetXmlExtensionsInfos(direction="input")

    def GetPlcOutputInterfaceInfos(self):
        return self.GetXmlExtensionsInfos(direction="output")

    def GetPlcMemoryInterfaceInfos(self):
        return self.GetXmlExtensionsInfos(direction="memory")

    def GetXmlExtensionsInfos(self, xml_file_name="extensions.xml", direction=""):
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'yaplctargets', 'plm2004', xml_file_name)

        with open(path) as fobj:
            xml = fobj.read()
        root = etree.fromstring(xml)
        if etree.iselement(root):
            return self.GetInfosExtensions(root, direction)

    def GetInfosExtensions(self, element, direction=""):
        d = list()
        #flag = False
        for ch in element.getchildren():
            flag = True
            if direction != "":
                if ch.tag == "interface":
                    flag = ch.get("direction") == direction.lower()
                elif ch.tag == "variable":
                    #name = ch.get("name")
                    flag = YAPLCLocationTepesDict[direction.lower()] in ch.get("name")
            if flag:
                infos = dict()
                infos[ch.tag] = {key: ch.get(key) for key in ch.keys()}
                if len(ch.getchildren()) > 0:
                    if ch.tag != "variable":
                        infos[ch.tag]["Children"] = self.GetInfosExtensions(ch, direction)
                    else:
                        infos[ch.tag]["Type"] = ch.getchildren()[0].tag
                d.append(infos.copy())
        return d


'''
def GetInfosExtensions(element, direction=""):
    d = list()
    flag = False
    for ch in element.getchildren():
        if direction != "":
            if ch.tag == "interface":
                flag = ch.get("direction") == direction
        if flag:
            infos = dict()
            infos[ch.tag] = {key: ch.get(key) for key in ch.keys()}
            if len(ch.getchildren()) > 0:
                if ch.tag != "variable":
                    infos["Children"] = GetInfosExtensions(ch, direction)
                else:
                    infos["Type"] = ch.getchildren()[0].tag
            d.append(infos)
    return d
'''


def PrintGpoup(groups):
    for grp in groups:#parser.groups():
        print("\n\n")
        print("\nname:\t" )
        print(grp.name())
        print("\nparameters:\t")
        print(grp.parameters())
        ch_grp = grp.children()
        if ch_grp is not None:
            PrintGpoup(ch_grp)
        locations = grp.locations()
        if len(locations) > 0:
            print("\nlocations:\t")
            print(grp.locations())

def GetChannels(parameters):
    if isinstance(parameters, list):
        parameters = parameters[0]
    return str(parameters["min"]) + ".." + str(parameters["max"])

def Variable(root, children, interface_name):
    locations = children.locations()
    if len(locations) > 0:
        for i, location in enumerate(locations):
            sub_element = etree.Element("variable")
            loc_name = location.type() + location.datatype()
            sub_element.set("name", loc_name)
            sub_element.set("id", str(i+1))
            type_var = ""
            datatype = location.datatype()
            if datatype in ["D", "L"]:
                #type_var = input(f"Type location {interface_name} {children.name()} {loc_name} {i+1}: ")
                type_var = "input"
                if datatype == "D":
                    type_var = "DWORD"
                else:
                    type_var = "LWORD"
            else:
                type_var = ""
                if datatype == "X":
                    type_var = "BOOL"
                elif datatype == "B":
                    type_var = "BYTE"
                elif datatype == "W":
                    type_var = "WORD"
            sub_element.set("max", "10")#input("max: "))
            sub_element.set("min", "1")#input("min: " ))
            etree.SubElement(sub_element, type_var)

            root.append(sub_element)


def Children(root, children, i, interface_name):

    children_xml = etree.Element("mode")
    try:
        children_xml.set("name", children.name())
    except:
        pass
    children_xml.set("id", str(i))
    children_children = children.children()
    if len(children_children) > 0:
        for ch in children_children:
            Children(children_xml, ch, i, interface_name)
    root.append(children_xml)
    Variable(children_xml, children, interface_name)


def GenerateVariableXml(root, childrens, interface_name):
    i = 1
    if isinstance(childrens, list):
        for children in childrens:
            Children(root, children, i, interface_name)
            i += 1
    else:
        Children(root, childrens, i, interface_name)


def Generate_XML_config(groups, xml_file_name="extensions.xml"):
    target = etree.Element("target")
    target.set("name", "plm2004")
    for i, grp in enumerate(groups):
        root = etree.Element("interface")
        root.set("name", grp.name())
        root.set("id", str(i+1))
        root.set("direction", "memory")
        children = grp.children()[0]
        if children is not None:
            if children.name() == "Channel":
                root.set("Channel", GetChannels(children.parameters()))
                GenerateVariableXml(root, children.children(), grp.name())
            else:

                GenerateVariableXml(root, children, grp.name())
            Variable(root, children, grp.name())
        if root is not None:
            target.append(root)
    if target is not None:
        path = os.path.join(os.path.dirname(__file__),
                            '..', 'yaplctargets', 'plm2004', xml_file_name)
        f = open(path, "w")
        xml_text = "<?xml version=\"1.0\"?>\n" + etree.tostring(target, pretty_print=True).decode("utf-8")
        f.writelines(xml_text)
        f.close()

def GetInfosExtensions(element, direction=""):
    d = list()
    flag = False
    for ch in element.getchildren():
        if direction != "":
            if ch.tag == "interface":
                flag = ch.get("direction") == direction
        if flag:
            infos = dict()
            infos[ch.tag] = {key: ch.get(key) for key in ch.keys()}
            if len(ch.getchildren()) > 0:
                if ch.tag != "variable":
                    infos["Children"] = GetInfosExtensions(ch, direction)
                else:
                    infos["Type"] = ch.getchildren()[0].tag
            d.append(infos)
    return d

def Parse(root, child):
    if len(child) == 0:
        return
    for elem in child:
        test = elem.keys()
        test2 = elem.tag
        Parse(child, elem.getchildren())


def parseXML_cfg(xml_file_name="extensions.xml"):
    path = os.path.join(os.path.dirname(__file__),
                        '..', 'yaplctargets', 'plm2004', xml_file_name)

    with open(path) as fobj:
        xml = fobj.read()
    root = etree.fromstring(xml)
    Parse(root, root.getchildren())
    ecxtensions_input = GetInfosExtensions(root, "input")
    ecxtensions_output = GetInfosExtensions(root, "output")
    ecxtensions_memory = GetInfosExtensions(root, "memory")

import re

if __name__ == '__main__':
    from gettext import gettext as _

    parser = YAPLCConfigParser()
    path = os.path.join(os.path.dirname(__file__),
                        '..', 'yaplctargets', 'plm2004',
                        r'extensions.cfg')
    try:
        parser.fparse(path)
    except ParseError as pe:
        print(pe.message())

    groups = parser.groups()

    PrintGpoup(groups)

    #Generate_XML_config(groups)

    parseXML_cfg("extensions copy.xml")

    test = re.split(r'\W+', '0..123')

    print(test)