from lxml import etree

class ReactorFuels(object):
    def __init__(self, imports, inrecipes, in_core_qty,
                 exports, outrecipes, out_core_qty, batches, burnup):
        self.imports = imports
        self.inrecipes = inrecipes
        self.in_core_qty = in_core_qty
        self.exports = exports
        self.outrecipes = outrecipes
        self.out_core_qty = out_core_qty
        self.batches = batches
        self.burnup = burnup

class ReactorSchedule(object):
    def __init__(self, cycle, refuel, lifetime, storage, cooling):
        self.cycle = cycle
        self.refuel = refuel
        self.lifetime = lifetime
        self.storage = storage
        self.cooling = cooling

class ReactorProduction(object):
    def __init__(self, prod_t, capacity, eff):
        self.prod_t = prod_t
        self.capacity = capacity
        self.eff = eff

class ReactorGenerator(object):
    def __init__(self, name, fac_t, fuels, schedule, production):
        self.name = name
        self.fac_t = fac_t
        self.fuels = fuels
        self.schedule = schedule
        self.production = production
        
    def __add_fuels(self,node):
        for i in range(len(self.fuels.inrecipes)):
            finput = etree.SubElement(node,"fuel_input")
            incommodity = etree.SubElement(finput,"incommodity")
            incommodity.text = self.fuels.imports[i]
            inrecipe = etree.SubElement(finput,"inrecipe")
            inrecipe.text = self.fuels.inrecipes[i]
        for i in range(len(self.fuels.outrecipes)):
            foutput = etree.SubElement(node,"fuel_output")
            outcommodity = etree.SubElement(foutput,"outcommodity")
            outcommodity.text = self.fuels.exports[i]
            outrecipe = etree.SubElement(foutput,"outrecipe")
            outrecipe.text = self.fuels.outrecipes[i]
        
    def __add_schedule(self,node):
        cycle = etree.SubElement(node,"cyclelength")
        cycle.text = str(self.schedule.cycle)
        refuel = etree.SubElement(node,"refueldelay")
        refuel.text = str(self.schedule.refuel)

    def __add_loading(self,node):
        incore = etree.SubElement(node,"incoreloading")
        incore.text = str(self.fuels.in_core_qty)
        outcore = etree.SubElement(node,"outcoreloadoutg")
        outcore.text = str(self.fuels.out_core_qty)
        batches = etree.SubElement(node,"batchespercore")
        batches.text = str(self.fuels.batches)

    def __add_production(self,node):
        top_lvl = etree.SubElement(node,"commodity_production")
        commod = etree.SubElement(top_lvl,"commodity")
        commod.text = self.production.prod_t
        cap = etree.SubElement(top_lvl,"capacity")
        cap.text = str(self.production.capacity)
        cap = etree.SubElement(top_lvl,"cost")
        cap.text = str(self.production.capacity)

    def node(self):
        # general facility
        root = etree.Element("facility")
        elname = etree.SubElement(root,"name")
        elname.text = self.name
        if self.schedule.lifetime is not None:
            ellife = etree.SubElement(root,"lifetime")
            ellife.text = str(self.schedule.lifetime)
        # batchreactor model
        elmodel = etree.SubElement(root,"model")
        elclass = etree.SubElement(elmodel,"BatchReactor")
        self.__add_fuels(elclass)
        self.__add_schedule(elclass)
        self.__add_loading(elclass)
        self.__add_production(elclass)
        # general facility
        inputs = self.fuels.imports
        for i in range(len(inputs)):
            elincommod = etree.SubElement(root,"incommodity")
            elincommod.text = inputs[i]
        outputs = self.fuels.exports
        for i in range(len(outputs)):
            eloutcommod = etree.SubElement(root,"outcommodity")
            eloutcommod.text = outputs[i]
        return root

    def parameters(self):
        params = []
        thermal_power = self.production.capacity / self.production.eff
        params.append(("thermal_power",["double","GWt"],thermal_power))
        params.append(("efficiency",["double","percent"],self.production.eff))
        params.append(("burnup",["double","GWd/tHM"],self.fuels.burnup))
        params.append(("storage_time",["int","year"],self.schedule.storage))
        params.append(("cooling_time",["int","year"],self.schedule.cooling))
        params.append(("cycle_length",["int","month"],self.schedule.cycle))
        params.append(("core_loading",["double","kg"],self.fuels.in_core_qty))
        params.append(("batch_number",["int",""],self.fuels.batches))
        params.append(("lifetime",["int","year"],self.schedule.lifetime))
        return params

