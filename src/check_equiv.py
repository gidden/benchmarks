import argparse as ap
from lxml import etree
from compare_xml_trees import compare_nodes

def compare(file1, file2):    
    obs = etree.parse(file1)
    exp = etree.parse(file2)
    
    return compare_nodes(obs.getroot(), exp.getroot(), log = False)

def main():
    description = "Compares two XML files to determine if they represent "+\
        "identical xml trees."
    parser = ap.ArgumentParser(description=description)

    parser.add_argument('file1', type=ap.FileType('r'))
    parser.add_argument('file2', type=ap.FileType('r'))

    args = vars(parser.parse_args())
    file1 = args["file1"]
    file2 = args["file2"]

    print compare(file1, file2)
    file1.close()
    file2.close()

if __name__ == "__main__":
    main()
