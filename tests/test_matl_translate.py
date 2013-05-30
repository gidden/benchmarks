# includes ---------------------------------------------------------------------
# get source files in path
import sys
sys.path.append("../src")

# local 
from matl_translate import readMaterials
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

def test_mats():
    json_data = open("test_mat.json")
    data = json.load(json_data)
    matls = readMaterials(data["materials"])

    tree = etree.parse("test_mat.xml")
    root = etree.Element("root")
    for mat in matls: root.append(mat.node)
    
    assert_true(compare_nodes(root, tree.getroot(), log = False))
