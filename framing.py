import os
import json

import cv2

from colorama import Fore, Style

from verifier import actualizeInfoWithFrames, downloadActualInfo
from utils import makeJSONname, extractCategory, extractBasename, extendName, readLines, writeLines, getNested, updateNested, putNested
from config import Extensions, Path, Constants as const


lastIdx = dict()


def frameVideo(filePath, marksPath, datasetPath, actualInfo, overwrite=False, extension=Extensions.png, params=None):
    categories = readLines(Path.categories)
    basename = extractBasename(filePath)

    try:
        jsonName = makeJSONname(basename)
        marks = json.load(open(os.path.join(marksPath, jsonName), "r"))
    except:
        print(f"{Fore.RED} There is no json file {marksPath} for {filePath} {Style.RESET_ALL}")
        return

    framesGenerator = generateFrames(filePath)

    marksSeparated = {}
    total = 0
    for idx, frame in enumerate(framesGenerator):
        frameID = f"frame_{idx}"
        if frameID not in marks:
            continue
        else:
            frameMarks = marks[frameID]

        category = marks.get(const.category)
        subcategory = marks.get(const.subcategory)

        countKeys = [const.original, category, subcategory]
        categoryCountIdx = getNested(actualInfo, countKeys, 0)

        if subcategory != const.merged:
            subcategory = "_" + subcategory

        idx += categoryCountIdx
        frameID = f"frame_{idx}"
        fullCategory = f"{category}{subcategory}"

        if fullCategory not in categories:
            categories.append(fullCategory)

        ctgIdx = categories.index(fullCategory)
        frameName = f"{fullCategory}{const.separator}{frameID}{const.separator}{const.original}"

        frameInfo = {
            const.image: extendName(frameName, extension),
            const.coords: frameMarks[const.coords],
            const.fullCategory: fullCategory,
            const.ctgIdx: ctgIdx,
            const.imageShape: frame.shape[:2]
        }

        keySet = countKeys[1:].append(frameName)
        putNested(marksSeparated, keySet, frameInfo)

        dirPath = os.path.join(datasetPath, const.original, category, subcategory)
        framesPath = os.path.join(dirPath, const.frames)

        framePath = os.path.join(framesPath, frameName)
        if not overwrite and os.path.exists(framePath):
            continue
        os.makedirs(framesPath, exist_ok=True)

        cv2.imwrite(framePath, frame, params)
        total += 1

        updateNested(actualInfo, countKeys, 1)
        print("\rFrame #{} has been added".format(idx), end="")

    for ctg, value in marksSeparated.items():
        for subctg, subctgMarks in value.items():
            subctgMarksJson = os.path.join(datasetPath, const.original, ctg, subctg,
                                           extendName(const.marks, Extensions.json))

            json.dump(subctgMarks, open(subctgMarksJson, "w"), indent=3)

            print(f"\n{Fore.GREEN} Added marks to {subctgMarksJson} {Style.RESET_ALL}")

    writeLines(categories, Path.categories)
    print(f"\n{Fore.GREEN} Updated categories file {Path.categories} {Style.RESET_ALL}")
    print(f"\n{Fore.GREEN} Added {total} frames in total {Style.RESET_ALL}")


def generateFrames(videoPath):
    cap = cv2.VideoCapture(videoPath)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        yield frame


def processVideoFolder(folderPath=Path.rawVideos, marksPath=Path.rawJson, framesPath=Path.frames, overwrite=False,
                       extension=Extensions.png, params=None):
    videos = [video for video in os.listdir(folderPath) if video.endswith(Extensions.mov)]

    actualInfo = downloadActualInfo()

    globalIdx = 0
    for video in videos:
        filePath = os.path.join(folderPath, video)

        category = extractCategory(video)
        globalIdx = actualInfo.get(category, {}).get(const.original, {}).get(const.overall, globalIdx)

        print(f"\n{Fore.GREEN} Video {filePath} is being processed {Style.RESET_ALL}")
        frameVideo(
            filePath=filePath,
            marksPath=marksPath,
            datasetPath=framesPath,
            actualInfo=actualInfo,
            overwrite=overwrite,
            extension=extension,
            params=params
        )

    actualizeInfoWithFrames(framesPath)


def main():
    pass


if __name__ == "__main__":
    main()