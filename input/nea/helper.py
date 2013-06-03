try:
    import simplejson as json
except ImportError:
    import json

xml2json_path = "../../xml2json"
import sys
sys.path.append(xml2json_path)

from matl_xml2json  import MatlJsonifier

def combine(dics):
    ret = {}
    for dic in dics:
        for k, v in dic.iteritems():
            ret[k] = v
    return ret
    
if __name__ == "__main__":
    # this helper script is designed to take xml representations of materials
    # used in the nea benchmark and translate them into json. the nea recipes
    # are broken into two files, one for strict recipes and the other for
    # inferred recipes (post irradiation)
    dics = []
    fname = "nea_nonrecipes.xml"
    dics.append(MatlJsonifier(fname, False).json)
    fname = "nea_recipes.xml"
    dics.append(MatlJsonifier(fname, True).json)
    print combine(dics)
    outname = "nea_matls.json"
    f = open(outname, 'w')
    json.dump(combine(dics), f)
