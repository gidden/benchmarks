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
        self.sources = self.constructSources()
        for source in self.sources: self.facs.append(source)
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

    def constructSource(self, commod):
        name = "source_" + commod
        root = etree.Element("facility")
        nname = etree.SubElement(root, "name")
        nname.text = name
        model = etree.SubElement(root, "model")
        classn = etree.SubElement(model, "SourceFacility")
        output = etree.SubElement(classn, "output")
        outputc = etree.SubElement(output, "outcommodity")
        outputc.text = commod
        outputr = etree.SubElement(output, "recipe")
        outputr.text = commod
        outcommod = etree.SubElement(root, "outcommodity")
        outcommod.text = commod
        return facxl.CyclusFacility(name, "source", [], [commod], None, root)

    def getSourceCommods(self):
        all_imports = []
        all_exports = []
        for fac in self.facs:
            all_imports += fac.imports
            all_exports += fac.exports
        for export in all_exports:
            if export in all_imports: all_imports.remove(export)
        return all_imports

    def constructSources(self):
        sources = []
        commods = self.getSourceCommods()
        for commod in commods: 
            sources.append(self.constructSource(commod))
        return sources

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
    # for node in xformer.commod_nodes: print etree.tostring(node, pretty_print = True)
    # for node in xformer.market_nodes: print etree.tostring(node, pretty_print = True)
    for source in xformer.sources: print etree.tostring(source.node, pretty_print = True)
