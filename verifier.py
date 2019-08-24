"""
    ---------------------------------------------------------
    Project data structure:
    ---------------------------------------------------------
        darknet_data/
            original/
                coin1/
                    avers*/
                        frames/
                            image1.png
                            image1.txt
                            ...
                            imageM.png
                            imageM.txt
                        marks.json
                    revers*/
                        ...
                    merged*/
                        ...
                    ...
                coinN/
                    ...
            augmented/
            ...
        raw_data/
            videos/
                coin1_X.MOV
                ...
                coinN_X.MOV
            jsons/
                coin1_X.json
                ...
                coinN_X.json
            xml/
                coin1_X.xml
                ...
                coinN_X.xml
        sets/
            train.txt
            valid.txt
            test.txt
        actual_info.json
        processed_files.txt
        categories.txt
    ---------------------------------------------------------
    marks.json structure:
    ---------------------------------------------------------
    {
        full_frame_name:{
            "image": full_frame_name + image_ext,
            "coords": [y1, x1, y2, x2],
            "fullCategory": category_subcategory,
            "ctgIdx": {0..N},
            "imageShape": (h, w)
            }
        ...
    }
    ---------------------------------------------------------
    actual_info.json structure:
    ---------------------------------------------------------
    {
        "original": {
            "coin1": {
                "avers"*: x1,
                "revers"*: y1,
                "merged": z1
                "overall": x1 + y1 + z1
            },
            ...
            "coinN": {...}
        },
        "augmented": {
            "coin1": {
                "avers"*: x2,
                "revers"*: y2,
                "merged": z2,
                "overall": x1 + y1 + z1
            },
            ...
            "coinN": {...}
        }
    }
    ---------------------------------------------------------
    Full frame names:
    ---------------------------------------------------------
        category_subcategory-frame_ID-{origin}
    ---------------------------------------------------------
    Image extensions:
    ---------------------------------------------------------
    .png
    .jpg
    .jpeg
    ---------------------------------------------------------
    * - optional
    {origin} - original or {augmented, hsv, bgr, ...}
    """

import os
import json

from colorama import Fore, Style

from utils import makeJSONname, makeMOVname, extractBasename, walk, putNested, updateNested, matchLists
from config import Extensions, Path, Constants as const


def downloadActualInfo():
    try:
        actualInfo = json.load(open(Path.actualInfo, "r"))
    except:
        actualInfo = {}

    return actualInfo

def matchVideosToMarks(marks, videos):
    marks = os.listdir(marks) if not isinstance(marks, list) else marks
    videos = os.listdir(videos) if not isinstance(videos, list) else videos

    transformer = lambda x: makeJSONname(extractBasename(x))

    return matchLists(master=marks, slave=videos, transformer=transformer, showMessages=True)


def matchMarksToVideos(marks, videos):
    marks = os.listdir(marks) if not isinstance(marks, list) else marks
    videos = os.listdir(videos) if not isinstance(videos, list) else videos

    transformer = lambda x: makeMOVname(extractBasename(x))

    return matchLists(master=videos, slave=marks, transformer=transformer, showMessages=True)


def crossMatchVideoAndMarks(marks, videos):
    marks = os.listdir(marks) if not isinstance(marks, list) else marks
    videos = os.listdir(videos) if not isinstance(videos, list) else videos

    videos = matchVideosToMarks(marks, videos)
    marks = matchMarksToVideos(marks, videos)

    return videos, marks


def actualizeInfoWithFrames(datasetPath):
    actualInfo = {}
    os.makedirs(os.path.dirname(Path.actualInfo), exist_ok=True)

    frames = walk(datasetPath, targetDirs=const.frames)
    frames = frames.get("dirs")

    for idx, dirsList in enumerate(frames):
        dirsList = dirsList[:-1]

        fullpath = os.path.join([datasetPath] + dirsList)
        images = walk(fullpath, targetExtensions=Extensions.images).get("extensions")

        putNested(actualInfo, dirsList, len(images))
        dirsList[-1] = const.overall
        updateNested(actualInfo, dirsList, len(images))

        print("\r{:.1f}% of work has been done".format(idx + 1 / len(frames) * 100), end="")

    json.dump(actualInfo, open(Path.actualInfo, "w"), indent=3)


def actualizeInfoWithJsons(datasetPath):
    actualInfo = {}
    os.makedirs(os.path.dirname(Path.actualInfo), exist_ok=True)

    frames = walk(datasetPath, targetDirs=const.frames)
    frames = frames.get("dirs")

    for idx, dirsList in enumerate(frames):
        dirsList = dirsList[:-1]

        fullpath = os.path.join([datasetPath] + dirsList + [makeJSONname(const.marks)])
        marks = json.load(open(fullpath, "r"))

        putNested(actualInfo, dirsList, len(marks))
        dirsList[-1] = const.overall
        updateNested(actualInfo, dirsList, len(marks))

        print("\r{:.1f}% of work has been done".format(idx + 1 / len(frames) * 100), end="")

    json.dump(actualInfo, open(Path.actualInfo, "w"), indent=3)


def main():
    pass


if __name__ == "__main__":
    main()