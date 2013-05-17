# includes ---------------------------------------------------------------------
# local 
from fac_translate import JsonFacilityParser, JsonRepositoryParser

# json/xml packages
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree

# test packages
from nose.tools import assert_equal, assert_almost_equal, assert_raises
import pprint
# ------------------------------------------------------------------------------

# mock objects -----------------------------------------------------------------
class MockFacilityParser(JsonFacilityParser):
    def __init__(self, name, description, value, text):
        JsonFacilityParser.__init__(self, name, description)
        self.value = value
        self.text = text

    def _getProduction(self):
        return self.value

    def _getNode(self):
        return etree.Element(self.text)
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

def setup_repo_xml(name,inputs,capacity=None,lifetime=None):
    root = etree.Element("facility")
    elname = etree.SubElement(root,"name")
    if lifetime is not None:
        ellife = etree.SubElement(root,"lifetime")
        ellife.text = str(lifetime)
    elname.text = name
    elmodel = etree.SubElement(root,"model")
    elclass = etree.SubElement(elmodel,"SinkFacility")
    elin = etree.SubElement(elclass,"input")
    elcommods = etree.SubElement(elin,"commodities")
    for i in range(len(inputs)):
        elincommod = etree.SubElement(elcommods,"incommodity")
        elincommod.text = inputs[i]
    if capacity is not None:
        elcapacity = etree.SubElement(elin,"input_capacity")
        elcapacity.text = str(capacity)
    for i in range(len(inputs)):
        elincommod = etree.SubElement(root,"incommodity")
        elincommod.text = inputs[i]
    return root
# ------------------------------------------------------------------------------

# checking parameters (guts of testing) ----------------------------------------
def check_base(fac,name,fac_t,imports,exports):
    assert_equal(name,fac.name)
    assert_equal(fac_t,fac.fac_t)
    assert_equal(imports,fac.imports)
    assert_equal(exports,fac.exports)

def check_only_derived(fac,production,node):
    assert_almost_equal(production,fac.production)
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

def test_derived():
    value, text = 1.5, "test"
    node = etree.Element(text)
    name, fac_t, imports, exports = "aname", "atype", ["a","b"], ["c","d"]
    description = setup_base(fac_t,imports,exports)
    mock = MockFacilityParser(name,description,value,text)
    fac = mock.parse()
    check_derived(fac,name,fac_t,imports,exports,value,node)

def do_repotest(name,fac_t,imports,exports,production,capacity,lifetime):
    node = setup_repo_xml(name,imports,capacity=capacity,lifetime=lifetime)
    parameters = []
    if capacity is not None:
        parameters.append(("capacity",["double","tHM"],capacity))
    if lifetime is not None:
        parameters.append(("lifetime",["int","year"],lifetime))
    description = setup_derived(fac_t,imports,exports,parameters)
    parser = JsonRepositoryParser(name,description)
    fac = parser.parse()
    check_derived(fac,name,fac_t,imports,exports,production,node)
    
def test_repo():
    name, fac_t, imports = "repo", "repository", ["lwr_waste","hwr_waste"]
    exports = []
    production = 0.0
    lifetime = 60
    capacity = 5e10
    do_repotest(name,fac_t,imports,exports,production,None,None)
    do_repotest(name,fac_t,imports,exports,production,capacity,None)
    do_repotest(name,fac_t,imports,exports,production,None,lifetime)
    do_repotest(name,fac_t,imports,exports,production,capacity,lifetime)
# ------------------------------------------------------------------------------
