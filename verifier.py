"""
    ---------------------------------------------------------
    Project data structure:
    ---------------------------------------------------------
        videos/
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

from colorama import Fore, Style

from config import Extensions


def extractBasename(filepath):
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)

    return name


def extractCategory(filepath):
    name = extractBasename(filepath)
    category = name.split("-")[0]

    return category, name


def makeJSONname(basename):
    return basename + Extensions.json


def makeMOVname(basename):
    return basename + Extensions.mov


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


def actualizeInfoWithFrames(filePath=None):
    pass


def actualizeInfoWithJsons():
    pass


def check():
    pass


def main():
    pass


if __name__ == "__main__":
    main()