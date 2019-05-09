import argparse
import os
import re
import xml.etree.ElementTree as ET
import sys

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

def addText(args):
    root = getRoot(args)
    svgSize = getSvgSize(root)
    style = 'fill:none;stroke:#000;stroke-width:{};opacity:1'.format(args.stroke_width/PIXEL_TO_MM_MULT)
    path = getText_alphabet1(args.text, svgSize[0]*(1-args.border_size), svgSize[1]*(1-args.border_size), svgSize[0]*args.text_size)
    root.append(ET.Element("path", d=path, style=style))
    saveRoot(root, args)
    if args.log:
        print("added Text: " + args.text, file=sys.stderr)

def getText_alphabet1(text, endX, y, height):
    def getPath(charArray, l, x, y):
        path = ""
        for line in charArray:
            path += "M{},{}".format(line[0]*l+x, -line[1]*l+y)
            for i in range(2, len(line), 2):
                path += "L{},{}".format(line[i]*l+x, -line[i+1]*l+y)

        return path

    baseLength = height/7
    alphabet = {
        "?": [[0,7,3,7,4,6,3,5,1,5,0,4,1,3,4,3],[2,0,2,1,3,1,3,0,2,0]],
        ".": [[1,0,1,1,2,1,2,0,1,0]],
        "-": [[1,3,3,3]],
        "=": [[1,4,3,4],[1,2,3,2]],
        "/": [[0,0,1,1,1,2,2,3,2,4,3,5,3,6,4,7]],
        "0": [[0,1,0,5,1,6,3,6,4,5,4,1,3,0,1,0,0,1]],
        "1": [[0,4,2,6,2,0],[1,0,3,0]],
        "2": [[0,5,1,6,3,6,4,5,4,4,0,0,4,0]],
        "3": [[0,5,1,6,3,6,4,5,4,4,3,3,1,3],[3,3,4,2,4,1,3,0,1,0,0,1]],
        "4": [[3,0,3,6,0,3,4,3]],
        "5": [[4,6,0,6,0,4,3,4,4,3,4,1,3,0,0,0]],
        "6": [[4,5,3,6,1,6,0,5,0,1,1,0,3,0,4,1,4,2,3,3,1,3,0,2]],
        "7": [[0,6,4,6,3,5,3,4,2,3,2,2,1,1,1,0]],
        "8": [[3,3,4,4,4,5,3,6,1,6,0,5,0,4,1,3,3,3,4,2,4,1,3,0,1,0,0,1,0,2,1,3]],
        "9": [[4,4,3,3,1,3,0,4,0,5,1,6,3,6,4,5,4,1,3,0,1,0,0,1]],
        "a": [[4,1,3,0,1,0,0,1,0,3,1,4,3,4,4,3,4,0]],
        "b": [[0,7,0,0],[0,3,1,4,3,4,4,3,4,1,3,0,0,0]],
        "c": [[4,3,3,4,1,4,0,3,0,1,1,0,3,0,4,1]],
        "d": [[4,7,4,0],[4,3,3,4,1,4,0,3,0,1,1,0,3,0,4,1]],
        "e": [[0,2,4,2,4,3,3,4,1,4,0,3,0,1,1,0,3,0,4,1]],
        "f": [[4,7,3,7,2,6,2,0],[1,3,3,3]],
        "g": [[0,-2,1,-3,3,-3,4,-2,4,3,4,3,3,4,1,4,0,3,0,1,1,0,3,0,4,1]],
        "h": [[0,7,0,0],[0,3,1,4,3,4,4,3,4,0]],
        "i": [[2,6,2,5],[1,4,2,4,2,0],[1,0,3,0]],
        "j": [[2,6,2,5],[1,4,2,4,2,0,1,-1]],
        "k": [[1,7,1,0],[1,2,2,2,4,4],[2,2,4,0]],
        "l": [[1,7,2,7,2,0],[1,0,3,0]],
        "m": [[0,4,0,0],[0,3,1,4,2,3,2,0],[2,3,3,4,4,3,4,0]],
        "n": [[0,0,0,4],[0,3,1,4,3,4,4,3,4,0]],
        "o": [[1,0,0,1,0,3,1,4,3,4,4,3,4,1,3,0,1,0]],
        "p": [[0,-3,0,1,0,3,1,4,3,4,4,3,4,1,3,0,0,0]],
        "q": [[4,0,1,0,0,1,0,3,1,4,3,4,4,3,4,-3]],
        "r": [[1,0,1,4],[1,3,2,4,3,4]],
        "s": [[4,4,1,4,0,3,1,2,3,2,4,1,3,0,0,0]],
        "t": [[2,7,2,1,3,0,4,1],[1,3,3,3]],
        "u": [[0,4,0,1,1,0,3,0,4,1],[4,4,4,0]],
        "v": [[0,4,0,3,1,2,1,1,2,0,3,1,3,2,4,3,4,4]],
        "w": [[0,4,0,1,1,0,2,1,2,4],[2,1,3,0,4,1,4,4]],
        "x": [[0,4,4,0],[0,0,4,4]],
        "y": [[0,4,0,1,1,0,3,0,4,1],[4,4,4,-2,3,-3,1,-3,0,-2]],
        "z": [[0,4,4,4,0,0,4,0],[1,2,3,2]],
    }
    
    path = ""
    for i in range(len(text)):
        x = endX-(5*len(text)-i*(5))*baseLength
        if text[i] in alphabet:
            #print(text[i])
            path += getPath(alphabet[text[i]], baseLength, x, y)
    return path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text", help="text to write")
    parser.add_argument("-i", "--input_path", help="path to a svg file")
    parser.add_argument("-o", "--output_path", help="path of the output svg file")
    parser.add_argument("-l", "--log", action="store_true", help="log what is happening")
    parser.add_argument("-s", "--text_size", default=0.022, type=float, help="size of the text as a percentage of the svg width")
    parser.add_argument("-b", "--border_size", default=0.022, type=float, help="size of the right and bottom border as a percentage of the svg width")
    parser.add_argument("-w", "--stroke_width", default=2, type=float, help="stroke width of the text in mm")
    
    args = parser.parse_args()

    addText(args)
    

if __name__ == "__main__":
    main()