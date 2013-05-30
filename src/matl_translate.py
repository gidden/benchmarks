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

    def __str__(self):
        return "Name: " + self.name + "\n" \
            + "Node: \n" + etree.tostring(self.node, pretty_print = True)

class JsonMaterialParser(object):
    """ A parser that accepts a python-based json object representation of
    materials from the FCS benchmark specification language and returns a
    cyclus-based representation of the material
    """
    def __init__(self, name, description):
        self.__name = name
        self.__description = description

    def __check_recipe(self,description):
        return description["attributes"]["recipe"]
    
    def __check_suggestedComposition(self,description):
        return "suggestedComposition" in description["metadata"]
    
    def __basis(self,description):
        if "basis" in description["attributes"]:
            return description["attributes"]["basis"]
        else:
            return "mass"

    def __get_nuclide(self,nucstr):
        # this will change once cyclus supports the full zzaaam
        # (we currently only support zzaaa)
        return str(nucname.zzaaam(nucstr))[:-1]

    def __add_recipe(self,constraints,root):
        for constraint in constraints:
            if nucname.isnuclide(constraint[0]):
                eliso = etree.SubElement(root,"isotope")
                elid = etree.SubElement(eliso,"id")
                elid.text = self.__get_nuclide(constraint[0])
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
            recipe = description["metadata"]["suggestedComposition"]
        self.__add_recipe(recipe,root)

    def parse(self):
        """ Takes as input a python dictionary of materials as specified in the
        benchmark specification language. returns a list of translated
        CyclusMaterials.
        """
        root = etree.Element("recipe")
        try:
            self.__construct_xml_tree(self.__name, self.__description, root)
        except: 
            raise CompositionError("No composition (recipe or "+
                                   "suggestedComposition) could be found "+
                                   "in " + self.__name)
        return CyclusMaterial(self.__name, root)


def readMaterials(json_obj):
    matls = []
    for name, descr in json_obj.iteritems(): 
        parser = JsonMaterialParser(name,descr)
        matls.append(parser.parse())
    return matls
