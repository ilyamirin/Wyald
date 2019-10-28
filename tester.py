import os

import cv2
from annotation_converter import xml2jsonFromFolder
from verifier import actualizeInfoWithFrames
from framing import processVideoFolder
from darknet_preparation import makeSets
from config import Path, Extensions, Constants


def parseTxtFile(filePath):
    rectangles = []
    if not os.path.exists(filePath):
        return rectangles

    with open(filePath, "r") as file:
        for line in file.readlines():
            rectangles.append(list(map(float, line.rstrip().split(' '))))

    return rectangles


def testMarkOnFrame(dirName):
    frameDir = os.path.join(Path.root, 'marked', Constants.frames)
    txtDir = os.path.join(Path.root, 'marked', dirName)

    for filename in os.listdir(frameDir):
        framePath = os.path.join(frameDir, filename)

        frame = cv2.imread(framePath)
        h, w, d = frame.shape

        name, ext = os.path.splitext(filename)
        rects = parseTxtFile(os.path.join(txtDir, f"{name}{Extensions.txt}"))

        for ctgTdx, xc, yc, tw, th in rects:
            x1 = int((xc - tw*0.5)*w)
            y1 = int((yc + th*0.5)*h)
            x2 = int(x1 + tw*w)
            y2 = int(y1 - th*h)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 00), 2)

        cv2.imshow("output", frame)
        cv2.waitKey(3)


def makeDividedSets():
    ctgInPart = 35
    import os
    from math import ceil
    from utils import readLines, writeLines
    from verifier import splitFullCategory

    categories = readLines(Path.categories)
    divisions = ceil(len(categories) / ctgInPart)
    categories = [categories[i * ctgInPart:(i + 1) * ctgInPart] for i in range(divisions)]

    for i, ctgList in enumerate(categories):

        pathsList = []
        for ctg in ctgList:
            category, subcategory = splitFullCategory(ctg)

            originalPath = os.path.join(Path.dataset, Constants.original, category, subcategory)
            augmentedPath = os.path.join(Path.dataset, Constants.augmented, category, subcategory)

            pathsList.extend([originalPath, augmentedPath])

        setPath = os.path.join(Path.sets, f"part_{i}")
        makeSets(pathsList, wpath=setPath, trainPart=0.9, validPart=0.05)

        writeLines(ctgList, os.path.join(setPath, "set_categories.txt"))


def smartTest():
    from prepare_jsons import fixFrameNumbers, summarizeInfo
    from smart_framing import extractCategories

    xml2jsonFromFolder(
        rpath=Path.rawXml,
        wpath=Path.rawJson
    )

    fixFrameNumbers(Path.rawJson)
    summarizeInfo()

    extractCategories(
        videosPath=Path.rawVideos,
        summarizedPath=Path.summarizedRaw,
        categoriesList=None,
        subcategories=[Constants.avers],
        extractionPath=Path.original,
        framesLimit=1000,
        augmentationsLimit=1000,
        augmentationFunc=Constants.default,
        augmentationName="augmented",
        augmentationPath=None,
        parallel=True, threads=16,
        overwriteOriginal=False,
        overwriteAugmented=False
    )


def main():
    smartTest()
    

if __name__ == "__main__":
    main()