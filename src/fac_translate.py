from lxml import etree
from rxtr_helpers import ReactorFuels, ReactorSchedule, \
    ReactorProduction, ReactorGenerator

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

    def _getProduction(self):
        """returns 0 by default, subclasses can override"""        
        if "capacity" in self._description["constraints"]:
            return self._description["constraints"]["capacity"]
        else:
            return 0.0

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

class CyclusReactorInfo(object):
    """ a simple holding class for non-specification related information that is
    still required by Cyclus to define its input
    """
    def __init__(self, recipeGuide,refuel_time = 0, prod_t = None): 
        self.recipeGuide = recipeGuide
        self.refuel_time = refuel_time
        self.prod_t = prod_t

class JsonReactorParser(JsonFacilityParser):
    """ A parser that accepts a python-based json object representation of
    reactors from the FCS benchmark specification language and returns a
    cyclus-based representation of the facility.
    """
    
    def __init__(self, name, description, extra_info):
        """ Reactor Parser constructor. Note that the additional argument
        provides an interface to the additional information required to make a
        Cyclus reactor object that is not needed to specify a reactor object in
        the specification language.
        """
        JsonFacilityParser.__init__(self,name,description)
        self._recipeGuide = extra_info.recipeGuide
        self._refuel_time = extra_info.refuel_time
        self._prod_t = extra_info.prod_t
        self.tag_eff = "efficiency"
        self.tag_pwr = "thermalPower"
        self.tag_loading = "coreLoading"
        self.tag_batch_n = "batchNumber"
        self.tag_cycle = "cycleLength"
        self.tag_life = "lifetime"
        self.tag_bu = "burnup"
        self.tag_storage = "storageTime"
        self.tag_cooling = "coolingTime"


    def _getProduction(self):
        eff = float(self._description["constraints"][self.tag_eff])
        power = eff * float(self._description["constraints"][self.tag_pwr])
        return power
    
    def _getNode(self):
        # get fuels
        imports = self._description["inputs"]
        exports = self._description["outputs"]
        inrecipes = [self._recipeGuide[import_mat] for import_mat in imports]
        outrecipes = [self._recipeGuide[export_mat] for export_mat in exports]
        in_core = float(self._description["constraints"][self.tag_loading])
        out_core = in_core
        batches = int(self._description["constraints"][self.tag_batch_n])
        burnup = float(self._description["constraints"][self.tag_bu])        
        fuels = ReactorFuels(imports,inrecipes,in_core,
                             exports,outrecipes,out_core,batches,burnup)
        
        cycle = int(self._description["constraints"][self.tag_cycle])
        lifetime = int(self._description["constraints"][self.tag_life])
        storage = int(self._description["constraints"][self.tag_storage])
        cooling = int(self._description["constraints"][self.tag_cooling])
        schedule = ReactorSchedule(cycle,self._refuel_time,lifetime,storage,cooling)
        
        eff = float(self._description["constraints"][self.tag_eff])
        capacity = eff * float(self._description["constraints"][self.tag_pwr])
        if self._prod_t is None:
            self._prod_t = "power"
        production = ReactorProduction(self._prod_t,capacity,eff)
        fac_t = self._description["type"]
        generator = ReactorGenerator(self._name,fac_t,fuels,schedule,production)
        return generator.node()

