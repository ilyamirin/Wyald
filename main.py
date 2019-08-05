import shutil
import os
import json

import cv2
import numpy as np

from random import shuffle, seed

category = {
    "1-ruble-avers": 0,
    "2-rubles-avers": 1,
    "5-rubles-avers": 2,
    "10-rubles-avers": 3
}

categoryNames = {
    "1-ruble-avers": "one ruble avers",
    "2-rubles-avers": "two rubles avers",
    "5-rubles-avers": "five rubles avers",
    "10-rubles-avers": "ten rubles avers"
}


def permutate(arr, saveOrder=False, seedValue=1234):
    idxs = [i for i in range(len(arr))]
    if saveOrder:
        seed(seedValue)

    shuffle(idxs)

    if isinstance(arr, np.ndarray):
        arr = arr[idxs]
    elif isinstance(arr, list):
        arr = [arr[idx] for idx in idxs]
    else:
        raise TypeError

    return arr


def prepareAll(cdir, idx):
    picturesDet = []
    picturesCls = []

    for j in range(1, 4):
        picturesFolder = os.path.join(cdir, f"{j}")

        marks = json.load(open(os.path.join(picturesFolder, "mark.json"), "r"))
        pictures = [os.path.join(picturesFolder, name) for name in os.listdir(picturesFolder) if name.endswith(".png")]

        classifierPicturesFolder = os.path.join(picturesFolder, "cut")
        if os.path.exists(classifierPicturesFolder):
            shutil.rmtree(classifierPicturesFolder)
        os.makedirs(classifierPicturesFolder, exist_ok=True)

        detectorFiles = []
        classifierFiles = []
        for i, imagePath in enumerate(pictures):
            i += idx
            #imageName = os.path.basename(imagePath)
            print(imagePath)
            if not imagePath in marks or not marks[imagePath]:
                continue

            categoryName = marks[imagePath]["category"]
            y1, x1, y2, x2 = marks[imagePath]["coords"]
            categoryIdx = category[categoryName]

            image = cv2.imread(imagePath, 1)
            height, width = image.shape[:2]
            detectorFiles.append(imagePath)

            y1 = max(0, y1)
            y2 = min(height, y2)
            x1 = max(0, x1)
            x2 = min(width, x2)

            bbox = image[y1 + 10:y2 - 10, x1 - 10:x2 + 10, :]

            yc = ((y2 + y1) // 2) / height
            xc = ((x2 + x1) // 2) / width
            h = (y2 - y1) / height
            w = (x2 - x1) / width

            imageString = f"{categoryIdx} {xc} {yc} {w} {h}\n"

            with open(imagePath.replace(".png", ".txt"), "w") as file:
                file.write(imageString)

            fnameNew = categoryNames[categoryName]
            # fnameNew = imageName.split("_")[:-2]
            # fnameNew = " ".join(fnameNew)

            newName = f"{i}_{fnameNew}.png"

            if not os.path.exists(os.path.join(classifierPicturesFolder, newName)):
                cv2.imwrite(os.path.join(classifierPicturesFolder, newName), bbox)

            classifierFiles.append(os.path.join(classifierPicturesFolder, newName))

        picturesDet.extend(permutate([name + "\n" for name in detectorFiles]))
        picturesCls.extend(permutate([name + "\n" for name in classifierFiles]))

    picturesDet = permutate(picturesDet)
    picturesCls = permutate(picturesCls)

    return picturesDet, picturesCls

#
# def prepareClassifierFiles(cdir, idx):
#     for i in range(1, 4):
#         flist = []
#         os.makedirs(os.path.join(cdir, "renamed"), exist_ok=True)
#
#         jsonPath = os.path.join(cdir, "mark.json")
#         cdir = os.path.join(cdir, "picrures")
#         pictures = [name for name in os.listdir(cdir) if os.path.isfile(os.path.join(cdir, name))]
#
#         marks = json.load(open(jsonPath, "r"))
#
#         for i, fname in enumerate(pictures):
#             imageMarks = marks.pop(fname, None)
#
#             i += (idx + 1)
#             fnameNew = fname.split("_")[:-1]
#             fnameNew = "-".join(fnameNew)
#
#             newName = f"{i}_{fnameNew}.png"
#
#             newPath = os.path.join(cdir, "renamed", newName)
#             flist.append(newPath + '\n')
#
#             imageMarks[newName] = imageMarks
#
#             if not os.path.exists(newPath):
#                 shutil.copy2(os.path.join(cdir, fname), newPath)
#
#     return permutate(flist), idx + i


def createLabels(trainFile, json_):
    marks = json.load(open(json_, "r"))

    with open(trainFile, "r") as file:
        filePaths = [path.strip() for path in file.readlines()]

    for file in filePaths:
        name = os.path.basename(file)

        imageMarks = marks.get(name, None)
        if imageMarks:
            clsName = imageMarks["name"]
            coords = imageMarks["coords"]

            clsIdx = category[clsName.replace("_", "-")]

            image = cv2.imread(file)
            if image is None:
                continue


def main():
    coinsRootDir = r"C:\Projects\data\coins\frames"
    coinsDirs = []

    for cdir in os.listdir(coinsRootDir):
        coinsDirs.append(os.path.join(coinsRootDir, cdir))

    fileListD = []
    fileListC = []

    idx = 0
    for cdir in coinsDirs:
        curDetList, curCategoryList = prepareAll(cdir, idx)

        idx += len(curCategoryList) + 1

        fileListC.extend(curCategoryList)
        fileListD.extend(curDetList)

    fileListC = permutate(fileListC)
    fileListD = permutate(fileListD)

    with open("trainC.txt", "w") as file:
        file.writelines(fileListC)

    with open("trainD.txt", "w") as file:
        file.writelines(fileListD)


if __name__ == '__main__':
    main()
