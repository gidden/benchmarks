
# json/xml packages
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree

# converting nucnames
from pyne import nucname

import pprint

class MatlJsonifier(object):
    """Given a file with xml recipes which should either all be represented as
    recipes in json or not as recipes, the jsonifier will return the appropriate
    python object.
    """
    def __init__(self, fname, recipe = True):
        self.json = jsonify(fname, recipe)

def getComposition(node):
    isos = node.xpath("isotope")
    constraints = [[nucname.name(iso[0].text), float(iso[1].text)] for iso in isos]
    return constraints    

def jsonify(fname, recipe):
    tree = etree.parse(fname)
    nodes = tree.xpath("recipe")
    matls = {}
    for node in nodes:
        name = node.xpath("name")[0].text
        attributes = {"recipe": recipe}
        if recipe:
            metadata = {}
            constraints = getComposition(node)
        else:
            metadata = {"suggestedComposition": getComposition(node)}
            constraints = []
        matls[name] = {"metadata": metadata, "attributes": attributes, \
                           "constraints": constraints}
    return matls

def main():
    xmlname = "test.xml"
    json_recname = "test-recipe.json"
    json_nonname = "test-non.json"
    
    json_data = open(json_recname)
    json_rec = json.load(json_data)
    json_data = open(json_nonname)
    json_non = json.load(json_data)
    pprint.pprint(json_rec)
    pprint.pprint(MatlJsonifier(xmlname, recipe = True).json)
    assert json_rec == MatlJsonifier(xmlname, recipe = True).json
    pprint.pprint(json_non)
    pprint.pprint(MatlJsonifier(xmlname, recipe = False).json)
    assert json_non == MatlJsonifier(xmlname, recipe = False).json
        
if __name__ == "__main__":
    main()
