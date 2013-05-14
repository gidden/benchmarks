#! /usr/bin/env python

# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

from pprint import pprint, pformat
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree
from pyne import nucname


class DemandType(object):
    """defines a demand type for the simulation, e.g. power"""
    def __init__(self,name,units):
        self.name = name
        self.units = units
        self.fac_types = []
        self.sections = []

class DemandSection(object):
    """defines a section of demand, for any non-piecewise functions,
    there will only be one 'demand section'"""
    
    def __init__(self,start,function):
        self.start = start
        self.function_type = function[0]
        self.params = function[1:]
        

class FacilityInput(object):
    
    def __init__(self,name):
        self.initial_num = 0
        self.name = name
        self.demanded_commodity = ""
        self.info = None

    def __str__(self):
        s = "name: " + self.name + ", no: " + str(self.initial_num)
        return s


class CyclusTransformer(object):
    """I'm a little teapot."""
    
    def __init__(self, jfile,rfile):
        self.fac_types = {}
        self.demand_types = []
        with open(jfile, 'r') as f:
            self.jroot = json.load(f)
        self.xroot = etree.Element('simulation')
        self.rroot = etree.parse(rfile).getroot()
            
    def __str__(self):
        s = ""
        #s += "\n".join(["JSON Root =", '-'*40, pformat(self.jroot), '', ''])
        s += "\n".join(["XML Root =", '-'*40, etree.tostring(self.xroot, pretty_print=True)])
        return s
    
    def visit(self, node=None):
        if node is None:
            node = self.jroot
        for key, value in node.iteritems():
            methname = 'visit_' + key
            #print "visiting " + key
            if hasattr(self, methname):
                meth = getattr(self, methname)
                meth(value)
        # for key,value in self.fac_types.items(): print key, value 
        region = self.add_region(self.xroot)
        model = etree.SubElement(region,"model")
        regtype = etree.SubElement(model,"GrowthRegion")
        self.add_demand(regtype)
        inst = self.add_inst(region)
        for name,fac_input in self.fac_types.iteritems():
            self.add_facility(name,fac_input)


    def add_facility(self,name,fac_input):
        switch = fac_input.info['type']
        if switch == 'reactor':
            self.add_reactor(name,fac_input)
        elif switch == 'repository':
            self.add_repository(name,fac_input)
        else:
            raise Exception("facility type: " + switch 
                            + " not currently supported")
    
    def add_repository(self,name,fac_input):
        fac = etree.SubElement(self.xroot,"facility")
        name_node = etree.SubElement(fac,"name")
        name_node.text = name
        model = etree.SubElement(fac,"model")
        cyclus_t = etree.SubElement(model,"SinkFacility")
        commod_input = etree.SubElement(cyclus_t,"input")
        commod = etree.SubElement(commod_input,"commodities")
        for item in fac_input.info['inputs']:
            incommod = etree.SubElement(commod,"incommodity")
            incommod.text = item            
            incommod = etree.SubElement(fac,"incommodity")
            incommod.text = item

    def add_reactor(self,name,fac_input):
        fac = etree.SubElement(self.xroot,"facility")
        name_node = etree.SubElement(fac,"name")
        name_node.text = name
        
        attr = fac_input.info['attributes']
        vals = fac_input.info['constraints']
        if 'lifetime' in attr:
            self.add_fac_life(fac,attr['lifetime'][1],find_in_list('lifetime',vals))
        model = etree.SubElement(fac,"model")
        cyclus_t = etree.SubElement(model,'BatchReactor')

        for item in fac_input.info['inputs']:
            self.add_fuel(cyclus_t,item,"in")
            incommod = etree.SubElement(fac,"incommodity")
            incommod.text = item

        for item in fac_input.info['outputs']:
            self.add_fuel(cyclus_t,item,"out")
            incommod = etree.SubElement(fac,"outcommodity")
            incommod.text = item

        self.add_cycle_length(cyclus_t,find_in_list('cycle_length',vals))
        self.add_core_loading(cyclus_t,find_in_list('core_loading',vals))
        self.add_batch_number(cyclus_t,find_in_list('batch_number',vals))

        power = find_in_list('thermal_power',vals) * find_in_list('efficiency',vals) / 100
        self.add_power(cyclus_t,fac_input.demanded_commodity,power)

    def add_power(self,node,name,val):
        commod_prod = etree.SubElement(node,'commodity_production')
        commod = etree.SubElement(commod_prod,'commodity')
        commod.text = name
        capacity = etree.SubElement(commod_prod,'capacity')
        capacity.text = str(val)
        cost = etree.SubElement(commod_prod,'cost')
        cost.text = str(val)

    def add_cycle_length(self,node,val):
        sub = etree.SubElement(node,'cycle_length')
        sub.text = str(val)

    def add_core_loading(self,node,val):
        sub = etree.SubElement(node,'core_loading')
        sub.text = str(val)

    def add_batch_number(self,node,val):
        sub = etree.SubElement(node,'batch_number')
        sub.text = str(val)

    def add_fuel(self,node,name,dir_t):
        fuel = etree.SubElement(node,"fuel_"+dir_t+"put")
        commod = etree.SubElement(fuel,dir_t+"commodity")
        commod.text = name
        recipe = etree.SubElement(fuel,dir_t+"recipe")
        recipe.text = name
        

    def add_fac_life(self,node,units,val):
        life = etree.SubElement(node,'lifetime')
        if units == 'year': val *= 12
        life.text = str(val)
        

    def visit_fuel_cycle(self,node):
        self.visit_time_values(node)
        self.visit_facility_set_up(node['initial_facilities'])
        self.visit_demands(node["demands"])
 
    def visit_demands(self,node):
        for name,info in node.iteritems():
            self.visit_demand(name,info)

    def visit_demand(self,name,info):
        demand_type = DemandType(name,info['units'])
        for fac_type in info['facilities']:
            demand_type.fac_types.append(fac_type)
            self.fac_types[fac_type].demanded_commodity = name #demand_type
        time = info['grid']
        functions = info['constraints']
        if len(time)-1 != len(functions): raise Exception("grid, constraint length mismatch in demand")
        for i in range(len(functions)):
           demand_type.sections.append(DemandSection(time[i],functions[i]))
        self.demand_types.append(demand_type)        

    def visit_facility_set_up(self,node):
        for item in node:
            self.fac_types[item[0]].initial_num = item[1]
        
    def visit_facilities(self,node):
        for name, value in node.iteritems():
            self.visit_facility(name, value)

    def visit_facility(self,name,info):
        fac_info = FacilityInput(name)
        fac_info.info = info
        self.fac_types[name] = fac_info

    def add_demand(self,regtype):
        for demand_type in self.demand_types:            
            commod = etree.SubElement(regtype,"commodity")
            name = etree.SubElement(commod,"name")
            name.text = demand_type.name
            for section in demand_type.sections:
                 demand_node = etree.SubElement(commod,"demand")
                 ftype = etree.SubElement(demand_node,"type")
                 ftype.text = section.function_type
                 params = etree.SubElement(demand_node,"parameters")
                 text = ""
                 for item in section.params:
                     text += str(item) + " " 
                 params.text = text[:-1]
                 start = etree.SubElement(demand_node,"start_time")
                 start.text = str(section.start)
        

    def add_region(self,node):
        region = etree.SubElement(node,"region")
        name = etree.SubElement(region,"name")
        name.text = "region"
        facilities = [k for k,v in self.fac_types.items()]
        for facility in facilities:
            allowed_fac = etree.SubElement(region,"allowedfacility")
            allowed_fac.text = facility
        
        return region

    def add_inst(self,node):
        inst = etree.SubElement(node,"institution")
        name = etree.SubElement(inst,"name")
        name.text = "inst"
        initial_list = etree.SubElement(inst,"initialfacilitylist")
        facility_info = [v for k,v in self.fac_types.items()]
        for facility in facility_info:
            self.add_prototype(inst,facility.name)
            self.add_initial_fac(initial_list,facility)

    def add_prototype(self,node,name):
        avail_prototype = etree.SubElement(node,"available_prototype")
        avail_prototype.text = name

    def add_initial_fac(self,node,facility):
        if facility.initial_num > 0:
            entry = etree.SubElement(node,"entry")
            prototype = etree.SubElement(entry,"prototype")
            prototype.text = facility.name
            number = etree.SubElement(entry,"number")
            number.text = str(facility.initial_num)

    def visit_time_values(self,node):
        self.add_control_block(get_months(node['grid'],
                                          node['grid_units']))

    def add_control_block(self,nmonths):
        control = etree.SubElement(self.xroot,'control')
        duration = etree.SubElement(control,'duration')
        duration.text = str(nmonths) 
        startmonth = etree.SubElement(control,'startmonth')
        startmonth.text = str(0)
        startyear = etree.SubElement(control,'startyear')
        startyear.text = str(0)
        decay = etree.SubElement(control,'decay')
        decay.text = str(0)
        
    def visit_materials(self, node):
        for name, value in node.iteritems():
            self.visit_material(name, value)
            
    def visit_material(self, name, mat):
        # Add commoditiy information
        commodity = etree.SubElement(self.xroot, 'commodity')
        commodname = etree.SubElement(commodity, 'name')
        commodname.text = name

        # Add market information
        market = etree.SubElement(self.xroot,'market')
        marketname = etree.SubElement(market, 'name')
        marketname.text = name+'_market'
        marketcommod = etree.SubElement(market, 'mktcommodity')
        marketcommod.text = name
        marketmodel = etree.SubElement(market, 'model')
        modeltype = etree.SubElement(marketmodel, 'NullMarket')
        
        # Add recipe
        recipe = etree.SubElement(self.xroot, 'recipe')
        recipename = etree.SubElement(recipe, 'name')
        recipename.text = name + '_recipe'
        basis = etree.SubElement(recipe, 'basis')
        basis.text = 'mass'
        if mat['recipe']:
            self.visit_recipe_material(mat,recipe)
        else:
            self.visit_stored_recipe(name,recipe)

    def visit_recipe_material(self,mat,recipe):
        constraints = mat['constraints']
        for constraint in constraints:
            if nucname.isnuclide(constraint[0]):
                self.visit_nuclide(recipe,
                                   nucname.zzaaam(constraint[0]),
                                   constraint[1])

    def visit_stored_recipe(self,name,recipe):
        nodes = self.iso_nodes(name)
        for node in nodes:
            self.visit_nuclide(recipe,node[0].text,node[1].text)

    def visit_nuclide(self,recipe,nuc,val):
        isotope = etree.SubElement(recipe,'isotope')
        isoid = etree.SubElement(isotope,'id')
        isoid.text=str(nuc)
        isoval = etree.SubElement(isotope,'comp')
        isoval.text=str(val)

    def iso_nodes(self,name):
        recipe_names = self.rroot.xpath('recipe/name')
        for i in range(len(recipe_names)):
            if recipe_names[i].text == name:
                return self.rroot.xpath('recipe')[i].findall('isotope')
        raise RecipeError("No recipe named " + name 
                          + " found in " + self.rfile)

def find_in_list(find,a_list):
    for item in a_list:
        if item[0] == find:
            return item[1]
    return None

def get_months(period,units):
    span = period[-1] - period[0]
    factor = 1 if units == 'years' else 12
    return span * factor

class RecipeError(Exception):
    """Exception indicating a Recipe wasn't found."""
    pass


# <codecell>

ct = CyclusTransformer('nea1a.json','nea_recipes.xml')
ct.visit()
print ct

# <codecell>


