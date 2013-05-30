# local 
import fc_translate as xlate
import fc_testing_tools as tools
import compare_xml_trees as cxt

# xml packages
from lxml import etree

# test packages
from nose.tools import assert_equal, assert_raises, assert_true

def runtests(time_vars, initial_facs, growth_params):
    # helpers
    info_helper = tools.SimInfo(time_vars)
    ic_helper = tools.InitialConditions(initial_facs)
    growth_helper = tools.Growth(growth_params)
    
    # json object construction
    description = {"attributes":{}, "constraints":{}}
    info_helper.add_to_description(description)
    ic_helper.add_to_description(description)
    growth_helper.add_to_description(description)
    # print description

    # observed
    fac_types = {}
    for fac in initial_facs:
        fac_types[fac.name] = fac.fac_t
    extra_info = xlate.ExtraneousFCInfo(fac_types)
    parser = xlate.JsonFuelCycleParser(description, extra_info)
    fc = parser.parse()

    # expected
    info_xml = info_helper.get_xml()
    ics = ic_helper.get_xml()
    growth = growth_helper.get_xml()
    
    # tests
    assert_true(cxt.compare_nodes(info_xml, fc.info))
    assert_true(cxt.compare_nodes(ics, fc.initial_conditions))
    assert_true(cxt.compare_nodes(growth, fc.growth))
    producers = {param.name: param.facilities for param in growth_params}
    assert_equal(producers,fc.producers)

def default_time_vars():
    return ["years", [1,100]]

def default_ics_vars():
    return [tools.TestFCFac("rxtr", 1, "reactor", "BatchReactor")]

def default_growth_vars():
    return [tools.TestFCGrowth("powa", "GWe", ["rxtr"], [1,120], \
                                   ['linear',[0,500]])]

def test_default():
    runtests(default_time_vars(), default_ics_vars(), default_growth_vars())

def test_years():
    time_units = "years"
    time = [1,1180]
    runtests([time_units, time], default_ics_vars(), default_growth_vars())

def test_month():
    time_units = "months"
    time = [1, 1180]
    runtests([time_units, time], default_ics_vars(), default_growth_vars())

def test_ics():
    rxtr = tools.TestFCFac("aReactorThing", 5, "reactor", "BatchReactor")
    repo = tools.TestFCFac("mightBeAREPOSITORY", 2, "repository","SinkFacility")
    runtests(default_time_vars(), [rxtr,repo], default_growth_vars())

def test_growth():    
    rxtr = tools.TestFCGrowth("powa", "GWe", ["rxtr1","rxtr2"], [1,120], \
                                  ['linear',[0,500]])
    repo = tools.TestFCGrowth("space", "tHM", ["repo1"], [1,120], \
                                  ['linear',[50,0,500],[100,0,1000]])
    runtests(default_time_vars(), default_ics_vars(), [rxtr,repo])

