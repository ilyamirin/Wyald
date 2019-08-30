import os
import json

import cv2

from colorama import Fore, Style

from verifier import actualizeInfoWithFrames, downloadActualInfo, getFullCategory, fitCoords, splitFullCategory
from utils import makeJSONname, openJsonSafely, extractBasename, extendName, readLines, writeLines, getNested, updateNested, putNested
from config import Extensions, Path, Constants as const


def getKeysOffset(keys):
    keys = list(keys)
    keys = sorted([int(l.split("_")[-1]) for l in keys]) # key == "frame_{idx}"

    return keys[0]


def getFrameMarks(idx, marks, offset):
    frameID = f"frame_{idx}"

    if frameID not in marks:
        print(f"\n{frameID} was not found, trying with offset")
        frameID = "frame_{}".format(idx + offset)

    if frameID not in marks:
        print(f"{frameID} was not found, continuing")
        return {}
    else:
        return marks[frameID]


def frameVideo(filePath, marksPath, datasetPath, actualInfo, overwrite=False, extension=Extensions.jpg, params=None,
               ctgLimit=None):

    categories = readLines(Path.categories)
    basename = extractBasename(filePath)

    try:
        jsonName = makeJSONname(basename)
        marks = json.load(open(os.path.join(marksPath, jsonName), "r"))
    except:
        print(f"{Fore.RED}There is no json file {marksPath} for {filePath} {Style.RESET_ALL}")
        return

    framesGenerator = generateFrames(filePath)
    offset = getKeysOffset(marks.keys())
    marksSeparated = {}
    total = 0
    for idx, frame in enumerate(framesGenerator):
        # if idx == 20:
        #     break

        frameMarks = getFrameMarks(idx, marks, offset)
        if not frameMarks:
            continue

        category = frameMarks[const.category]
        subcategory = frameMarks[const.subcategory]

        countKeys = [const.original, category, subcategory]
        if idx == 0:
            globalIdx = getNested(dictionary=actualInfo, keys=countKeys, default=0)

        localIdx = idx + globalIdx
        if ctgLimit is not None and localIdx == ctgLimit:
            break

        frameID = f"frame_{localIdx}"
        fullCategory = getFullCategory(category, subcategory)

        if fullCategory not in categories:
            categories.append(fullCategory)

        ctgIdx = categories.index(fullCategory)
        frameName = f"{fullCategory}{const.separator}{frameID}{const.separator}{const.original}"

        dirPath = os.path.join(datasetPath, const.original, category, subcategory)
        framesPath = os.path.join(dirPath, const.frames)
        framePath = os.path.join(framesPath, extendName(frameName, extension))

        updateNested(dictionary=actualInfo, keys=countKeys, value=1)
        if not overwrite and os.path.exists(framePath):
            print("\rFrame #{} has been passed".format(idx), end="")
            continue

        os.makedirs(framesPath, exist_ok=True)

        frameInfo = {
            const.image: extendName(frameName, extension),
            const.coords: fitCoords(frameMarks[const.coords], frame.shape[:2]),
            const.fullCategory: fullCategory,
            const.ctgIdx: ctgIdx,
            const.imageShape: frame.shape[:2]
        }

        keySet = countKeys + [frameName] # ["original", category, subcategory, frameName]
        putNested(dictionary=marksSeparated, keys=keySet, value=frameInfo)

        cv2.imwrite(framePath, frame, params)
        total += 1

        print("\rFrame #{} has been added".format(idx), end="")

    marksSeparated = marksSeparated[const.original]
    print()
    for ctg, value in marksSeparated.items():
        for subctg, subctgMarks in value.items():
            subctgMarksJson = os.path.join(datasetPath, const.original, ctg, subctg,
                                           extendName(const.marks, Extensions.json))

            oldMarks = openJsonSafely(subctgMarksJson)
            for k, v in subctgMarks.items():
                oldMarks[k] = v

            json.dump(oldMarks, open(subctgMarksJson, "w"), indent=3)

            print(f"{Fore.GREEN}Added marks to {subctgMarksJson} {Style.RESET_ALL}")

    writeLines(categories, Path.categories)
    print(f"{Fore.GREEN}Updated categories file {Path.categories} {Style.RESET_ALL}")
    print(f"{Fore.GREEN}Added {total} frames in total {Style.RESET_ALL}")


def frameWithAugmentation(filePath, marksPath, datasetPath, actualInfo, overwrite=False, extension=Extensions.jpg,
                          params=None, ctgLimit=None):
    pass


def getSameCtgVideo(categories, files):
    filesDict = {}
    for category in categories:
        filesDict[category] = [f for f in files if category in f]

    return filesDict


def calcFrames(videosPath, videosDict):
    for ctg, videosList in videosDict.items():
        pass


def frameFolderSmart(folderPath, ctgLimit):
    processedVideos = readLines(Path.processedFiles)
    fullCategories = readLines(Path.fullCategories)

    videos = [video for video in os.listdir(folderPath) if video and video.endswith(Extensions.videos())]

    videosByCtgs = getSameCtgVideo(fullCategories, videos)




    pass


def generateFrames(videoPath):
    cap = cv2.VideoCapture(videoPath)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        yield frame


def processVideoFolder(folderPath=Path.rawVideos, marksPath=Path.rawJson, datasetPath=Path.dataset, overwrite=False,
                       extension=Extensions.jpg, params=None):

    processedVideos = readLines(Path.processedFiles)
    videos = [video for video in os.listdir(folderPath) if video not in processedVideos and
              (video.endswith(Extensions.mov) or video.endswith(Extensions.mp4))]

    actualInfo = downloadActualInfo()

    for video in videos:
        actualizeInfoWithFrames(Path.dataset)
        filePath = os.path.join(folderPath, video)

        print(f"\n{Fore.GREEN}Video {filePath} is being processed {Style.RESET_ALL}")
        frameVideo(
            filePath=filePath,
            marksPath=marksPath,
            datasetPath=datasetPath,
            actualInfo=actualInfo,
            overwrite=overwrite,
            extension=extension,
            params=params
        )

        processedVideos.append(video)

        writeLines(set(processedVideos), Path.processedFiles)


def main():
    pass


if __name__ == "__main__":
    main()