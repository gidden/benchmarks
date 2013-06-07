# includes ---------------------------------------------------------------------
# get source files in path
import sys
sys.path.append("../src")

import fac_translate as ft
import input_compiler as ic
import compare_xml_trees as cxt
from lxml import etree
from copy import deepcopy

# test packages
from nose.tools import assert_equal, assert_raises, eq_, raises, assert_true, assert_false
from sets import Set
# ------------------------------------------------------------------------------

class CycleDescription(object):
    def __init__(self, clunits, clval, cfunits = None, cfval = None):
        self.clunits = clunits
        self.clval = clval
        self.cfunits = cfunits
        self.cfval = cfval

    def attrs(self):
        attrs = {}
        if self.clunits is not None:
            attrs["cycleLength"] = ["int", self.clunits]
        if self.cfunits is not None:
            attrs["capacityFactor"] = ["float", self.cfunits]
        return attrs

    def constrs(self):
        constrs = []
        if self.clval is not None:
            constrs.append(["cycleLength", self.clval])
        if self.cfunits is not None:
            constrs.append(["capacityFactor", self.cfval])
        return constrs

def test_cycle_length():
    expected = 12 # number of months of cycle length

    descr1 = CycleDescription("month", expected)
    obs = ft.getCycleLength(descr1.attrs(), descr1.constrs())
    eq_(obs, expected)

    descr2 = CycleDescription("year", expected/12)
    obs = ft.getCycleLength(descr2.attrs(), descr2.constrs())
    assert_equal(obs, expected)

    cf = 80
    upval = (expected * 365 / 12) * (cf / 100.0)
    descr3 = CycleDescription("EFPD", upval, "percent", cf)
    obs = ft.getCycleLength(descr3.attrs(), descr3.constrs())
    assert_equal(obs, expected)

@raises(TypeError)
def test_cycle_err():
    descr4 = CycleDescription("notaunit", 12)
    ft.getCycleLength(descr4.attrs(), descr4.constrs())

def test_source_commods():
    imports = Set(["a"])
    exports = Set(["a"])
    exp = Set([])
    obs = ic.getSourceCommods(imports, exports)
    assert_equal(obs, exp)

    imports = Set(["a", "b"])
    exports = Set(["b"])
    exp = Set(["a"])
    obs = ic.getSourceCommods(imports, exports)
    assert_equal(obs, exp)

    imports = Set(["a", "b", "c"])
    exports = Set(["b"])
    exp = Set(["a", "c"])
    obs = ic.getSourceCommods(imports, exports)
    assert_equal(obs, exp)

    imports = Set(["a", "a", "b"])
    exports = Set(["b"])
    exp = Set(["a"])
    obs = ic.getSourceCommods(imports, exports)
    assert_equal(obs, exp)

def test_compare():
    obs = etree.Element("root")
    extra = etree.SubElement(obs, "thing")
    exp = deepcopy(obs)
    extra2 = etree.SubElement(obs, "thing")
    assert_false(cxt.compare_nodes(obs, exp))
    
    obs = etree.parse("input/obs.xml").getroot()
    exp = etree.parse("input/exp.xml").getroot()
    
    assert_false(cxt.compare_nodes(obs, exp))
