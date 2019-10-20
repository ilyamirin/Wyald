import shutil
import os
import json

import cv2
import numpy as np
from config import Path, Extensions
from random import shuffle, seed
from Annotator import Annotation

catIdx = {}
jData = {}
categoriesCount = 80

def createTxtFile(img, frameData, framesDir, frame_idx):
    category = frameData["category"]
    ih, iw, c = img.shape

    y1, x1, y2, x2 = frameData["coordinates"]

    xc = (x2 + x1) * 0.5 / iw
    yc = (y2 + y1) * 0.5 / ih

    w = (x2 - x1) / iw
    h = (y2 - y1) / ih

    with open(os.path.join(framesDir, "frame_{:06d}.txt".format(frame_idx)), "w") as txtFile:
        txtFile.write(f"{catIdx[category]['idx']} {xc} {yc} {w} {h}")


def rewriteTxtFiles(txtDir, local_frame_idx, frame_idx, framesDir):
    if not os.path.exists(os.path.join(txtDir, "frame_{:06d}.txt".format(local_frame_idx))):
        return False
    txtFile = open(os.path.join(txtDir, "frame_{:06d}.txt".format(local_frame_idx)), "r")
    dstTxtFile = open(os.path.join(framesDir, "frame_{:06d}.txt".format(frame_idx)), "a")

    for line in txtFile.readlines():
        nums  = line.split(" ")
        if int(nums[0]) < categoriesCount:
            dstTxtFile.write(line)
    return True


def framingVideo(typeAnnotation, video, framesDir, frame_idx = 0):

    cap = cv2.VideoCapture(video)
    localFrame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        print("\rFrame #{}".format(frame_idx), end="")
        if typeAnnotation == Annotation.json:
            videoName = os.path.basename(video)
            if f"frame_{localFrame_idx}" in jData[videoName]:
                cv2.imwrite(os.path.join(framesDir, 'frame_{:06d}.jpg'.format(frame_idx)), frame)
                createTxtFile(frame, jData[videoName][f"frame_{localFrame_idx}"], framesDir, frame_idx)
                localFrame_idx += 1
                frame_idx += 1
        elif typeAnnotation == Annotation.txt:
            if rewriteTxtFiles(video[:-4], localFrame_idx, frame_idx, framesDir):
                cv2.imwrite(os.path.join(framesDir, 'frame_{:06d}.jpg'.format(frame_idx)), frame)
            localFrame_idx += 1
            frame_idx += 1
    return frame_idx


def generateFramesAndTxtFromVideos(srcPath, dstPath, typeAnnotation):
    for group in os.listdir(srcPath):
        if group == "original" and typeAnnotation == Annotation.txt:
            continue

        targetDir = os.path.join(dstPath, group)
        os.makedirs(targetDir, exist_ok=True)

        for video in os.listdir(os.path.join(srcPath, group)):
            print(f"Start process file: {group}/{video}")
            videoName, ext = os.path.splitext(video)
            if not ext in list(Extensions.videos()):
                continue

            category = ""
            videoPath = os.path.join(srcPath, group, video)
            if typeAnnotation == Annotation.json:
                with open(os.path.join(srcPath, group, "annotation", f"{videoName}.json"), "r") as jFile:
                    jData[video] = json.load(jFile)
                category, _ = videoName.rsplit('-', 1)

                framesDir = os.path.join(targetDir, category, 'frames')
                os.makedirs(framesDir, exist_ok=True)
                frameIdx = framingVideo(typeAnnotation,
                                        videoPath,
                                        framesDir,
                                        frame_idx = catIdx[category]["globalFrameIdx"]
                                        )
                catIdx[category]["globalFrameIdx"] = frameIdx
            if typeAnnotation == Annotation.txt:
                category = videoName
                if group == "mix":
                    dstVideoDir = os.path.join(targetDir, videoName)
                    os.makedirs(dstVideoDir, exist_ok=True)
                framesDir = os.path.join(dstVideoDir, 'frames')
                os.makedirs(framesDir, exist_ok=True)
                frameIdx = framingVideo(typeAnnotation,
                                       videoPath,
                                       framesDir)

            if category == "":
                continue

            if video in jData:
                print(f"{video} already processed\n")
                continue


def processAnnotation(pathAnnotation):
    typeAnnotation = os.path.basename(pathAnnotation)
    print(f"Start process .{typeAnnotation} files of annotations to {pathAnnotation} \n")
    generateFramesAndTxtFromVideos(pathAnnotation, Path.dataset, typeAnnotation=typeAnnotation)


def processRawData():
    with open(os.path.join(Path.root,  "categories.names"), "r") as f:
        categoriesList = f.readlines()
        idx = 0
        for cat in categoriesList:
            catIdx[cat[:-1]] = {
                "idx" : idx,
                "globalFrameIdx": 0
            }
            idx += 1

    for folder in os.listdir(Path.raw):
        if folder in list(Annotation.annotationExtList()):
            if folder == "txt":
                processAnnotation(os.path.join(Path.raw, folder))


def main():
    processRawData()


if __name__ == '__main__':
    main()
