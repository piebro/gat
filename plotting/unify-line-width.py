import argparse
import os
import re
import xml.etree.ElementTree as ET
import sys

TAGS_WITH_STROKE_WIDTH=["altGlyph", "circle", "ellipse", "line", "path",
"polygon", "polyline", "rect", "text", "textPath", "tref", "tspan"]
PIXEL_TO_MM_MULT = 3.779527559

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


def modStrokeWidth(strokeWidth, element, scale):
    for child in list(element):
        if child.tag in TAGS_WITH_STROKE_WIDTH:
            if "style" in child.attrib:
                if "stroke-width" in child.attrib["style"]:
                    child.attrib["style"] = re.sub(r'stroke-width:\d+(?:\.\d+)', 'stroke-width:'+str(strokeWidth/scale), child.attrib["style"], count=1)
                else:
                    child.attrib["stroke-width"] = str(strokeWidth/scale)
            else:
                child.attrib["stroke-width"] = str(strokeWidth/scale)
        elif child.tag == "g" and ("transform" in child.attrib) and ("scale" in child.attrib["transform"]):
            newScale = float(re.findall(r'scale\((\d+(?:\.\d+)?)\)',child.attrib["transform"])[0])
            modStrokeWidth(strokeWidth, child, scale*newScale)
            return

        modStrokeWidth(strokeWidth, child, scale)

def saveModSvgString(args):
    root = getRoot(args)
    modStrokeWidth(args.stroke_width / PIXEL_TO_MM_MULT, root, 1)

    saveRoot(root, args)

    if args.log:
        print("unfied stroke-width to {} mm".format(args.stroke_width), file=sys.stderr)
        


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", help="path to a svg file")
    parser.add_argument("-o", "--output_path", help="path of the output svg file")
    parser.add_argument("-w", "--stroke_width", help="width of every stroke in mm", default=2, type=float)
    parser.add_argument("-l", "--log", action="store_true", help="log what is happening")
    args = parser.parse_args()

    saveModSvgString(args)


    # TODO: stroke width is the same but with different scale

if __name__ == "__main__":
    main()
