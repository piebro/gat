import argparse
import os
from pathlib import Path

parser = argparse.ArgumentParser(description='Opens the link(s) in the chrome headless browser, presses the "s" key, waits for a download prompt, confirms it and downloads the data.')

parser.add_argument("link", type=str, nargs="+", help="One or more Links to a .html website or local .html document")
parser.add_argument("--website_folder", "-wf", type=str, default="", help="Path to a website root folder. All relevant website files need to be in the folder.")
parser.add_argument("--output_folder", "-o", type=str, default="", help="Path to the output folder.")

args = parser.parse_args()

if args.output_folder == "":
    args.output_folder = os.getcwd() + "/images"
else:
    args.output_folder = os.path.expanduser(args.output_folder)
    args.output_folder = os.path.abspath(args.output_folder)

print("saving to: " + args.output_folder)

cmd = [
    "docker run",
    "-v '{0}:{0}'".format(args.website_folder),
    "-v '{0}:/script'".format(os.getcwd()),
    "-v '{0}:/images'".format(args.output_folder),
    "buildkite/puppeteer:latest",
    "bash -c '",
        "node /script/index.js",
            "\"" + str(args.link).replace("'", "\\\"") + "\"",
        "&& chmod --recursive 764 /images",
        "&& chown --recursive 1000:1000 /images'"
]

os.system(" ".join(cmd))
