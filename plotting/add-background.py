import argparse
import os
import re
import xml.etree.ElementTree as ET
import sys

def getRoot(args):
    if args.input_path == None:
        contents = []
        while True:
            try:
                line = input()
            except EOFError:
                break
            contents.append(line)
    else:
        with open(args.input_path, "r") as f:
            contents = f.readlines()
    svg_str = "\n".join(contents)
    svg_str = re.sub(' xmlns="[^"]+"', '', svg_str, count=1)
    return ET.fromstring(svg_str)

def saveRoot(root, args):
    root.attrib["xmlns"] = "http://www.w3.org/2000/svg"
    if args.output_path == None:
        print(ET.tostring(root).decode('utf-8'))
    else:
        with open(args.output_path,"wb") as f:
            f.write(ET.tostring(root))

def saveModSvgString(args):
    root = getRoot(args)

    bgElement = ET.Element("rect", x="-100000", y="-100000", width="1000000", height="1000000", style="fill:rgb(255,255,255)") 
    root.insert(0,bgElement)

    saveRoot(root, args)

    if args.log:
        print("added white background", file=sys.stderr)
        


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", help="path to a svg file")
    parser.add_argument("-o", "--output_path", help="path of the output svg file")
    parser.add_argument("-l", "--log", action="store_true", help="log what is happening")
    args = parser.parse_args()

    saveModSvgString(args)


    # TODO: stroke width is the same but with different scale

if __name__ == "__main__":
    main()
