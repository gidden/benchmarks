from lxml import etree

class CyclusFacility(object):
    """ simple holding class for facilities in cyclus input. underlying
    representation is in xml.
    """
    def __init__(self,name,fac_t,imports,exports,production,node):
        self.name = name
        self.fac_t = fac_t
        self.imports = imports
        self.exports = exports
        self.production = production
        self.node = node

class JsonFacilityParser(object):
    """ A parser that accepts a python-based json object representation of
    facilities from the FCS benchmark specification language and returns a
    cyclus-based representation of the facility.

    This is a parent class that handles the translation of general
    facility-level parameters, i.e., the name, type, imports, and
    exports. Subclasses are relied upon to provide translation of specific
    facility-level parameters, e.g., the power production and node
    representation of a reactor.
    """
    def __init__(self, name, description):
        self.__name = name
        self.__description = description

    def __getProduction(self):
        """returns 0 by default, subclasses can override"""
        return 0.0

    def __getNode(self):
        """returns None by default, subclasses can override"""
        return None

    def parse(self):
        fac_t = self.__description["type"]
        imports = self.__description["inputs"]
        exports = self.__description["outputs"]
        production = self.__getProduction()
        node = self.__getNode()
        return CyclusFacility(self.__name,fac_t,imports,exports,production,node)

