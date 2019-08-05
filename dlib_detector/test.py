import os
import sys
import glob

import numpy as np
import cv2
import dlib
import json

ddir = "./detector"

def processFile(category, path, detector):
    res = {}
    for f in glob.glob(os.path.join(path, "*.png")):
        img = cv2.imread(f)
        print(f"Processing file: {f}")
        dets = detector(img)
        if dets == 0:
            continue
        print(f"Number of coins detected: {len(dets)}")
        imgData = {}
        for k, d in enumerate(dets):
            print(f"Detection {k}: Left: {d.left()} Top: {d.top()} Right: {d.right()} Bottom: {d.bottom()}")
            cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (0, 128, 255))
            imgData["category"] = category
            imgData["coords"] = [ d.top(), d.left(), d.bottom(), d.right()]
        if imgData == {}:
            res[f] = imgData
        cv2.imshow("Output", img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    return res


def main():
    fpath = r"C:\Projects\data\coins\frames"
    accordanceDict = dict()

    for coinCategoryName in os.listdir(fpath):
        for i in range(1, 4):
            path = f"{os.path.join(fpath, coinCategoryName, str(i))}"
            coinDetector = dlib.simple_object_detector(os.path.join(ddir, f"detector_{coinCategoryName}_{i}.svm"))

            jsonData = processFile(coinCategoryName, path, coinDetector)
            dstDir = os.path.exists(os.path.join(path, "mark.json"))

            if os.path.exists(dstDir) is False:
                os.mkdir(dstDir)

            with open(os.path.join(path, "mark.json"), "w") as fout:
                json.dump(jsonData, fout)


if __name__ == "__main__":
    main()