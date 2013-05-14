# local 
from matl_translate import json_to_cyclus

# json/xml packages
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree

# test packages
from nose.tools import assert_equal

def test_translation():
    name,ntopes,xml_isotopes,json_isotopes,values = setup_constants()
    xml_node = setup_xml(name,ntopes,xml_isotopes,values)
    json_node = setup_json(name,ntopes,json_isotopes,values)
    materials = json_to_cyclus(json_node)
    assert_equal(xml_node,materials[0].node)
    # don't need to perform xml to json xform (yet)
    #assert_equal(json_str,xml_to_json(xml_str))

def setup_xml(name,ntopes,isotopes,values):
    root = etree.Element("recipe")
    elname = etree.SubElement(root,"name")
    elname.text = name
    elbasis = etree.SubElement(root,"basis")
    elbasis.text = "mass"
    for i in range(ntopes):
        eliso = etree.SubElement(root,"isotope")
        elid = etree.SubElement(eliso,"id")
        elid.text = isotopes[i]
        elval = etree.SubElement(eliso,"comp")
        elval.text = str(values[i])
    return root

def setup_json(name,ntopes,isotopes,values):
    jisotopes = []
    for i in range(ntopes):
        jisotopes.append([isotopes[i],values[i]])
    obj = {name:{\
               "attributes":{"recipe":"true"},\
               "constraints":jisotopes\
          }}
    return obj

def setup_constants():
    name = "a_name"
    ntopes = 2
    xml_isotopes = ["92235", "92238"]
    json_isotopes = ["U235", "U238"]
    values = [1e0, 2e0]
    return name,ntopes,xml_isotopes,json_isotopes,values

if __name__ == "__main__":
    name,ntopes,xml_isotopes,json_isotopes,values = \
        setup_constants()
    xml_node = setup_xml(name,ntopes,xml_isotopes,values)
    json_obj = setup_json(name,ntopes,json_isotopes,values)
#    print etree.tostring(xml_node)
#    print json.dumps(json_obj, indent = 4 * ' ')
    json_to_cyclus(json_obj)
