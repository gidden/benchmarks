# includes ---------------------------------------------------------------------
# get source files in path
import sys
sys.path.append("../src")

# local
from matl_translate import readMaterials
from fac_translate import readFacs
from compare_xml_trees import compare_nodes
from input_compiler import CyclusTranslator

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
    facs = readFacs(data["facilities"])
    
    tree = etree.parse("input/test_fac.xml")
    root = etree.Element("root")
    for fac in facs: root.append(fac.node)
    assert_true(compare_nodes(root, tree.getroot(), log = False))

def test_full_translation():
    json_data = open("input/test_full.json")
    data = json.load(json_data)
    xlator = CyclusTranslator(data)
    tree = etree.parse("input/test_full.xml")
    #print etree.tostring(xlator.translate(), pretty_print = True)
    assert_true(compare_nodes(xlator.translate(), tree.getroot(), log = False))
    
def test_inpro_translation():
    json_data = open("input/inpro_low.json")
    data = json.load(json_data)
    xlator = CyclusTranslator(data)
    tree = etree.parse("input/inpro_low.xml")
    #print etree.tostring(xlator.translate(), pretty_print = True)
    # #print "\n"
    #print etree.tostring(tree.getroot(), pretty_print = True)
    assert_true(compare_nodes(xlator.translate(), tree.getroot(), log = False))
    
def test_nea_translation():
    json_data = open("input/nea1.json")
    data = json.load(json_data)
    xlator = CyclusTranslator(data)
    tree = etree.parse("input/nea1.xml")
    print etree.tostring(xlator.translate(), pretty_print = True)
    print etree.tostring(tree.getroot(), pretty_print = True)
    assert_true(compare_nodes(xlator.translate(), tree.getroot(), log = False))
    
