from lxml import etree

class SimInfo(object):
    """This class provides xml and json descriptions of the high level
    simulation description parameters
    """
    def __init__(self, time_variables):
        # variables
        self.units = time_variables[0]
        self.values = time_variables[1]

        # defaults
        self.startmonth = "1"
        self.startyear = "2000"
        self.simstart = "0"
        self.decay = "2"        

    def add_to_description(self,description):
        description["attributes"]["grid"] = self.units
        description["constraints"]["grid"] = self.values
        
    def get_xml(self):
        diff = self.values[1] - self.values[0]
        if self.units is "years":
            diff *= 12
        root = etree.Element("control")
        duration = etree.SubElement(root,"duration")
        duration.text = str(diff)
        startmonth = etree.SubElement(root,"startmonth")
        startmonth.text = self.startmonth
        startyear = etree.SubElement(root,"startyear")
        startyear.text = self.startyear
        simstart = etree.SubElement(root,"simstart")
        simstart.text = self.simstart
        decay = etree.SubElement(root,"decay")
        decay.text = self.decay
        return root

class TestFCFac(object):
    """A holder class for testing facilities. It holds all the information
    needed to set up  the various xml nodes and json objects.
    """
    def __init__(self,name,number,fac_t,agent_t): 
        self.name = name 
        self.number = number 
        self.fac_t = fac_t 
        self.agent_t = agent_t

    def __str__(self):
        return self.name

class InitialConditions(object):
    """This class provides xml and json descriptions of the simulation initial
    condition parameters
    """
    def __init__(self, initial_facs):
        # variables
        self.fac_list = initial_facs

    def add_to_description(self,description):
        dic = description["attributes"]
        if len(self.fac_list) > 0:
            dic["initialConditions"] = {}
            for fac in self.fac_list:
                dic["initialConditions"][fac.name] = fac.number
        
        
    def get_xml(self):
        xml_ics = []
        for fac in self.fac_list:
            root = etree.Element("entry")
            prototype = etree.SubElement(root,"prototype")
            prototype.text = fac.agent_t
            number = etree.SubElement(root,"number")
            number.text = str(fac.number)
            xml_ics.append(root)
        return xml_ics

class TestFCGrowth(object):
    """A holder class for testing demand curves. It holds all the information
    needed to set up  the various xml nodes and json objects.
    """
    def __init__(self, name, units, facilities, time, demand_info): 
        self.name = name 
        self.units = units
        self.facilities = facilities
        self.time = time
        self.demand_info = demand_info

    def __str__(self):
        return self.name

class Growth(object):
    def __init__(self, params):
        self.params = params

    def __add_growth_period(self, dic, n, info):
        key = "period"+str(n)
        dic[key] = {"startTime": info[0], \
                        "slope": info[1]}
        if len(info) > 2:
            dic[key]["startValue"] = info[2]

    def add_to_description(self, description):
        attributes, constraints = {}, {}
        for demand in self.params:
            attributes[demand.name] = [demand.units, demand.facilities]
            growth = {}
            growth["type"] = demand.demand_info[0]
            for i in range(len(demand.demand_info)-1):
                self.__add_growth_period(growth,i+1,demand.demand_info[i+1])
            constraints[demand.name] = {"grid": demand.time, "growth": growth}
        description["attributes"]["demands"] = attributes
        description["constraints"]["demands"] = constraints

    def __add_growth_xml(self, node, info):
        start =  etree.SubElement(node,"start_time")
        start.text = str(info[0])
        text = str(info[1])
        if len(info) > 2:
             text += " " + str(info[2])
        else: 
            text += " 0"
        params = etree.SubElement(node,"parameters")
        params.text = text

    def get_xml(self):
        xml_growth = {}
        lvl = 0
        for demand in self.params:
            key = demand.name
            node_list = []
            for i in range(len(demand.demand_info)-1):
                node = etree.Element("demand")
                eltype = etree.SubElement(node,"type")
                eltype.text = demand.demand_info[0]
                self.__add_growth_xml(node,demand.demand_info[i+1])
                node_list.append(node)
            xml_growth[key] = node_list
        return xml_growth
