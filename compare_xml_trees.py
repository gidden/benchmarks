from lxml import etree
from copy import deepcopy

def is_leaf(a):
    return len(a) == 0

def compare_leaves(a, b):
    return etree.tostring(a) == etree.tostring(b)

def compare_nodes(a, b):
    if is_leaf(a) or is_leaf(b):
        if is_leaf(a) and is_leaf(b): return compare_leaves(a, b)
        else: return False
    else:
        b = deepcopy(b)
        try: 
            for achild in a:
                for bchild in b:
                     if compare_nodes(achild, bchild): b.remove(bchild)
        except ValueError:
            return False
        return len(b) == 0
                
if __name__ == "__main__":
    root = etree.Element("root")
    el2 = etree.SubElement(root,"el2")
    el2.text = "stuff"
    ch1 = etree.SubElement(root,"ch")
    sib1 = etree.SubElement(ch1,"ch1")
    sib1.text = "thing1"
    sib2 = etree.SubElement(ch1,"ch2")
    sib2.text = "thing2"
    ch2 = etree.SubElement(root,"ch")
    sib3 = etree.SubElement(ch2,"ch1")
    sib3.text = "thing3"
    sib4 = etree.SubElement(ch2,"ch2")
    sib4.text = "thing4"
    
    root2 = deepcopy(root)
    print compare_nodes(root,root2)
