import shutil
import os
import json
import random

import cv2
import numpy as np
from config import Path, Extensions
from random import shuffle, seed
from annotator import Annotation
from augmentation import applyAugmentations
import augmentations_kit as ak

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
        if w > 0.05 or h > 0.05: # if annotation is exist
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


def generateFramesAndTxtFromVideos(srcPath, dstPath, typeAnnotation, groups):
    for group in os.listdir(srcPath):
        if not group in groups:
            continue
        targetDir = os.path.join(dstPath, group)
        os.makedirs(targetDir, exist_ok=True)

        for video in os.listdir(os.path.join(srcPath, group)):
            print(f"Start process file: {group}/{video} \n")
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
                #todo for "original" of txt format
                if group == "mix": # skip txt/original directory
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


def processAnnotation(pathAnnotation, groups):
    typeAnnotation = os.path.basename(pathAnnotation)
    print(f"Start process .{typeAnnotation} files of annotations to {pathAnnotation} \n")
    generateFramesAndTxtFromVideos(pathAnnotation, Path.dataset, typeAnnotation=typeAnnotation, groups=groups)


def processRawData(groups):
    for folder in os.listdir(Path.raw):
        if folder in list(Annotation.annotationExtList()):
                processAnnotation(
                    pathAnnotation = os.path.join(Path.raw, folder),
                    groups = groups
                )


def generateAugmentedData(maxCount):
    allPath = []
    augmentations = ak.customAugmentations
    os.makedirs(os.path.join(Path.dataset, "augmented"), exist_ok=True)
    for categoryName in os.listdir(Path.original):
        print(f"Start process category: {categoryName} \n")
        catPathList = [ name for name in os.listdir(os.path.join(Path.original, categoryName, "frames")) if name.endswith("jpg")]
        allPath.append(catPathList)
        cnt = len(catPathList)
        catIdx[categoryName]["count"] = cnt
        print(f"{categoryName} {cnt}")

        augCount = 0
        imgPath = os.path.join(Path.original, categoryName, "frames")
        for image in os.listdir(imgPath):
            if image.endswith("txt"):
                continue
            if maxCount - cnt <= augCount:
                break
            print("\rMax_count: {} augCount: {} | Augmentation image #{} processed".format(maxCount, maxCount - cnt, augCount), end="")
            augCount += 1

            frame = cv2.imread(os.path.join(imgPath, image), cv2.IMREAD_COLOR)
            ih, iw, _ = frame.shape

            txtName = f"{image[:-4]}.txt"
            txtFile = open(os.path.join(imgPath, txtName), "r")

            line = txtFile.readline()
            outAugData = ""
            img = frame
            if line != "":
                idx, xc, yc, w, h = tuple([ float(x) for x in line.split(" ")])
                x1 = (xc - w*0.5) * iw
                y1 = (yc - h*0.5) * ih
                x2 = (xc + w*0.5) * iw
                y2 = (yc + h*0.5) * ih
                bbox = [ y1, x1, y2, x2 ]

                img, bbox = applyAugmentations(frame, bbox, augmentations)

                ih, iw, _ = img.shape

                pb = bbox
                xc = (pb[1] + pb[3]) * 0.5 / iw
                yc = (pb[0] + pb[2]) * 0.5 / ih
                w = (pb[3] - pb[1]) / iw
                h = (pb[2] - pb[0]) / ih

                if w > 0.05 and h > 0.05:
                    outAugData = f"{int(idx)} {xc} {yc} {w} {h}"

            dstPath = os.path.join(Path.dataset, "augmented", categoryName, "frames")
            os.makedirs(os.path.join(dstPath), exist_ok=True)

            augTxtFile = open(os.path.join(dstPath, txtName), "w")
            augTxtFile.writelines(outAugData)
            cv2.imwrite(os.path.join(dstPath, image), img)


def extraSets(groups, cfgPath):
    data = []
    for group in [ os.path.join(Path.dataset, g) for g in groups ]:
        for category in os.listdir(group):
            path = os.path.join(group, category)
            if group != os.path.join(Path.dataset, "negatives"):
                path = os.path.join(path, "frames")

            for imgFile in os.listdir(path):
                if imgFile.endswith("jpg"):
                    data.append(os.path.join(path, imgFile))
                    print(f"{os.path.join(path, imgFile)}")
    random.shuffle(data)

    ftrain = open(os.path.join(cfgPath, "train.txt"), "a")
    ftest = open(os.path.join(cfgPath, "test.txt"), "a")

    for idx, path in enumerate(data):
        if idx <= 0.9 * len(data):
            ftrain.write(f"{path}\n")
        if idx > 0.9 * len(data):
            ftest.write(f"{path}\n")

    ftrain.close()
    ftest.close()


def actualizeCategories(path):
    with open(path, "r") as f:
        categoriesList = f.readlines()
        idx = 0
        for cat in categoriesList:
            catIdx[cat[:-1]] = {
                "idx" : idx,
                "globalFrameIdx": 0,
                "count": 0
            }
            idx += 1
        categoriesCount = idx + 1


def clearAnnotation(path):
    for category in os.listdir(path):
        print("Start process {} \n".format(category))
        for file in os.listdir(os.path.join(path, category, "frames")):
            if file.endswith("txt"):
                print("\rFile {} in process \n".format(file), end="")
                txtFile = open(os.path.join(path, category, "frames", file), "r")
                line = txtFile.readline()
                if line == "":
                    continue
                idx, xc, yc, w, h = tuple([ float(x) for x in line.split(" ")])
                txtFile.close()

                if w < 0.05 or h < 0.05 or xc > 1 or yc > 1:
                    txtFile = open(os.path.join(path, category, "frames", file), "w")
                    txtFile.write("")


def updateAnnotation(folder, newIdx):
    path = os.path.join(Path.raw, 'txt', 'original', folder)
    for txtFile in os.listdir(path):
        print("\r Start process {}".format(txtFile), end="")

        if txtFile.endswith('txt'):
            ftxt = open (os.path.join(path, txtFile), "r")
            res = []
            lines = list(ftxt)
            for line in lines:
                ctg, xc, yc, w, h = tuple(line.split(" "))
                if int(ctg) in newIdx:
                    ctg = newIdx[int(ctg)]

                res.append(f"{ctg} {xc} {yc} {w} {h}")

            ftxt.close()
            with open(os.path.join(path, txtFile), "w") as f:
                f.writelines(res)


def updateRawDataCategoriesAndIndices():
    rctg = dict()

    fctg = open(os.path.join(Path.root, "new_ctg.txt"), "r")
    ctgList = list(fctg)
    updatedCategoriesList = list()

    nidx = 0
    for idx, ctg in enumerate(ctgList):
        if ctg[0] == '#':
            print(f"Skip category {ctg} for process in original folder \n")
            sym, new_ctg = ctg.split(" ")
            ctg = new_ctg
        elif ctg[0] == '!':
            continue
            sym, old_ctg, new_ctg = ctg.split(" ")
            print(f"Start process folder {old_ctg}. Assign new category: {new_ctg} \n")
            if old_ctg.find("On_Guard_of_the_Fatherland_18_1") != -1:
                updateAnnotation(old_ctg[:-2], { idx: rctg[new_ctg]["new_idx"] })  # old ctg idx == 135 -> 111, 136 -> 112
            continue

        ctg = ctg.split("\n")[0]
        if ctg == "Sergius_of_Radonezh_18":
            updateAnnotation(ctg, { 106 : 52 })
        elif ctg == "Seraphim_of_Sarov_18":
            updateAnnotation(ctg, { 106: 51 })
        elif ctg == "Panteleimon":
            updateAnnotation(ctg, { 106: 107 })

        # if idx >= 141:
        #     #ctgFullName = ctg.split("_")
        #     if ctg == "Well_wait_11_1":
        #         updateAnnotation("Well_wait_11", {idx: nidx})
        #     elif ctg == "Peter_I_The_Great_17":
        #         updateAnnotation(ctg, { idx : nidx })
        #         updateAnnotation(f"{ctg}-1", {idx: nidx})
        #         updateAnnotation(f"{ctg}-2", {idx: nidx})
        #     else:
        #         updateAnnotation(ctg, { idx : nidx })

        # rctg[ctg] = {
        #     "new_idx": nidx
        # }

        print(f"{nidx} {ctg}")
        updatedCategoriesList.append(f"{ctg}\n")
        nidx += 1


    with open(os.path.join(Path.root, "categories.txt"), "w") as f:
        f.writelines(updatedCategoriesList)


def main():
    # clearAnnotation(r"D:\Projects\coins-project\DATASETS\final_ext1\dataset\original")
    actualizeCategories(
        path = os.path.join(Path.root,  "categories.names")
    )

    processRawData(
        groups = ["original"]
    ) # framing video, process *.json and *.txt annotation
    generateAugmentedData(
        maxCount=5000
    )

    extraSets(
        groups = ["original", "augmented", "mix", "negatives"],
        cfgPath=r"C:\Projects\darknet_win\my_configs\80_coins_21_10_2019"
    )


if __name__ == '__main__':
    main()
