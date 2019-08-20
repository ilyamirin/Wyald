import os
import sys
import glob

import xmltodict, json
from lxml import etree

categoryList = dict()

def xml2json(path, filename, data):
    jsonData = {}

    o = xmltodict.parse(data)

    if not 'dataset' in o or not 'images' in o['dataset'] or not 'image' in o['dataset']['images']:
        print('xml is incorrect' )
        return {}

    imgList = o['dataset']["images"]["image"]
    for image in imgList:
        imgIdx = image['@frame']
        x1 = int(image['box']['@left'])
        y1 = int(image['box']['@top'])
        x2 = x1 + int(image['box']['@width'])
        y2 = y1 + int(image['box']['@height'])

        jsonData[os.path.join(path, filename[:-4], f"{filename[:-4]}-{imgIdx}.png")] = { # cut 4 symbols '.xml'
            'category' : filename[:-7], # cut 7 symbols '-v1.xml' or '-v{n}.xml'
            'coords' : [ y1, x1, y2, x2 ]
        }
        if not filename[:7] in categoryList:
            count = len(categoryList)
            categoryList[filename[:-7]] = count

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

    # if not os.path.exists(xmlDir):
    #     os.mkdir(xmlDir)
    #     imgsDir = os.path.join(rootDir,  'imgs')
    #
    #     for dir in os.listdir(imgsDir):
    #         flist = glob.glob(os.path.join(imgsDir, dir, '*.xml'))
    #         fin = open(os.path.join(imgsDir, dir, flist[0]), 'r')
    #         fout = open(os.path.join(xmlDir, f"{dir}.xml"), 'w')
    #         data = fin.read()
    #         fout.write(data)

    for filename in os.listdir(xmlDir):
        coinDir = os.path.join(frameDir, filename[:-4])
        if not os.path.exists(coinDir):
            os.mkdir(coinDir)
        path = os.path.join(xmlDir, filename)
        file = open(os.path.join(path), "r")
        print(path)
        jsonData = xml2json(frameDir, filename, file.read())
        json.dump(jsonData, open(os.path.join(coinDir, 'mark.json'), 'w'), indent=3)

    f = open(os.path.join(rootDir, 'categories.txt'), 'w')
    json.dump(categoryList, f, indent=3)
    for val in categoryList:
        f.writelines(f"\n{val}",)


if __name__ == "__main__":
    main(sys.argv[1:])