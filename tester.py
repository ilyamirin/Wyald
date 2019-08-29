from xml2json import xml2jsonFromFolder
from verifier import crossMatchVideoAndMarks, actualizeInfoWithJsons, actualizeInfoWithFrames
from framing import processVideoFolder
from augmentation import augmentDatasetWithGenerator
from darknet_preparation import cleanOldMarks, extractMarksThroughDataset, makeSets
from config import Path, Extensions, Constants as const
import augmentations_kit as ak

def test():
    try:
        actualizeInfoWithFrames(Path.dataset)
    except:
        pass

    xml2jsonFromFolder(
        rpath=Path.rawXml,
        wpath=Path.rawJson
    )

    crossMatchVideoAndMarks(
        marks=Path.rawJson,
        videos=Path.rawVideos
    )

    processVideoFolder(
        folderPath=Path.rawVideos,
        marksPath=Path.rawJson,
        datasetPath=Path.dataset,
        overwrite=False
    )

    # actualizeInfoWithFrames(Path.dataset)

    augmentations = ak.cartoonAugs

    augmentDatasetWithGenerator(
        augmentationName="augmented",
        augmentations=augmentations,
        imageExtension=Extensions.png,
        multiplier=2,
        parallel=True
    )

    print()
    actualizeInfoWithFrames(Path.dataset)
    #

    extractMarksThroughDataset(Path.dataset)
    makeSets([Path.dataset])

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
    with open(Path.actualInfo) as f:
        info = json.load(f)

    for coinName in info["original"].keys():
        aSum, rSum, mSum = 0, 0, 0
        for aug in augList:
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
        print("{:>50} : {:>10} {:>10} {:>10}".format(coinName, aSum, rSum, mSum))
def main():

    try:
        actualizeInfoWithFrames(Path.dataset)
    except:
        pass

    # import os
    #
    # augmentations = ak.cartoonAugs
    #
    # augmentDatasetWithGenerator(
    #     augmentationName="hsl_yuv",
    #     augmentations=augmentations,
    #     imageExtension=Extensions.png,
    #     multiplier=2,
    #     parallel=True
    # )
    #
    # extractMarksThroughDataset(os.path.join(Path.dataset, "hsl_yuv"))
    # makeSets([
    #     os.path.join(Path.dataset, "hsl_yuv")
    # ])


if __name__ == "__main__":
    main()