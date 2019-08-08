import os
import sys
import glob

import numpy as np
import cv2
import dlib
import json

ddir = "./detector_v2"

def processFile(videoSource, vpath, path, detector):

    res = {}
    cap = cv2.VideoCapture(os.path.join(vpath, videoSource))
    idx = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        fname = f"{videoSource[:-4]}_{idx}.png"
        print(f"Processing file: {fname}")

        dets = detector(frame)
        if dets == 0:
            continue
        print(f"Number of coins detected: {len(dets)}")
        imgData = {}
        for k, d in enumerate(dets):
            print(f"Detection {k}: Left: {d.left()} Top: {d.top()} Right: {d.right()} Bottom: {d.bottom()}")
            cv2.rectangle(frame, (d.left(), d.top()), (d.right(), d.bottom()), (0, 128, 255))
            imgData["category"] = videoSource[:-7]
            imgData["coords"] = [d.top(), d.left(), d.bottom(), d.right()]
            #cv2.imwrite(os.path.join(path, fname), frame)

        if imgData != {}:
            res[os.path.join(path, fname)] = imgData
        cv2.imshow("Output", frame)
        if cv2.waitKey(10) & 0xFF == ord('q'):
             break
        idx += 1

    return res


def main():
    fpath = r"C:\Projects\coins\data\coins"
    accordanceDict = dict()


    for coinCategoryName in os.listdir(os.path.join(fpath, "raw_videos")):
        t = coinCategoryName[:-7]
        # if t == "1-ruble-avers" or t == "10-rubles-avers": continue
        # if t == "2-rubles-avers":
        #     if coinCategoryName[:-4] != "2-rubles-avers-v6":
        #         continue
        path = f"{os.path.join(fpath, 'frames', 'imgs', coinCategoryName[:-4])}"
        if not os.path.exists(path):
            os.makedirs(path)

        coinDetector = dlib.simple_object_detector(os.path.join(ddir, f"detector_{coinCategoryName[:-4]}.svm"))
        vpath = os.path.join(fpath, "raw_videos")
        jsonData = processFile(coinCategoryName, vpath, path, coinDetector)
        dstDir = os.path.exists(os.path.join(path, "mark.json"))

        return
        if os.path.exists(dstDir) is False:
            os.mkdir(dstDir)

        with open(os.path.join(path, "mark.json"), "w") as fout:
            json.dump(jsonData, fout)


if __name__ == "__main__":
    main()