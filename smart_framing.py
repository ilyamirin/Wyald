import os
import json
import multiprocessing as mp

import cv2

from math import ceil
from colorama import Fore, Style

from verifier import getFullCategory, fitCoords
from utils import makeJSONname, openJsonSafely, extendName
from config import Extensions, Path, Constants as const



def createGenerator(videosPath, videosInfo, overall, limit):
    pointer = 0
    step = ceil(overall / limit)
    offsets = [i for i in range(step)]

    for offset in offsets:
        for video, videoMarks in videosInfo.items():
            cap = cv2.VideoCapture(os.path.join(videosPath, video))

            frameIdx = 0
            while cap.isOpened():
                pointer += offset

                if pointer == limit:
                    break
                if pointer % step != 0:
                    continue

                ret, frame = cap.read()
                if not ret:
                    break

                frameName = f"frame_{frameIdx}"
                coords = videoMarks[frameName]

                globalFrameName = f"frame_{pointer}"

                pointer += 1
                frameIdx += 1
                yield frame, globalFrameName, coords


def augment():
    pass


def extract(ctg, ctgInfo, videosPath:Path.rawVideos, extractionPath=Path.original, extension=Extensions.jpg, limit=None,
            augmentFunc=None, augmentations=None, augmentationName=const.augmented, augmentationPath=None):

    parent = ctgInfo.get(const.parent, "")
    fullExtractionPath = os.path.join(extractionPath, parent, ctg)
    os.makedirs(os.path.join(fullExtractionPath, const.frames), exist_ok=True)

    videos = ctgInfo[const.videos]

    overall = ctgInfo[const.overall]

    limit = limit if limit is not None else overall

    if augmentFunc is not None:
        augmentations = int(augmentations) if augmentations is not None else min(limit, overall)
        augmentations = max(augmentations, augmentations + limit - overall)

        augRepeats = ceil(augmentations / min(limit, overall))

        augmentationPath = augmentationPath if augmentationPath is not None \
            else extractionPath.replace(const.original, augmentationName)

        fullAugmentationPath = os.path.join(augmentationPath, parent, ctg)
        os.makedirs(os.path.join(fullAugmentationPath, const.frames), exist_ok=True)

        augMarks = {}
        totalAugs = 0

    generator = createGenerator(videosPath, videos, overall, limit)

    marks = {}
    total = 0
    for idx, genInfo in enumerate(generator):
        frame, frameName, coords = genInfo

        fullCategory = getFullCategory(parent, ctg)
        fullFrameName = const.separator.join((fullCategory, frameName, const.original))

        coords = fitCoords(coords, frame.shape[:2])

        frameMarks = {
            const.image: extendName(fullFrameName, extension),
            const.coords: coords,
            const.fullCategory: fullCategory,
            const.ctgIdx: ctgInfo[const.ctgIdx],
            const.imageShape: frame.shape[:2]
        }

        cv2.imwrite(os.path.join(fullExtractionPath, const.frames, extendName(fullFrameName, extension)), frame)
        marks[frameName] = frameMarks

        total += 1

        if augmentFunc is not None:
            frameAugments = 0
            for i in range(augRepeats):
                if totalAugs == augmentations:
                    break

                augFrame, augCoords = augmentFunc(frame, coords)
                augFrameName = f"{fullCategory}{const.separator}{frameName}_{i}{const.separator}{augmentationName}"

                augFrameMarks = {
                    const.image: extendName(augFrameName, extension),
                    const.coords: fitCoords(augCoords, augFrame.shape[:2]),
                    const.fullCategory: fullCategory,
                    const.ctgIdx: ctgInfo[const.ctgIdx],
                    const.imageShape: augFrame.shape[:2]
                }

                cv2.imwrite(os.path.join(fullAugmentationPath, const.frames, extendName(augFrameName, extension)),
                            augFrame)

                augMarks[augFrameName] = augFrameMarks

                frameAugments += 1
            totalAugs += frameAugments

        print("\rFrame #{} has been added with {}".format(idx, frameAugments), end="")

    json.dump(marks, os.path.join(fullExtractionPath, makeJSONname(const.marks)), indent=3)
    print(f"{Fore.GREEN}Added marks to {fullExtractionPath} {Style.RESET_ALL}")

    if augmentFunc is not None:
        json.dump(augMarks, os.path.join(fullAugmentationPath, makeJSONname(const.marks)), indent=3)
        print(f"{Fore.GREEN}Added marks to {fullAugmentationPath} {Style.RESET_ALL}")

    print(f"{Fore.GREEN}Added {total} pure frames and {totalAugs} augmentede frames in total {Style.RESET_ALL}")


def extractCategories(videosPath:Path.rawVideos, summarizedPath, categoriesList, extractionPath=Path.original, subcategories=None):
    subcategories = {} if subcategories is None else subcategories

    summarized = openJsonSafely(summarizedPath)

    for category, categoryInfo in categoriesList.items():
        curSubcategories = subcategories.get(category, list(categoryInfo.keys()))

        for subctg in curSubcategories:
            subctgInfo = categoryInfo.get(subctg, {})
            extract(subctg, subctgInfo, videosPath, extractionPath)


def main():
    pass


if __name__ == "__main__":
    main()