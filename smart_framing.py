import os
import json
import multiprocessing as mp

import cv2

from time import sleep
from math import ceil
from colorama import Fore, Style

from verifier import getFullCategory, fitCoords
from utils import makeJSONname, openJsonSafely, extendName
from config import Extensions, Path, Sets, Constants as const


def createGenerator(videosPath, videosInfo, overall, limit):
    counter = 0

    step = ceil(overall / limit)
    offsets = [i for i in range(step)]

    for offset in offsets:
        globalIdx = 0
        for video, videoMarks in videosInfo.items():
            cap = cv2.VideoCapture(os.path.join(videosPath, video))

            frameIdx = 0
            while cap.isOpened():
                ret = cap.grab()
                if not ret:
                    break

                if counter == limit:
                    break
                if (frameIdx + offset) % step != 0:
                    globalIdx += 1
                    frameIdx += 1
                    continue

                frameName = f"frame_{frameIdx}"
                if frameName not in videoMarks:
                    globalIdx += 1
                    frameIdx += 1
                    continue

                ret, frame = cap.retrieve()

                coords = videoMarks[frameName]

                globalFrameName = f"frame_{globalIdx}"

                counter += 1
                globalIdx += 1
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


def updateMarks(oldMarks, newMarks, overwrite=False):
    for key, value in newMarks.items():
        if key not in oldMarks or (key in oldMarks and overwrite):
            oldMarks[key] = value
        else:
            continue

    return oldMarks


def extract(ctg, ctgInfo, videosPath=Path.rawVideos, extractionPath=Path.original, extension=Extensions.jpg, limit=None,
            augmentFunc=None, augmentations=None, augmentationName=const.augmented, augmentationPath=None,
            overwriteOriginal=False, overwriteAugmented=True):

    try:
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

            existingAugs = len(os.listdir(os.path.join(fullAugmentationPath, const.frames)))

            augMarks = {}
            totalAugs = 0

        fullCategory = getFullCategory(parent, ctg)

        print("Cutting videos: {:>50} \t expected orig frames {:>10} \t expected aug frames \t {:>10} process id: {:>10}".
              format(fullCategory, min(limit, overall), augmentations, os.getpid()))
        sleep(0.5)

        # time.sleep(0.5)

        generator = createGenerator(videosPath, videos, overall, limit)

        marks = {}
        total = 0
        for idx, genInfo in enumerate(generator):
            frame, frameName, coords = genInfo

            fullFrameName = const.separator.join((fullCategory, frameName, const.original))
            framePath = os.path.join(fullExtractionPath, const.frames, extendName(fullFrameName, extension))

            coords = fitCoords(coords, frame.shape[:2])

            status = "passed"
            if not os.path.exists(framePath) or overwriteOriginal:
                status = "added"
                frameMarks = {
                    const.fullCategory: fullCategory,
                    const.ctgIdx: ctgInfo[const.ctgIdx],
                    const.image: extendName(fullFrameName, extension),
                    const.coords: coords,
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

                    if totalAugs >= augmentations or (existingAugs >= augmentations and not overwriteAugmented):
                        break

                    if os.path.exists(augFramePath) and not overwriteAugmented:
                        continue

                    augFrame, augCoords = augmentFunc(frame, coords)

                    augFrameMarks = {
                        const.fullCategory: fullCategory,
                        const.image: extendName(augFrameName, extension),
                        const.ctgIdx: ctgInfo[const.ctgIdx],
                        const.coords: fitCoords(augCoords, augFrame.shape[:2]),
                        const.imageShape: augFrame.shape[:2]
                    }

                    cv2.imwrite(augFramePath, augFrame)

                    augMarks[augFrameName] = augFrameMarks

                    frameAugments += 1
                totalAugs += frameAugments

            print("\rFrame #{} has been {} with {} augmentations".format(idx + 1, status, frameAugments), end="")

        marksPath = os.path.join(fullExtractionPath, makeJSONname(const.marks))
        oldMarks = openJsonSafely(marksPath)
        json.dump(updateMarks(oldMarks, marks, overwriteOriginal), open(marksPath, "w"), indent=3, sort_keys=True)
        print(f"\n{Fore.GREEN}Added marks to {fullExtractionPath} {Style.RESET_ALL}")

        if augmentFunc is not None:
            augMarksPath = os.path.join(fullAugmentationPath, makeJSONname(const.marks))
            oldAugMarks = openJsonSafely(augMarksPath)
            json.dump(updateMarks(oldAugMarks, augMarks, overwriteAugmented), open(augMarksPath, "w"), indent=3,
                      sort_keys=True)
            print(f"{Fore.GREEN}Added marks to {fullAugmentationPath} {Style.RESET_ALL}")

        print(f"{Fore.GREEN}Added {total} pure frames and {totalAugs} augmented frames in total {Style.RESET_ALL}")

    except Exception as e:
        print(e)


def extractCategories(videosPath=Path.rawVideos, summarizedPath=Path.summarizedRaw, categoriesList=None,
                      extractionPath=Path.original, subcategories=None, framesLimit=None,
                      augmentationsLimit=None, augmentationFunc=None, augmentationName="augmented",
                      augmentationPath=None,
                      parallel=True, threads=8, overwriteOriginal=False, overwriteAugmented=False):

    summarized = openJsonSafely(summarizedPath)

    categoriesList = list(summarized.keys()) if categoriesList is None else categoriesList
    categoriesList.remove(const.maxIdx)

    if parallel:
        threads = min(threads, mp.cpu_count())
    else:
        threads = 1

    threadsList = []
    with mp.Pool(threads) as pool:
        for category in categoriesList:
            categoryInfo = summarized[category]

            neededSubcategories = list(categoryInfo.keys())
            if subcategories is not None:
                if isinstance(subcategories, list):
                    neededSubcategories = subcategories
                elif isinstance(subcategories, dict):
                    neededSubcategories = subcategories.get(category, neededSubcategories)
                else:
                    raise TypeError

            for subctg in neededSubcategories:
                if subctg not in categoryInfo:
                    continue

                subctgInfo = categoryInfo[subctg]

                # extract(
                #     subctg,
                #     subctgInfo,
                #     videosPath=Path.rawVideos,
                #     extractionPath=Path.original,
                #     limit=framesLimit,
                #     augmentations=augmentationsLimit,
                #     augmentFunc=augmentationFunc,
                #     augmentationName=augmentationName,
                #     augmentationPath=augmentationPath,
                #     overwriteOriginal=overwriteOriginal,
                #     overwriteAugmented=overwriteAugmented
                # )

                threadsList.append(
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
                )

        for r in threadsList:
            r.get()


def main():
    extractCategories(
        videosPath=Path.rawVideos,
        summarizedPath=Path.summarizedRaw,
        categoriesList=None,
        subcategories=Sets.subcategories,
        extractionPath=Path.original,
        framesLimit=2000,
        augmentationsLimit=2000,
        augmentationFunc=const.default,
        augmentationName="augmented",
        augmentationPath=None,
        parallel=True, threads=8,
        overwriteOriginal=False,
        overwriteAugmented=False
    )


if __name__ == "__main__":
    main()