# local 
import fc_translate as xlate
import fc_testing_tools as tools

# xml packages
from lxml import etree

# test packages
from nose.tools import assert_equal, assert_raises, assert_true

def compare(s, t):
    """compare unordered sets, e.g. lists of xml nodes"""
    t = list(t)   # make a mutable copy
    try:
        for elem in s:
            t.remove(elem)
    except ValueError:
        return False
    return not t

def runtests(time_vars, initial_facs):
    # helpers
    info_helper = tools.SimInfo(time_vars)
    ic_helper = tools.InitialConditions(initial_facs)
    
    # json object construction
    description = {"attributes":{}, "constraints":{}}
    info_helper.add_to_description(description)
    ic_helper.add_to_description(description)

    # observed
    fac_types = {}
    for fac in initial_facs:
        fac_types[fac.name] = fac.fac_t
    extra_info = xlate.ExtraneousFCInfo(fac_types)
    parser = xlate.JsonFuelCycleParser(description, extra_info)
    fc = parser.parse()

    # expected
    info_xml = info_helper.get_xml()
    #print "\n" + etree.tostring(info_xml, pretty_print = True)
    ics = ic_helper.get_xml() #initial_facs
    # for ic in ics:
    #     print "\n" + etree.tostring(ic, pretty_print = True)
    growth = []

    # tests
    assert_equal(etree.tostring(info_xml), etree.tostring(fc.info))
    ics_strings, fc_strings = [], []
    for i in range(len(ics)):
        ics_strings.append(etree.tostring(ics[i]))
        fc_strings.append(etree.tostring(fc.initial_conditions[i]))
    assert_true(compare(ics_strings,fc_strings))
    for i in range(len(growth)):
        assert_equal(etree.tostring(growth[i]), etree.tostring(fc.growth[i]))

def default_time_vars():
    return ["years", [1,100]]

def default_ics_vars():
    return []

def test_default():
    runtests(default_time_vars(), default_ics_vars())

def test_years():
    time_units = "years"
    time = [1,1180]
    runtests([time_units, time], default_ics_vars())

def test_month():
    time_units = "months"
    time = [1, 1180]
    runtests([time_units, time], default_ics_vars())

def test_ics():
    rxtr = tools.TestFCFac("aReactorThing",5,"reactor","BatchReactor")
    repo = tools.TestFCFac("mightBeAREPOSITORY",2, "repository","SinkFacility")
    runtests(default_time_vars(), [rxtr,repo])
