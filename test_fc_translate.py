# local 
from fc_translate import JsonFuelCycleParser

# json/xml packages
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree

# test packages
from nose.tools import assert_equal, assert_raises

def test_everything():
    # expected
    info_xml = etree.Element("simulation")
    ics = []
    growth = []
    
    # observed
    description = {}
    parser = JsonFuelCycleParser(description)
    fc = parser.parse()

    # tests
    assert_equal(etree.tostring(info_xml), etree.tostring(fc.info))
    for i in range(len(ics)):
        assert_equal(etree.tostring(ics[i]), etree.tostring(fc.ics[i]))
    for i in range(len(growth)):
        assert_equal(etree.tostring(growth[i]), etree.tostring(fc.growth[i]))
