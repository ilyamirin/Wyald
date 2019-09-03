import os
import uuid
import json

import cv2

from utils import walk, makeJSONname, openJsonSafely
from config import Extensions, Constants as const
from framing import generateFrames


def prepareVideo(rpath, wpath):
    videos = walk(rpath, targetExtensions=Extensions.videos()).get("extensions")

    for vset in videos:
        vpath = os.path.join(rpath, *vset)

        for frame in generateFrames(vpath):
            cv2.imwrite(os.path.join(wpath, "negative-{}{}".format(uuid.uuid1(), Extensions.jpg)), frame)


def prepareImages(rpath, wpath):
    images = walk(rpath, targetExtensions=Extensions.images()).get("extensions")

    for iset in images:
        ipath = os.path.join(rpath, *iset)
        os.rename(ipath, os.path.join(wpath, "negative-{}{}".format(uuid.uuid1(), Extensions.jpg)))


def makeNegativesMarks(rpath):
    negatives = os.listdir(os.path.join(rpath, const.frames))
    marks = {}

    for nimage in negatives:
        marks[nimage] = {
            const.coords: [0, 0, 0, 0],
            const.ctgIdx: 0,
            const.imageShape: [1, 1],
            const.image: nimage
        }

    json.dump(marks, open(os.path.join(rpath, makeJSONname(const.marks)), "w"), indent=3)


def main():
    # prepareImages(
    #     rpath=r"E:\negatives",
    #     wpath=r"E:\pretty_coins\negatives\frames"
    # )
    #
    # prepareVideo(
    #     rpath=r"E:\negatives",
    #     wpath=r"E:\pretty_coins\negatives\frames"
    # )

    makeNegativesMarks(r"E:\pretty_coins\negatives")


if __name__ == "__main__":
    main()