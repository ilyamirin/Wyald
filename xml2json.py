import os
import sys

import xmltodict, json

categoryList = dict()

def xml2json(path, filename, data):
    jsonData = {}
    o = xmltodict.parse(data)
    imgList = o['dataset']["images"]["image"]
    for image in imgList:
        imgIdx = image['@frame']
        x1 = int(image['box']['@left'])
        y1 = int(image['box']['@top'])
        x2 = x1 + int(image['box']['@width'])
        y2 = y1 + int(image['box']['@height'])
        jsonData[os.path.join(path, filename[:-8], f"{filename[:-8]}-{imgIdx}.png")] = {
            'category' : filename[:-11],
            'coords' : [ y1, x1, y2, x2 ]
        }
        if not filename[:11] in categoryList:
            count = len(categoryList)
            categoryList[filename[:-11]] = count

    return jsonData


def tryCreateDirectory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        return path
    return None # todo rm ?


def main(argv):
    rootDir = argv[0]
    xmlDir = os.path.join(rootDir, 'xml')
    frameDir = os.path.join(rootDir, 'frames')

    for filename in os.listdir(xmlDir):
        coinDir = os.path.join(frameDir, filename[:-8])

        path = os.path.join(xmlDir, filename)
        file = open(path, "r")

        jsonData = xml2json(frameDir, filename, file.read())
        json.dump(jsonData, open(os.path.join(coinDir, 'mark.json'), 'w'), indent=3)
    json.dump(categoryList, open(os.path.join(rootDir, 'categories.txt'), 'w'), indent=3)


if __name__ == "__main__":
    main(sys.argv[1:])