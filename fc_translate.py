from lxml import etree

class CyclusFuelCycle(object):
    """ simple holding class for the fuel cycle in cyclus input. underlying
    representation is in xml.
    """
    def __init__(self, info, initial_conditions, growth):
        self.info = info
        self.initial_conditions = initial_conditions
        self.growth = growth

class SimulationDefaults(object):
    """ A holding class to be a singular point to define all default parameters
    used in the translation.
    """
    def __init__(self):
        self.startmonth = "1"
        self.startyear = "2000"
        self.simstart = "0"
        self.decay = "2"

class JsonFuelCycleParser(object):
    """ A parser that accepts a python-based json object representation of
    the fuel cycle from the FCS benchmark specification language and returns a
    cyclus-based representation of the fuel cycle
    """
    def __init__(self, description):
        self.__description = description

    def __duration(self):
        units = self.__description["attributes"]["grid"]
        time = self.__description["constraints"]["grid"]
        diff = time[1] - time[0]
        if units is "years":
            diff *= 12
        return diff

    def __constructSimInfo(self):
        root = etree.Element("control")
        duration = etree.SubElement(root,"duration")
        duration.text = str(self.__duration())
        defaults = SimulationDefaults()
        startmonth = etree.SubElement(root,"startmonth")
        startmonth.text = defaults.startmonth
        startyear = etree.SubElement(root,"startyear")
        startyear.text = defaults.startyear
        simstart = etree.SubElement(root,"simstart")
        simstart.text = defaults.simstart
        decay = etree.SubElement(root,"decay")
        decay.text = defaults.decay
        return root

    def __constructInitialCondition(self):
        ics = []
        return ics

    def __constructGrowth(self):
        demands = []
        return demands

    def parse(self):
        """ Takes as input a python dictionary of the fuel cycle as specified in
        the benchmark specification language. returns the corresponding
        CyclusFuelCycle object.
        """
        info = self.__constructSimInfo()
        ics = self.__constructInitialCondition()
        growth = self.__constructGrowth()
        return CyclusFuelCycle(info, ics, growth)
