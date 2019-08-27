import os
import json

import cv2

from colorama import Fore, Style

from verifier import actualizeInfoWithFrames, downloadActualInfo, getFullCategory, fitCoords
from utils import makeJSONname, openJsonSafely, extractBasename, extendName, readLines, writeLines, getNested, updateNested, putNested
from config import Extensions, Path, Constants as const


def frameVideo(filePath, marksPath, datasetPath, actualInfo, overwrite=False, extension=Extensions.png, params=None):
    categories = readLines(Path.categories)
    basename = extractBasename(filePath)

    try:
        jsonName = makeJSONname(basename)
        marks = json.load(open(os.path.join(marksPath, jsonName), "r"))
    except:
        print(f"{Fore.RED}There is no json file {marksPath} for {filePath} {Style.RESET_ALL}")
        return

    framesGenerator = generateFrames(filePath)

    marksSeparated = {}
    total = 0
    for idx, frame in enumerate(framesGenerator):
        # if idx == 20:
        #     break
        frameID = f"frame_{idx}"
        if frameID not in marks:
            continue
        else:
            frameMarks = marks[frameID]

        category = frameMarks[const.category]
        subcategory = frameMarks[const.subcategory]

        countKeys = [const.original, category, subcategory]
        if idx == 0:
            globalIdx = getNested(dictionary=actualInfo, keys=countKeys, default=0)

        frameID = f"frame_{idx + globalIdx}"
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


def generateFrames(videoPath):
    cap = cv2.VideoCapture(videoPath)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        yield frame


def processVideoFolder(folderPath=Path.rawVideos, marksPath=Path.rawJson, datasetPath=Path.dataset, overwrite=False,
                       extension=Extensions.png, params=None):

    processedVideos = readLines(Path.processedFiles)
    videos = [video for video in os.listdir(folderPath) if video not in processedVideos and
              (video.endswith(Extensions.mov) or video.endswith(Extensions.mp4))]

    actualInfo = downloadActualInfo()

    for video in videos:
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

    writeLines(processedVideos, Path.processedFiles)
    actualizeInfoWithFrames(Path.dataset)


def main():
    pass


if __name__ == "__main__":
    main()