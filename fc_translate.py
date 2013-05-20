from lxml import etree

class CyclusFuelCycle(object):
    """ simple holding class for the fuel cycle in cyclus input. underlying
    representation is in xml.
    """
    def __init__(self, info, initial_conditions, growth):
        self.info = info
        self.initial_conditions = initial_conditions
        self.growth = growth

class JsonFuelCycleParser(object):
    """ A parser that accepts a python-based json object representation of
    the fuel cycle from the FCS benchmark specification language and returns a
    cyclus-based representation of the fuel cycle
    """
    def __init__(self, description):
        self.__description = description

    def parse(self):
        """ Takes as input a python dictionary of the fuel cycle as specified in
        the benchmark specification language. returns the corresponding
        CyclusFuelCycle object.
        """
        info = self.__constructSimInfo()
        ics = self.__constructInitialCondition()
        growth = self.__constructGrowth()
        return CyclusFuelCycle(info, ics, growth)

    def __constructSimInfo(self):
        root = etree.Element("simulation")
        return root

    def __constructInitialCondition(self):
        ics = []
        return ics

    def __constructGrowth(self):
        demands = []
        return demands
