from pyne import nucname
from lxml import etree

class CompositionError(Exception):
    """Exception indicating a composition wasn't found."""
    pass

class CyclusMaterial(object):
    """ simple holding class for materials in cyclus input. underlying
    representation is in xml.
    """
    def __init__(self,name,node):
        self.name = name
        self.node = node

class JsonMaterialParser(object):
    def __init__(self,json_materials):
        self.__json_rep = json_materials

    def __check_recipe(self,description):
        return description["attributes"]["recipe"] == "true"
    
    def __check_suggestedComposition(self,description):
        return "suggestedComposition" in description["attributes"]
    
    def __basis(self,description):
        if "basis" in description["attributes"]:
            return description["attributes"]["basis"]
        else:
            return "mass"

    def __add_recipe(self,constraints,root):
        for constraint in constraints:
            if nucname.isnuclide(constraint[0]):
                eliso = etree.SubElement(root,"isotope")
                elid = etree.SubElement(eliso,"id")
                elid.text = str(nucname.zzaaam(constraint[0]))
                elval = etree.SubElement(eliso,"comp")
                elval.text = str(constraint[1])

    def __construct_xml_tree(self,name,description,root):
        elname = etree.SubElement(root,"name")
        elname.text = name
        elbasis = etree.SubElement(root,"basis")
        elbasis.text = self.__basis(description)
        recipe = []
        if (self.__check_recipe(description)):
            recipe = description["constraints"]
        else:
            recipe = description["attributes"]["suggestedComposition"]
        self.__add_recipe(recipe,root)

    def parse(self):
        """ Takes as input a python dictionary of materials as specified in the
        benchmark specification language. returns a list of translated
        CyclusMaterials.
        """
        materials = []
        for name, description in self.__json_rep.iteritems():
            # matl name, description
            root = etree.Element("recipe")
            try:
                self.__construct_xml_tree(name, description, root)
            except: 
                raise CompositionError("No composition (recipe or "+
                                       "suggestedComposition) could be found "+
                                       "in " + name)
            materials.append(CyclusMaterial(name, root))
        return materials

