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
        self._name = name
        self._description = description

    def _getProduction(self):
        """returns 0 by default, subclasses can override"""
        return 0.0

    def _getNode(self):
        """returns None by default, subclasses can override"""
        return None

    def parse(self):
        fac_t = self._description["type"]
        imports = self._description["inputs"]
        exports = self._description["outputs"]
        production = self._getProduction()
        node = self._getNode()
        return CyclusFacility(self._name,fac_t,imports,exports,production,node)

class JsonRepositoryParser(JsonFacilityParser):
    """ A parser that accepts a python-based json object representation of
    repositories from the FCS benchmark specification language and returns a
    cyclus-based representation of the facility.

    Repositories have no notion of "production", so only the node formation
    functionality is overwritten.
    """
    def _getNode(self):
        # initialize parameters
        inputs = self._description["inputs"]
        if "lifetime" in self._description["constraints"]:
            lifetime = self._description["constraints"]["lifetime"]
        else:
            lifetime = None
        if "capacity" in self._description["constraints"]:
            capacity = self._description["constraints"]["capacity"]
        else:
            capacity = None
        
        return self.__constructNode(inputs,lifetime,capacity)

    def __constructNode(self,inputs,lifetime,capacity):
        root = etree.Element("facility")
        elname = etree.SubElement(root,"name")
        elname.text = self._name
        if lifetime is not None:
            ellife = etree.SubElement(root,"lifetime")
            ellife.text = str(lifetime)    
        elmodel = etree.SubElement(root,"model")
        elclass = etree.SubElement(elmodel,"SinkFacility")
        elin = etree.SubElement(elclass,"input")
        elcommods = etree.SubElement(elin,"commodities")
        for i in range(len(inputs)):
            elincommod = etree.SubElement(elcommods,"incommodity")
            elincommod.text = inputs[i]
        if capacity is not None:
            elcapacity = etree.SubElement(elin,"input_capacity")
            elcapacity.text = str(capacity)
        for i in range(len(inputs)):
            elincommod = etree.SubElement(root,"incommodity")
            elincommod.text = inputs[i]
        return root

