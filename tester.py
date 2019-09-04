import re
import json

import augmentations_kit as ak

from xml2json import xml2jsonFromFolder
from verifier import crossMatchVideoAndMarks, actualizeInfoWithJsons, actualizeInfoWithFrames
from framing import processVideoFolder
from augmentation import augmentDatasetWithGenerator
from darknet_preparation import cleanOldMarks, extractMarksThroughDataset, makeSets
from config import Path, Extensions, Constants as const


def test():
    # try:
    #     actualizeInfoWithFrames(Path.dataset)
    # except:
    #     pass

    xml2jsonFromFolder(
        rpath=Path.rawXml,
        wpath=Path.rawJson
    )

    # crossMatchVideoAndMarks(
    #     marks=Path.rawJson,
    #     videos=Path.rawVideos
    # )

    # processVideoFolder(
    #     folderPath=Path.rawVideos,
    #     marksPath=Path.rawJson,
    #     datasetPath=Path.dataset,
    #     overwrite=False
    # )

    # actualizeInfoWithFrames(Path.dataset)

    # augmentations = ak.cartoonAugs
    #
    # augmentDatasetWithGenerator(
    #     augmentationName="augmented",
    #     augmentations=augmentations,
    #     imageExtension=Extensions.jpg,
    #     multiplier=2,
    #     parallel=True
    # )
    #
    # print()
    # actualizeInfoWithFrames(Path.dataset)
    # #
    #
    # extractMarksThroughDataset(Path.dataset)
    # makeSets([Path.dataset])


def prettifyNames(path):
    import os
    for filename in os.listdir(path):
        s = filename.replace("-", "_")
        pos = s.rfind('_')
        s = list(s)
        s[pos] = '-'
        newName = "".join(s)
        os.rename(os.path.join(path, filename), os.path.join(path, newName))


def check(augList):
    import json
    from collections import Counter

    with open(Path.actualInfo) as f:
        info = json.load(f)

    mySum = {}
    print("{:>50} : {:>10} {:>10} {:>10} {:>10} {:>10}".format("coin name", "original", "augmented", "avers", "revers", "merged"))

    for coinName in info["original"].keys():
        aSum, rSum, mSum = 0, 0, 0
        counter = Counter()

        for aug in augList:
            counter[aug] = info[aug][coinName]["overall"]

            if not aug in info or not coinName in info[aug]:
                continue
            if 'avers' in info[aug][coinName]:
                aSum += info[aug][coinName]['avers']
            if 'reverse' in info[aug][coinName]:
                rSum += info[aug][coinName]['reverse']
            if 'revers' in info[aug][coinName]:
                rSum += info[aug][coinName]['revers']
            if 'merged' in info[aug][coinName]:
                mSum += info[aug][coinName]['merged']

            mySum[coinName] = counter
        print("{:>50} : {:>10} {:>10} {:>10} {:>10} {:>10}".
              format(coinName, mySum[coinName]['original'], mySum[coinName]['augmented'], aSum, rSum, mSum))


def main():
    # check(["augmented", "original"])
    # prettifyNames(r"D:\projects\coins\test_data\raw_data\json")
    try:
        actualizeInfoWithFrames(Path.dataset)
    except:
        pass
    #
    # xml2jsonFromFolder(
    #     rpath=Path.rawXml,
    #     wpath=Path.rawJson
    # )
    #
    # crossMatchVideoAndMarks(
    #     marks=Path.rawJson,
    #     videos=Path.rawVideos
    # )
    #
    # processVideoFolder(
    #     folderPath=Path.rawVideos,
    #     marksPath=Path.rawJson,
    #     datasetPath=Path.dataset,
    #     overwrite=False
    # )
    import os

    # augmentations = ak.cartoonAugs


    # augmentDatasetWithGenerator(
    #     augmentationName="augmented",
    #    augmentations=ak.customAugmentations,
    #     imageExtension=Extensions.png,
    #     overwrite=False,
    #     multiplier=2,
    #     parallel=True
    # )

    # extractMarksThroughDataset(os.path.join(Path.dataset))
    makeSets([
        os.path.join(Path.dataset)
    ])


def fixJsons():
    import os
    from utils import walk, readLines

    categories = readLines(Path.categories)
    jsons = walk(Path.dataset, targetFiles="marks.json").get("files")

    for i, jsn in enumerate(jsons):
        print(f"\rProcessing {i} json file", end="")

        path = os.path.join(Path.dataset, *jsn)
        marks = json.load(open(path, "r"))
        for name, items in marks.items():
            ctgIdx = categories.index(items[const.fullCategory])

            items[const.ctgIdx] = ctgIdx

        json.dump(marks, open(path, "w"), indent=3)


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

            originalPath = os.path.join(Path.dataset, const.original, category, subcategory)
            augmentedPath = os.path.join(Path.dataset, const.augmented, category, subcategory)

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
        subcategories=[const.avers],
        extractionPath=Path.original,
        framesLimit=1000,
        augmentationsLimit=1000,
        augmentationFunc=const.default,
        augmentationName="augmented",
        augmentationPath=None,
        parallel=True, threads=16,
        overwriteOriginal=False,
        overwriteAugmented=False
    )


if __name__ == "__main__":
    smartTest()