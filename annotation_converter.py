import os
import argparse

import xmltodict, json

from colorama import Fore, Style

from utils import makeJSONname, extractCategory
from config import Extensions, Constants as const
from config import Annotation


def xml2json(xmlPath, wpath=None, overwrite=False):
    jsonData = {}
    category, basename = extractCategory(xmlPath)
    jsonName = makeJSONname(basename)

    if wpath is not None:
        os.makedirs(wpath, exist_ok=True)
        if not overwrite and os.path.exists(os.path.join(wpath, jsonName)):
            print(f"{Fore.RED}JSON {jsonName} already exists in {wpath} {Style.RESET_ALL}")
            return
        elif overwrite and os.path.exists(os.path.join(wpath, jsonName)):
            print(f"{Fore.RED}JSON {jsonName} will be overwritten in {wpath} {Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}JSON {jsonName} will be written to {wpath} {Style.RESET_ALL}")

    try:
        file = open(os.path.join(xmlPath), "r")
        data = file.read()
        o = xmltodict.parse(data)
        imgList = o["dataset"]["images"]["image"]
    except:
        print(f"{Fore.RED} Couldn't parse {xmlPath}")
        return {}, None

    for image in imgList:
        if not "@frame" in image:
            # print(f"{Fore.RED} {filename} : The attribute '@frame' was not found")
            continue

        imgIdx = image['@frame']
        x1 = int(image['box']['@left'])
        y1 = int(image['box']['@top'])
        x2 = x1 + int(image['box']['@width'])
        y2 = y1 + int(image['box']['@height'])

        subCategory = image.get("@category", const.merged)

        jsonData[f"frame_{imgIdx}"] = {
            const.category: category,
            const.subcategory: subCategory,
            const.coords: [y1, x1, y2, x2]
        }

    if wpath is not None:
        json.dump(jsonData, open(os.path.join(wpath, jsonName), "w"), indent=3)

    return jsonData


def xml2jsonFromFolder(rpath, wpath, overwrite=False):
    filenames = [name for name in os.listdir(rpath) if name.endswith(Extensions.xml)]

    for filename in filenames:
        xml2json(
            xmlPath=os.path.join(rpath, filename),
            wpath=wpath,
            overwrite=overwrite
        )


def makeArgumentsParser():
    parser = argparse.ArgumentParser()

    parser.add_argument("--rpath", help="Path to folder with xml-files which should be converted")
    parser.add_argument("--wpath", help="Path to folder where json-files will be written (overwritten)")
    parser.add_argument("--overwrite", help="Whether overwrite existing json-files", action="store_true")

    return parser


def json2txt(jsonPath):
    txtPath = os.path.join(os.path.dirname(jsonPath), Annotation.txt)
    for group in os.listdir(jsonPath):
        os.makedirs(os.path.join(txtPath, group))


if __name__ == "__main__":
    parser = makeArgumentsParser()
    args = parser.parse_args()

    xml2jsonFromFolder(
        rpath=args.rpath,
        wpath=args.wpath,
        overwrite=args.overwrite
    )