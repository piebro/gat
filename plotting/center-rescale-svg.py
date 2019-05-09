import argparse
import os
import re
import xml.etree.ElementTree as ET
import sys

PIXEL_TO_MM_MULT = 3.779527559
PAPER_SIZES_LANDSCAPE = {
    "a3":[420,297],
    "a4":[297,210],
    "a5":[210,148],
    "a6":[148,105],
    "a7":[105,74],
    "card":[149,111]
}

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


def calcScaleAndOffset(svg_size, targetSize, args):
    widthMult = svg_size[1]/svg_size[0]

    newTargetSize = [targetSize[0]-2*args.border,
    targetSize[1]-2*args.border]

    if newTargetSize[0] * widthMult <= newTargetSize[1]:
        newWidth = args.scale * targetSize[0]
        newHeight = newWidth * widthMult
    else:
        newHeight = args.scale * newTargetSize[1]
        newWidth = newHeight / widthMult

    offsetX = (newTargetSize[0] - newWidth) / 2 + args.border
    offsetY = (newTargetSize[1] - newHeight) / 2 + args.border

    scale = newWidth/svg_size[0] * PIXEL_TO_MM_MULT
    offset = [offsetX * PIXEL_TO_MM_MULT, offsetY * PIXEL_TO_MM_MULT]
    return [scale,offset]

def getSvgSize(root):
    if "viewBox" in root.attrib:
        viewBox = re.split(' |,',root.attrib["viewBox"])
        width = float(re.findall(r'(\d+(?:\.\d+)?)',viewBox[2])[0])
        height = float(re.findall(r'(\d+(?:\.\d+)?)',viewBox[3])[0])
    elif "viewbox" in root.attrib:
        viewBox = re.split(' |,',root.attrib["viewbox"])
        width = float(re.findall(r'(\d+(?:\.\d+)?)',viewBox[2])[0])
        height = float(re.findall(r'(\d+(?:\.\d+)?)',viewBox[3])[0])
    elif "width" in root.attrib and "height" in root.attrib:
        width =  float(re.findall(r'(\d+(?:\.\d+)?)',root.attrib["width"])[0])
        height =  float(re.findall(r'(\d+(?:\.\d+)?)',root.attrib["height"])[0])
    else:
        raise ValueError("invalid svg. No viewBox or width and height in svg file")
    return [width, height]


def saveScaledSvgString(args):
    root = getRoot(args)
    svg_size = getSvgSize(root)

    targetSize = PAPER_SIZES_LANDSCAPE[args.format]
    if args.portrait:
        targetSize = [targetSize[1],targetSize[0]]

    #if args.rotate:
    #    svg_size = [svg_size[1],svg_size[0]]

    [scale, offset] = calcScaleAndOffset(svg_size, targetSize, args)

    #if args.rotate:
    #    originalSVG.rotate(90,svg_size[1]/2,svg_size[0]/2)
    #    diff_size = svg_size[0]-svg_size[1]
    #    offset[0] = offset[0]+diff_size/2*scale
    #    offset[1] = offset[1]-diff_size/2*scale

    transform = 'translate({},{}) scale({})'.format(offset[0], offset[1], scale)
    g = ET.Element("g", transform=transform)
    
    for child in list(root):
        g.append(child)
        root.remove(child)

    root.append(g)
    root.attrib["viewBox"] = "0 0 {} {}".format(targetSize[0]*PIXEL_TO_MM_MULT, targetSize[1]*PIXEL_TO_MM_MULT)
    root.attrib["width"] = "{}mm".format(targetSize[0])
    root.attrib["height"] = "{}mm".format(targetSize[1])

    saveRoot(root, args)

    if args.log:
        print("centered", file=sys.stderr)
        logMsg = "scaled to {}mm x {}mm".format(targetSize[0], targetSize[1])
        print(logMsg, file=sys.stderr)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_path", help="path to a svg file")
    parser.add_argument("-o", "--output_path", help="path of the output svg file")
    parser.add_argument("-f", "--format", help="the size of the paper to plot on", default="card", choices=["a3", "a4", "a5", "a6", "a7", "card"])
    parser.add_argument("-s", "--scale", help="scale the svg", default=1, type=float)
    parser.add_argument("-b", "--border", help="size of a border around the image in mm", type=int, default=0)
    parser.add_argument("-p", "--portrait", action="store_true", help="the paper to print on is in oriented as a portrait")
    #parser.add_argument("-r", "--rotate", action="store_true", help="rotate the svg with 90 degrees")
    parser.add_argument("-l", "--log", action="store_true", help="log what is happening")
    args = parser.parse_args()

    saveScaledSvgString(args)
    

if __name__ == "__main__":
    main()
