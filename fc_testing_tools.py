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
