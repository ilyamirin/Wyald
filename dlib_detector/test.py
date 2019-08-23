import os
import sys
import glob

import numpy as np
import cv2
import dlib
import json

ddir = "./detector"

def processFile(videoSource, videoDir, coinDir, detector):

    res = {}
    cap = cv2.VideoCapture(os.path.join(videoDir, videoSource))
    idx = 0

    counter = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        counter += 1
        if counter % 3 == 0:
            continue
        fname = f"{videoSource[:-4]}-{idx}.png"
        print(f"Processing file: {fname}")

        dets = detector(frame)
        if dets == 0:
            continue
        # print(f"Number of coins detected: {len(dets)}")
        imgData = {}
        for k, d in enumerate(dets):
            imgData["category"] = videoSource[:-7]
            imgData["coords"] = [d.top(), d.left(), d.bottom(), d.right()]
            cv2.imwrite(os.path.join(path, fname), frame)

        if imgData != {}:
            res[os.path.join(coinDir, fname)] = imgData
        idx += 1

    return res


def main():
    rootDir = r"D:\Projects\coins-project\data"
    rublesDir = os.path.join(rootDir, 'rubles')
    frameDir = os.path.join(rootDir, 'frames')
    videoDir = os.path.join(rublesDir, 'video')

    for coinCategoryName in os.listdir(videoDir):
        detectorPath = os.path.join(ddir, f"detector_{coinCategoryName[:-4]}.svm")
        if not os.path.exists(detectorPath):
            continue

        coinDir = f"{os.path.join(frameDir, coinCategoryName[:-4])}"  # cut 4 ends symbols '.MOV'
        if not os.path.exists(coinDir):
            os.makedirs(coinDir)

        coinDetector = dlib.simple_object_detector(detectorPath)
        jsonData = processFile(coinCategoryName, os.path.join(videoDir), coinDir, coinDetector)


        with open(os.path.join(originDir, "mark.json"), "w") as fout:
            json.dump(jsonData, fout, indent=3)


if __name__ == "__main__":
    main()