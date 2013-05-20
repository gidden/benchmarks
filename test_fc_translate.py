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


 # "fuelCycle": {
 #     "attributes": {
 #         "grid": "year",
 #         "initialConditions": {
 #             "repository": 1,
 #         },
 #         "demands": {
 #             "power": ["GWe", ["lwrReactor"]]
 #         }
 #     }
 #     "constraints": {
 #         "grid": [0, 120],
 #         "demands": {
 #             "power": {
 #                 "grid": [0,120],
 #                 "growth": {
 #        	     "type": "linear",
 #        	     "period": {
 #        	         "startTime": 0,
 #        	         "startValue": 1000,
 #                         "slope": 500
 #        	     }
 #                 }
 #             }
 #         }
 #     }
 # }

def fill_info(attr, units, constrs, time):
    attr["grid"] = units
    constrs["grid"] = time

def get_description(time_units, time):
    obj = {}
    obj["attributes"] = {}
    obj["constraints"] = {}
    fill_info(obj["attributes"],time_units,obj["constraints"],time)
    return obj

def get_info_xml(time_units,time):
    diff = time[1] - time[0]
    if time_units is "years":
        diff *= 12
    root = etree.Element("control")
    duration = etree.SubElement(root,"duration")
    duration.text = str(diff)
    startmonth = etree.SubElement(root,"startmonth")
    startmonth.text = "1" # default starting month
    startyear = etree.SubElement(root,"startyear")
    startyear.text = "2000" # default starting year
    simstart = etree.SubElement(root,"simstart")
    simstart.text = "0" # default starting time period
    decay = etree.SubElement(root,"decay")
    decay.text = "2" # default decay switch
    return root

def runtests(time_vars):
    # variables
    time_units = time_vars[0]
    time = time_vars[1]

    # observed
    description = get_description(time_units,time)
    parser = JsonFuelCycleParser(description)
    fc = parser.parse()

    # expected
    info_xml = get_info_xml(time_units,time)
    #print "\n" + etree.tostring(info_xml, pretty_print = True)
    ics = []
    growth = []

    # tests
    assert_equal(etree.tostring(info_xml), etree.tostring(fc.info))
    for i in range(len(ics)):
        assert_equal(etree.tostring(ics[i]), etree.tostring(fc.ics[i]))
    for i in range(len(growth)):
        assert_equal(etree.tostring(growth[i]), etree.tostring(fc.growth[i]))

def default_time_vars():
    return ["years", [1,100]]

def test_default():
    runtests(default_time_vars())

def test_years():
    time_units = "years"
    time = [1,1180]
    runtests([time_units, time])

def test_month():
    time_units = "months"
    time = [1, 1180]
    runtests([time_units, time])
