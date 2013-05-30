import fac_translate as facxl
import matl_translate as matxl
import fc_translate as fcxl

# json/xml packages
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree


class CyclusTransformer(object):
    """This class takes a set of conditioned input parameters for materials,
    facilities, and general fuel cycle information from helper classes and
    compiles them into a Cyclus input file.
    """
    
    def __init__(self, mats, facs, fc):
        self.mats = mats
        self.facs = facs
        self.fc = fc
        self.commod_nodes, self.market_nodes = self.getResourceNodes()
        self.sources = []#self.constructSources()
        self.inst = []#self.constructInstNode()
        self.region = []#self.constructRegionNode()

    def getResourceNodes(self):
        commods, markets = [], []
        for mat in self.mats:
            cnode = etree.Element("commodity")
            cname = etree.SubElement(cnode,"name")
            cname.text = mat.name
            mnode = etree.Element("market")
            mname = etree.SubElement(mnode,"name")
            mname.text = mat.name + "_market"
            mcommod = etree.SubElement(mnode,"mktcommodity")
            mcommod.text = mat.name 
            mmodel = etree.SubElement(mnode,"model")
            mclass = etree.SubElement(mmodel,"NullMarket")
            commods.append(cnode)
            markets.append(mnode)
        return commods, markets

    def translate(self):
        root = etree.Element("simulation")
        root.append(self.fc.info)
        for node in self.commod_nodes: root.append(node)
        for node in self.market_nodes: root.append(node)
        for mat in self.mats: root.append(mat.node)
        for fac in self.facs: root.append(fac.node)
        root.append(self.region)
        return root

if __name__ == "__main__":
    
    f = open("../tests/input/test_full.json")
    obj = json.load(f)
    json_facs = obj["facilities"]
    json_matls = obj["materials"]
    json_fc = obj["fuelCycle"]

    mats = matxl.readMaterials(json_matls)
#    for mat in mats: print mat

    facs = facxl.readFacs(json_facs)
#    for fac in facs: print fac

    fc = fcxl.JsonFuelCycleParser(json_fc)
#    print fc.parse()

    xformer = CyclusTransformer(mats, facs, fc)
    for node in xformer.commod_nodes: print etree.tostring(node, pretty_print = True)
    for node in xformer.market_nodes: print etree.tostring(node, pretty_print = True)
    # cycl_matls = [JsonMaterialParser(name, descr).parse() \
    #                   for name, descr in json_matls.iteritems()]

    # for mat in cycl_matls: print mat

    # fac_t_map = {"lwr_reactor":"reactor","repository":"repository"}
    # cycl_fc = JsonFuelCycleParser(json_fc, ExtraneousFCInfo(fac_t_map)).parse()
    # print cycl_fc
    
    # for name, descr in json_facs.iteritems():
    #     print name, descr 

    # cycl_facs = [parse_fac(name, descr) \
    #                  for name, descr in json_facs.iteritems()]

    # for fac in cycl_facs: print fac
