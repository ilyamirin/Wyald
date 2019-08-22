import os
import sys
import glob

import xmltodict, json
from lxml import etree
import xmlschema

categoryList = dict()

def xml2json(path, filename, data):

    if not xmlschema.validate(data):
        print(f"{filename} is invalid")
        return {}

    o = xmltodict.parse(data)
    imgList = o['dataset']["images"]["image"]

    jsonData = {}
    for image in imgList:
        if not "@frame" in image:
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
        jsonData[os.path.join(path, filename[:-8], f"{filename[:-8]}-{imgIdx}.jpg")] = {  # cut 9 symbols '.MOV.xml'
            'category': category,  # cut 7 symbols '-v1.MOV.xml' or '-v{n}.xml'
            'coords': [y1, x1, y2, x2]
        }

        if not category in categoryList:
            count = len(categoryList)
            categoryList[category] = count

    return jsonData


def tryCreateDirectory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return path

    return None # todo rm ?


def main():
    rootDir = r"E:\data\coins"

    xmlDir = os.path.join(rootDir, 'xml')
    frameDir = os.path.join(rootDir, 'frames')
    videoDir = os.path.join(rootDir, 'sber', 'video')

    for dir in os.listdir(xmlDir):
        for filename in os.listdir(os.path.join(xmlDir, dir)):
            videoPath = os.path.join(videoDir, filename[:-4])
            if not os.path.exists(videoPath):
                continue

            path = os.path.join(xmlDir, dir, filename)
            file = open(os.path.join(path), "r")
            print(path)
            jsonData = xml2json(frameDir, filename, file.read())
            if jsonData == {}:
                continue
            coinDir = os.path.join(frameDir, filename[:-8])
            if not os.path.exists(coinDir):
                os.mkdir(coinDir)
            # json.dump(jsonData, open(os.path.join(coinDir, 'mark.json'), 'w'), indent=3)

    f = open(os.path.join(rootDir, 'categories.txt'), 'w')
    json.dump(categoryList, f, indent=3)
    for val in categoryList:
        f.writelines(f'\n"{val}" : "{val.replace("_", "-")}",')
    for val in categoryList:
        f.writelines(f"\n{val}")


if __name__ == "__main__":
    main()