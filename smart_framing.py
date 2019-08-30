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


def proxifyAugmentFunc(func):
    if func == const.default:
        from augmentations_kit import customAugmentations

        return customAugmentations

    elif callable(func):
        return func
    else:
        raise RuntimeError


def extract(ctg, ctgInfo, videosPath=Path.rawVideos, extractionPath=Path.original, extension=Extensions.jpg, limit=None,
            augmentFunc=None, augmentations=None, augmentationName=const.augmented, augmentationPath=None,
            overwriteOriginal=False, overwriteAugmented=True):

    parent = ctgInfo.get(const.parent, "")
    fullExtractionPath = os.path.join(extractionPath, parent, ctg)
    os.makedirs(os.path.join(fullExtractionPath, const.frames), exist_ok=True)

    videos = ctgInfo[const.videos]

    overall = ctgInfo[const.overall]

    limit = limit if limit is not None else overall

    if augmentFunc is not None:
        augmentFunc = proxifyAugmentFunc(augmentFunc)

        augmentations = int(augmentations) if augmentations is not None else min(limit, overall)
        augmentations = max(augmentations, augmentations + limit - overall)

        augRepeats = ceil(augmentations / min(limit, overall))

        augmentationPath = augmentationPath if augmentationPath is not None \
            else extractionPath.replace(const.original, augmentationName)

        fullAugmentationPath = os.path.join(augmentationPath, parent, ctg)
        os.makedirs(os.path.join(fullAugmentationPath, const.frames), exist_ok=True)

        augMarks = {}
        totalAugs = 0

    fullCategory = getFullCategory(parent, ctg)
    print("Cutting videos: \t {:>50} \t expected orig frames {:>10} \t expected aug frames {:>10} process id: {:>10}".
          format(fullCategory, min(limit, overall), augmentations, os.getpid()))

    # time.sleep(0.5)

    generator = createGenerator(videosPath, videos, overall, limit)

    marks = {}
    total = 0
    for idx, genInfo in enumerate(generator):
        frame, frameName, coords = genInfo

        fullFrameName = const.separator.join((fullCategory, frameName, const.original))
        framePath = os.path.join(fullExtractionPath, const.frames, extendName(fullFrameName, extension))

        coords = fitCoords(coords, frame.shape[:2])

        if not os.path.exists(framePath) or overwriteOriginal:
            frameMarks = {
                const.image: extendName(fullFrameName, extension),
                const.coords: coords,
                const.fullCategory: fullCategory,
                const.ctgIdx: ctgInfo[const.ctgIdx],
                const.imageShape: frame.shape[:2]
            }

            cv2.imwrite(framePath, frame)
            marks[frameName] = frameMarks

            total += 1

        if augmentFunc is not None:
            frameAugments = 0
            for i in range(augRepeats):
                augFrameName = f"{fullCategory}{const.separator}{frameName}_{i}{const.separator}{augmentationName}"
                augFramePath = os.path.join(fullAugmentationPath, const.frames, extendName(augFrameName, extension))

                if totalAugs == augmentations:
                    break

                if os.path.exists(augFramePath) or not overwriteAugmented:
                    continue

                augFrame, augCoords = augmentFunc(frame, coords)

                augFrameMarks = {
                    const.image: extendName(augFrameName, extension),
                    const.coords: fitCoords(augCoords, augFrame.shape[:2]),
                    const.fullCategory: fullCategory,
                    const.ctgIdx: ctgInfo[const.ctgIdx],
                    const.imageShape: augFrame.shape[:2]
                }

                cv2.imwrite(augFramePath, augFrame)

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


def extractCategories(videosPath=Path.rawVideos, summarizedPath=Path.summarizedRaw, categoriesList=None,
                      framesLimit=None,
                      augmentationsLimit=None, augmentationFunc=None, augmentationName="augmented",
                      augmentationPath=None,
                      extractionPath=Path.original, subcategories=None, parallel=True, threads=8,
                      overwriteOriginal=False, overwriteAugmented=False):

    summarized = openJsonSafely(summarizedPath)

    subcategories = {} if subcategories is None else subcategories
    categoriesList = list(summarized.keys()) if categoriesList is None else categoriesList

    if parallel:
        threads = min(threads, mp.cpu_count())
    else:
        threads = 1

    with mp.Pool(threads) as pool:
        for category in categoriesList:
            categoryInfo = summarized[category]
            curSubcategories = subcategories.get(category, list(categoryInfo.keys()))

            for subctg in curSubcategories:
                subctgInfo = categoryInfo.get(subctg, {})

                pool.apply_async(
                    extract,
                    args=(subctg, subctgInfo),
                    kwds={
                        "videosPath": videosPath,
                        "extractionPath": extractionPath,
                        "extension": Extensions.jpg,
                        "limit": framesLimit,
                        "augmentFunc": augmentationFunc,
                        "augmentations": augmentationsLimit,
                        "augmentationName": augmentationName,
                        "augmentationPath": augmentationPath,
                        "overwriteOriginal": overwriteOriginal,
                        "overwriteAugmented": overwriteAugmented
                    }
                )


def main():
    pass


if __name__ == "__main__":
    main()