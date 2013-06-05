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
        
    def __str__(self):
        return "Name: " + self.name + "\n" \
            + "Node: \n" + etree.tostring(self.node, pretty_print = True)

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
        self._fac_t = description["metadata"]["type"]
        # a useful dictionary for parameter values described as lists in the
        # json implementation
        self._params = {} 
        self._setTags()
        self._setParams()

    def _setTags(self):
        """Subclasses should override this function to set up the json
        implementation-specific names for parameters member"""
        pass
    
    def _setParams(self):
        """Subclasses should override this function to set up the _params
        member"""
        pass    

    def _getProduction(self):
        """returns 0 by default, subclasses can override"""
        return 0.0

    def _getNode(self):
        """returns None by default, subclasses can override"""
        return None

    def _convertLifetime(self, value, units):
        """converts a lifetime value into the correct cyclus units"""
        years = ["year", "years"]
        factor = 1
        if units in years:
            factor = 12
        return value * factor

    def parse(self):
        try:
            imports = self._description["inputs"]
        except KeyError:
            imports = []
        try:
            exports = self._description["outputs"]
        except KeyError:
            exports = []
        node = self._getNode()
        production = self._getProduction()
        return CyclusFacility(self._name,self._fac_t,imports,exports,production,node)

class JsonEnrichmentParser(JsonFacilityParser):
    """ A parser that accepts a python-based json object representation of
    enrichment facilities from the FCS benchmark specification language and
    returns a cyclus-based representation of the facility.
    """

    def __init__(self, name, description):
        JsonFacilityParser.__init__(self,name,description)

    def _setTags(self):
        """These tags correspond to the json implementation's parameter naming
        conventions.  They are defined here so that they only need to be defined
        in one place.
        """
        self.tag_tails = "tailsFraction"
        self.tag_life = "lifetime"
        self.tag_capacity = "capacity"

    def _setParams(self):
        """The json spec implementation lists parameter values as a list. It's
        easier to use them as a dictionary, so we'll do that.
        """
        constrs = self._description["constraints"]
        for constr in constrs:
            self._params[constr[0]] = constr[1]

    def _getNode(self):
        # initialize parameters
        inputs = self._description["inputs"]
        if len(inputs) > 1: raise NotImplementedError("Enrichment facs can't take more than one input.")
        outputs = self._description["outputs"]
        if "lifetime" in self._description["attributes"]:
            lifetime = self._convertLifetime(int(self._params[self.tag_life]), \
                                                 self._description["attributes"][self.tag_life][1])
        else:
            lifetime = None
        if self.tag_capacity in self._description["attributes"]:
            capacity = float(self._params[self.tag_capacity])
        else:
            capacity = None
        if self.tag_tails in self._description["attributes"]:
            tails = float(self._params[self.tag_tails]) / 100 # e.g. 80% to 0.8
        else:
            tails = None
        
        return self.__constructNode(inputs, outputs, lifetime, capacity, tails)

    def _getProduction(self):
        """returns 0 by default, subclasses can override"""        
        if self.tag_capacity in self._params:
            return self._params[self.tag_capacity]
        else:
            return 0.0

    def __constructNode(self, inputs, outputs, lifetime, capacity, tails):
        root = etree.Element("facility")
        elname = etree.SubElement(root,"name")
        elname.text = self._name
        if lifetime is not None:
            ellife = etree.SubElement(root,"lifetime")
            ellife.text = str(lifetime)    
        elmodel = etree.SubElement(root,"model")
        elclass = etree.SubElement(elmodel,"EnrichmentFacility")
        
        elin = etree.SubElement(elclass,"input")
        elincommod = etree.SubElement(elin,"incommodity")
        elincommod.text = inputs[0] # hack
        elinrecipe = etree.SubElement(elin,"inrecipe")
        elinrecipe.text = inputs[0] # hack
        
        elout = etree.SubElement(elclass,"output")
        eloutcommod = etree.SubElement(elout,"outcommodity")
        eloutcommod.text = outputs[0] # hack
        eltails = etree.SubElement(elout,"tails_assay")
        eltails.text = str(tails)
        
        if capacity is not None:
            elcapacity = etree.SubElement(elin,"input_capacity")
            elcapacity.text = str(capacity)
        for i in range(len(inputs)):
            elincommod = etree.SubElement(root,"incommodity")
            elincommod.text = inputs[i]
        for i in range(len(outputs)):
            eloutcommod = etree.SubElement(root,"outcommodity")
            eloutcommod.text = outputs[i]
        return root

class JsonRepositoryParser(JsonFacilityParser):
    """ A parser that accepts a python-based json object representation of
    repositories from the FCS benchmark specification language and returns a
    cyclus-based representation of the facility.
    """
    def __init__(self, name, description):
        JsonFacilityParser.__init__(self,name,description)

    def _setTags(self):
        """These tags correspond to the json implementation's parameter naming
        conventions.  They are defined here so that they only need to be defined
        in one place.
        """
        self.tag_capacity = "capacity"
        self.tag_life = "lifetime"

    def _setParams(self):
        """The json spec implementation lists parameter values as a list. It's
        easier to use them as a dictionary, so we'll do that.
        """
        constrs = self._description["constraints"]
        for constr in constrs:
            self._params[constr[0]] = constr[1]

    def _getNode(self):
        # initialize parameters
        inputs = self._description["inputs"]
        if "lifetime" in self._description["attributes"]:
            lifetime = self._convertLifetime(int(self._params[self.tag_life]), \
                                                 self._description["attributes"][self.tag_life][1])
        else:
            lifetime = None
        if self.tag_capacity in self._description["attributes"]:
            capacity = float(self._params[self.tag_capacity])
        else:
            capacity = None
        
        return self.__constructNode(inputs,lifetime,capacity)

    def _getProduction(self):
        """returns 0 by default, subclasses can override"""        
        if self.tag_capacity in self._description["constraints"]:
            return self._description["constraints"][self.tag_capacity]
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
    def __init__(self, refuel_time = 0, prod_t = None): 
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
        self._refuel_time = extra_info.refuel_time
        self._prod_t = extra_info.prod_t

    def _setTags(self):
        """These tags correspond to the json implementation's parameter naming
        conventions.  They are defined here so that they only need to be defined
        in one place.
        """
        self.tag_eff = "efficiency"
        self.tag_pwr = "thermalPower"
        self.tag_loading = "coreLoading"
        self.tag_batch_n = "batches"
        self.tag_cycle = "cycleLength"
        self.tag_life = "lifetime"
        self.tag_bu = "burnup"
        self.tag_storage = "storageTime"
        self.tag_cooling = "coolingTime"

    def _setParams(self):
        """The json spec implementation lists parameter values as a list. It's
        easier to use them as a dictionary, so we'll do that.
        """
        constrs = self._description["constraints"]
        for constr in constrs:
            self._params[constr[0]] = constr[1]

    def _getProduction(self):
        eff = float(self._params[self.tag_eff])
        power = eff * float(self._params[self.tag_pwr])
        return power
    
    def _getNode(self):
        # get fuels
        imports = self._description["inputs"]
        exports = self._description["outputs"]
        inrecipes = imports
        outrecipes = exports
        in_core = float(self._params[self.tag_loading])
        out_core = in_core
        batches = int(self._params[self.tag_batch_n])
        burnup = float(self._params[self.tag_bu])        
        fuels = ReactorFuels(imports,inrecipes,in_core,
                             exports,outrecipes,out_core,batches,burnup)
        
        cycle = getCycleLength(self._description["attributes"], \
                                   self._description["constraints"])
        lifetime = self._convertLifetime(int(self._params[self.tag_life]), \
                                             self._description["attributes"][self.tag_life][1])
        storage = int(self._params[self.tag_storage])
        cooling = int(self._params[self.tag_cooling])
        schedule = ReactorSchedule(cycle,self._refuel_time,lifetime,storage,cooling)
        
        eff = float(self._params[self.tag_eff]) / 100.0
        powerunits = self._description["attributes"][self.tag_pwr][1]
        capacity = round(getPower(powerunits[:2], eff * float(self._params[self.tag_pwr])))
        if self._prod_t is None:
            self._prod_t = "power"
        production = ReactorProduction(self._prod_t,capacity,eff)
        generator = ReactorGenerator(self._name,self._fac_t,fuels,schedule,production)
        return generator.node()

def getParser(name, descr):
    fac_t = descr["metadata"]["type"]
    if fac_t == "repository":
        return JsonRepositoryParser(name, descr)
    if fac_t == "enrichment":
        return JsonEnrichmentParser(name, descr)
    elif fac_t == "reactor":
        prod_t = name + "_power" #default
        info = CyclusReactorInfo(prod_t = prod_t)
        return JsonReactorParser(name, descr, info)
    else:
        raise TypeError("Facility type " + fac_t + " is not supported.")

def readFacs(json_obj):
    facs = []
    for name, descr in json_obj.iteritems(): 
        parser = getParser(name, descr)
        fac = parser.parse()
        facs.append(fac)
    return facs

def getPower(units, value):
    gw = ["gw"]
    if units.lower() in gw:
        value *= 1000
    print units, value
    return value

def getCycleLength(attributes, constraints):
    
    clunits = attributes["cycleLength"][1].lower()
    for item in constraints:
        if item[0] == "cycleLength": clval = int(item[1])
        if item[0] == "capacityFactor": cfval = float(item[1])

    if clval is None: raise ValueError("No cycle length value found")

    months = ["month", "months"]
    years = ["year", "years"]
    efpd = ["efpd", "efpds"]
    if clunits in months: return clval
    elif clunits in years: return clval * 12
    elif clunits in efpd:
        return int( round( clval * (cfval / 100) / 365 * 12 ))
    else: raise TypeError("Unsupported Cycle Length units: " + clunits)
