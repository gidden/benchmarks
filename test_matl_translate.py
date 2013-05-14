from matl_translate import json_to_xml, xml_to_json
from nose.tools import assert_equal

def setup_xml(name,ntopes,isotopes,values):
    xml_str = \
        "<recipe>" + \
        "<name>"+name+"</name>" +\
        "<basis>mass</basis>"

    for i in range(ntopes):
        xml_str += \
            "<isotope>" +\
            "<id>"+isotopes[i]+"</id>" +\
            "<comp>"+values[i]+"</comp>" +\
            "</isotope>"

    xml_str += "</recipe>"
    return xml_str

def setup_json(name,ntopes,isotopes,values):
    json_str = \
        "\""+name+"\": {" +\
	"\"recipe\": true," +\
	"\"constraints\": ["

    for i in range(ntopes):
        json_str += "[\""+isotopes[i]+"\", "+values[i]+"]"
        if (i < ntopes-1):
            json_str += ","
        else:
            json_str += "]"

    json_str += "}"
    return json_str

def test_translation():
    #constants
    name = "a_name"
    ntopes = 2
    xml_isotopes = ["92235", "92238"]
    json_isotopes = ["U235", "U238"]
    values = ["1e0", "2e0"]

    xml_str = setup_xml(name,ntopes,xml_isotopes,values)
    json_str = setup_json(name,ntopes,json_isotopes,values)
    
    xml_str = "hi"
    json_str = "hi"
    assert_equal(xml_str,json_to_xml(json_str))
    assert_equal(json_str,xml_to_json(xml_str))

