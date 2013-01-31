# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from pprint import pprint, pformat
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree
from pyne import nucame


class CyclusTransformer(object):
    """I'm a little teapot."""
    
    def __init__(self, filename):
        with open(filename, 'r') as f:
            self.jroot = json.load(f)
        self.xroot = etree.Element('simulation')
            
    def __str__(self):
        s = "\n".join(["JSON Root =", '-'*40, pformat(self.jroot), '', ''])
        s += "\n".join(["XML Root =", '-'*40, etree.tostring(self.xroot, pretty_print=True)])
        return s
    
    def visit(self, node=None):
        if node is None:
            node = self.jroot
        for key, value in node.iteritems():
            methname = 'visit_' + key
            if hasattr(self, methname):
                meth = getattr(self, methname)
                meth(value)
                
    def visit_materials(self, node):
        for name, value in node.iteritems():
            self.visit_material(name, value)
            
    def visit_material(self, name, mat):
        # Add commoditiy information
        commodity = etree.SubElement(self.xroot, 'commodity')
        commodname = etree.SubElement(commodity, 'name')
        commodname.text = name
        
        # Add recipe
        recipe = etree.SubElement(self.xroot, 'recipe')
        recipename = etree.SubElement(recipe, 'name')
        recipename.text = name + '_recipe'
        basis = etree.SubElement(recipe, 'basis')
        basis.text = 'mass'
        for 

# <codecell>

ct = CyclusTransformer('nea1a.json')
ct.visit()
print ct

# <codecell>


