import os
import sys
import glob

import xmltodict, json
import xmlschema
from colorama import Fore, Back, Style

categoryList = dict()

def xml2json(path, filename, xmlPath):
    o = {}
    try:
        file = open(os.path.join(xmlPath), "r")
        data = file.read()
        o = xmltodict.parse(data)
    except:
        print(f"{Fore.RED} Couldn't parse {xmlPath}")
        return {}, None

    imgList = o['dataset']["images"]["image"]

    jsonData = {}
    for image in imgList:
        if not "@frame" in image:
            print(f"{Fore.RED} {filename} : The attribute '@frame' was not found")
            continue

        imgIdx = image['@frame']
        x1 = int(image['box']['@left'])
        y1 = int(image['box']['@top'])
        x2 = x1 + int(image['box']['@width'])
        y2 = y1 + int(image['box']['@height'])

        subCategory = f"-{image['@category']}" if '@category' in image else ""
        if subCategory != "":
            filename.replace(f"-{subCategory}", "")

        category = f"{filename[:-11]}{subCategory}"
        category = category.replace("_", "-")
        jsonData[os.path.join(path, category, f"{filename[:-8]}-{imgIdx}.jpg")] = {  # cut 8 symbols '.MOV.xml'
            'category': category,  # cut 7 symbols '-v1.MOV.xml' or '-v{n}.xml'
            'coords': [y1, x1, y2, x2]
        }

        if not category in categoryList:
            count = len(categoryList)
            categoryList[category] = {
                "categoryIndex": count,
                "name": category.replace("_", "-")
            }

    return jsonData, category


def checkDir(path, toCreate=False):
    if os.path.exists(path):
        return path
    if toCreate:
        os.mkdir(path)
        print(f"{Fore.GREEN} The directory {path} was create")
        return path
    print(f"{Fore.RED} The directory {path} is not found...")
    exit(1)


def tryLoadJsonData(pathToFile):
    if not os.path.exists(pathToFile):
        return {}
    res = None
    try:
        res = json.load(open(pathToFile, 'r'))
    except:
        return {}

    return res


def main():
    rootDir = r"D:\Projects\coins-project\data"

    xmlDir = checkDir(os.path.join(rootDir, 'xml'))
    frameDir = checkDir(os.path.join(rootDir, 'frames'), toCreate=True)
    coinsDir = checkDir(os.path.join(rootDir, 'sber'))
    videoDir = checkDir(os.path.join(coinsDir, 'video'))

    fileProcessDataPath = os.path.join(rootDir, 'process-data.txt')
    jProcessData = tryLoadJsonData(fileProcessDataPath)
    foutProcess = open(fileProcessDataPath, 'w')

    for dir in os.listdir(xmlDir):
        for filename in os.listdir(os.path.join(xmlDir, dir)): # filename ends '.MOV.xml'
            jpd = {}

            videoPath = os.path.join(videoDir, filename[:-4]) # cut 4 symbols '.xml'
            if not os.path.exists(videoPath):
                print(f"{Fore.RED} Videofile {videoPath} is not found")
                continue

            path = os.path.join(xmlDir, dir, filename)
            jpd['video'] = videoPath
            jpd['path'] = path
            print(Style.RESET_ALL)
            print(f"Start process file {path}")
            jsonData, category = xml2json(frameDir, filename, path)

            if jsonData == {}:
                print(f"{Fore.RED} The file {filename} is invalid")
                continue

            markJsonPath = os.path.join(originDir, 'mark.json')
            json.dump(jsonData, open(markJsonPath, 'a'), indent=3)
            jpd['jsonPath'] = markJsonPath

            jProcessData[filename] = jpd

    f = open(os.path.join(rootDir, 'categories.txt'), 'w')
    json.dump(categoryList, f, indent=3)
    json.dump(jProcessData, foutProcess, indent=3)
    json.dump(jProcessData, foutProcess, indent=3)
    foutProcess.close()


if __name__ == "__main__":
    main()