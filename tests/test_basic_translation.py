# includes ---------------------------------------------------------------------
# get source files in path
import sys
sys.path.append("../src")

# local
from matl_translate import readMaterials
from fac_translate import readFacs
from compare_xml_trees import compare_nodes

# json/xml packages
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree

# test packages
from nose.tools import assert_true
import pprint
# ------------------------------------------------------------------------------

def test_mats_translation():
    json_data = open("input/test_mat.json")
    data = json.load(json_data)
    matls = readMaterials(data["materials"])

    tree = etree.parse("input/test_mat.xml")
    root = etree.Element("root")
    for mat in matls: root.append(mat.node)
    
    assert_true(compare_nodes(root, tree.getroot(), log = False))

def test_fac_translation():    
    json_data = open("input/test_fac.json")
    data = json.load(json_data)
    # note that data["recipes"] is an artifact required to print out the xml
    # nodes that will be fleshed out in higher-level objects
    facs = readFacs(data["facilities"], data["recipes"])
    
    tree = etree.parse("input/test_fac.xml")
    root = etree.Element("root")
    for fac in facs: root.append(fac.node)
    assert_true(compare_nodes(root, tree.getroot(), log = False))
