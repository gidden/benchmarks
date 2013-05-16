# includes ---------------------------------------------------------------------
# local 
from fac_translate import JsonFacilityParser

# json/xml packages
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree

# test packages
from nose.tools import assert_equal, assert_raises
# ------------------------------------------------------------------------------

# setting up parameters --------------------------------------------------------
def setup_base(fac_t,imports,exports):
    obj = {
        "type":fac_t,
        "inputs":imports,
        "outputs":exports
        }
    return obj

def setup_derived(fac_t,imports,exports,parameters):
    """ parameters is a list of tuples where:
    parameter[0] = string key
    parameter[1] = attributes entry
    parameter[2] = constraints entry
    """
    desc = setup_base(fac_t,imports,exports)
    attributes, constraints = {}, {}
    for parameter in parameters:
        attributes[parameter[0]] = parameter[1]
        constraints[parameter[0]] = parameter[2]
    desc["attributes"] = attributes
    desc["constraints"] = constraints
    return desc
# ------------------------------------------------------------------------------

# checking parameters (guts of testing) ----------------------------------------
def check_base(fac,name,fac_t,imports,exports):
    assert_equal(name,fac.name)
    assert_equal(fac_t,fac.fac_t)
    assert_equal(imports,fac.imports)
    assert_equal(exports,fac.exports)

def check_only_derived(fac,production,node):
    assert_equal(production,fac.production)
    assert_equal(etree.tostring(node),etree.tostring(fac.node))

def check_derived(fac,name,fac_t,imports,exports,production,node):
    check_base(fac,name,fac_t,imports,exports)
    check_only_derived(fac,production,node)
# ------------------------------------------------------------------------------

# compilation tests (set up then run) ------------------------------------------
def test_base():
    default_prod = 0.0
    default_node = None
    name, fac_t, imports, exports = "aname", "atype", ["a","b"], ["c","d"]
    description = setup_base(fac_t,imports,exports)
    parser = JsonFacilityParser(name,description)
    fac = parser.parse()
    check_base(fac,name,fac_t,imports,exports)
    assert_equal(default_prod,fac.production)
    assert_equal(default_node,fac.node)

def test_repo():
    name, fac_t, inputs = "repo", "repository", ["lwr_waste","hwr_waste"]
    defualt_exports = []
    default_production = 0.0
    parameters = [("lifetime",["int","year"],60)]
    node = setup_repo_xml(name,fac_t,inputs)
    description = setup_derived(fac_t,imports,default_exports,parameters)
    parser = JsonFacilityParser(name,description)
    fac = parser.parse()
    check_derived(fac,name,fac_t,imports,default_exports,default_production,node)
# ------------------------------------------------------------------------------
