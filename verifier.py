"""
    ---------------------------------------------------------
    Project data structure:
    ---------------------------------------------------------
        frames/
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
                coin2/
                    ...
                coinN/
                    frames/
                        image1.png
                        image1.txt
                        ...
                        imageM.png
                        imageM.txt
                    marks.json
            augmented/
            ...
        jsons/
            coin1.json
            ...
            coinN.json
        actual_info.json
        categories.txt
        train.txt
        valid.txt
        test.txt
    ---------------------------------------------------------
    marks.json structure:
    ---------------------------------------------------------
    {
        "frame_1":{
            "fullCategory": {ctg}_{subctg},
            "coords": [y1, x1, y2, x2]
            }
        ...
    }
    ---------------------------------------------------------
    actualize_info.json structure:
    ---------------------------------------------------------
    {
        "coin1": {
            "original": {
                "overall": l0 (= x0 + y0),
                "avers"*: x0,
                "revers"*: y0
                },
            "augmented": {
                "overall": l1 (= x1 + y1),
                "avers"*: x1,
                "revers"*: y1
                },
            "overall": l2 (= l0 + l1)
            },
            ...
    }
    ---------------------------------------------------------
    * - optional
    """

import os
import argparse
import json

from colorama import Fore, Style

from utils import makeJSONname, makeMOVname, extractBasename, walk, putNested
from config import Extensions


def matchVideosToMarks(marks, videos):
    marks = os.listdir(marks) if not isinstance(marks, list) else marks
    videos = os.listdir(videos) if not isinstance(videos, list) else videos

    for name in videos[::-1]:
        if makeJSONname(extractBasename(name)) not in marks:
            print(f"{Fore.RED} No matched json for {name} {Style.RESET_ALL}")

            videos.remove(name)

    return videos


def matchMarksToVideos(marks, videos):
    marks = os.listdir(marks) if not isinstance(marks, list) else marks
    videos = os.listdir(videos) if not isinstance(videos, list) else videos

    for name in marks[::-1]:
        if makeMOVname(extractBasename(name)) not in videos:
            print(f"{Fore.RED} No matched video for {name} {Style.RESET_ALL}")

            videos.remove(name)

    return marks


def crossMatchVideoAndMarks(marks, videos):
    marks = os.listdir(marks) if not isinstance(marks, list) else marks
    videos = os.listdir(videos) if not isinstance(videos, list) else videos

    videos = matchVideosToMarks(marks, videos)
    marks = matchMarksToVideos(marks, videos)

    return videos, marks


def actualizeInfoWithFrames(framesPath, actualInfoPath=None):
    actualInfo = {}
    if actualInfoPath is not None:
        actualInfo = json.load(open(actualInfoPath, "r"))

    frames = walk(framesPath, targetDir="frames")
    frames = frames.get("dirs")

    for idx, framesDir in enumerate(frames):
        framesDir = framesDir[:-1]

        fullpath = os.path.join([framesPath] + framesDir)
        images = walk(fullpath, targetExtensions=Extensions.images).get("extensions")

        putNested(actualInfo, framesDir, len(images))
        print("\r{:.1f}% of work has been done".format(idx + 1 / len(frames) * 100), end="")


def actualizeInfoWithJsons(framesPath, actualInfoPath=None):
    actualInfo = {}
    if actualInfoPath is not None:
        actualInfo = json.load(open(actualInfoPath, "r"))

    frames = walk(framesPath, targetDir="frames")
    frames = frames.get("dirs")

    for idx, framesDir in enumerate(frames):
        framesDir[-1] = "marks.json"

        fullpath = os.path.join([framesPath] + framesDir)
        marks = json.load(open(fullpath, "r"))

        putNested(actualInfo, framesDir[:-1], len(marks))
        print("\r{:.1f}% of work has been done".format(idx + 1 / len(frames) * 100), end="")


def check():
    pass


def main():
    walk(r"D:\Projects\coins-project\data\sber", targetDir="xml", targetExtensions=".MOV")


if __name__ == "__main__":
    main()