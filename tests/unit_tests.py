# includes ---------------------------------------------------------------------
# get source files in path
import sys
sys.path.append("../src")

import fac_translate as ft

# test packages
from nose.tools import assert_equal, assert_raises, eq_, raises
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
    upval = (expected * 365 / 12) / (cf / 100.0)
    descr3 = CycleDescription("EFPD", upval, "percent", cf)
    obs = ft.getCycleLength(descr3.attrs(), descr3.constrs())
    assert_equal(obs, expected)

@raises(TypeError)
def test_cycle_err():
    descr4 = CycleDescription("notaunit", 12)
    ft.getCycleLength(descr4.attrs(), descr4.constrs())
