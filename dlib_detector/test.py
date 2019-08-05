import os
import sys
import glob

import numpy as np
import cv2
import dlib


ddir = "./detector"

def processFile(path, detector):
    for f in glob.glob(os.path.join(path, "*.png")):
        img = cv2.imread(f)
        print(f"Processing file: {f}")
        dets = detector(img)
        print(f"Number of coins detected: {len(dets)}")
        for k, d in enumerate(dets):
            print(f"Detection {k}: Left: {d.left()} Top: {d.top()} Right: {d.right()} Bottom: {d.bottom()}")
            cv2.rectangle(img, (d.left(), d.top()), (d.right(), d.bottom()), (0, 128, 255))

        cv2.imshow("Output", img)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break


def main():
    fpath = r"C:\Projects\data\coins\frames"
    accordanceDict = dict()

    for coinClassName in os.listdir(fpath):
        for i in range(1, 4):
            accordanceDict[f"{os.path.join(fpath, coinClassName, str(i))}"] = dlib.simple_object_detector(
                os.path.join(ddir, f"detector_{coinClassName}_{i}.svm"))

    for path, detector in accordanceDict.items():
        processFile(path, detector)


if __name__ == "__main__":
    main()