import argparse as ap
try:
    import simplejson as json
except ImportError:
    import json
from lxml import etree

from input_compiler import CyclusTranslator

def main():
    description = "The Cyclus Benchmark Specification Transformer "+\
        "translates a fuel cycle benchmark specification from a supported "+\
        "implementation langage (e.g. JSON) into a valid Cyclus input file."
    parser = ap.ArgumentParser(description=description)

    json_help = "the name of the json file to be translated"
    xml_help = "the name of the xml file to write to"
    parser.add_argument('json-file', type=ap.FileType('r'), help=json_help)
    parser.add_argument('xml-file', type=ap.FileType('w'), help=xml_help)

    args = vars(parser.parse_args())
    jfile = args["json-file"]
    xfile = args["xml-file"]

    data = json.load(jfile)
    xlator = CyclusTranslator(data)
    xfile.write(etree.tostring(xlator.translate(), pretty_print = True))

    xfile.close()
    jfile.close()

if __name__ == "__main__":
    main()
