import shutil
import os
import json

import cv2
import numpy as np

from random import shuffle, seed

category = {
   "Akhaltekinskiy-kon-2011": 0,
   "astronomiya_2009": 1,
   "bandikut_2011": 2,
   "Barselona-2014": 3,
   "bashnya_2010": 4,
   "Bekenbaue-2012": 5,
   "BELYY-MEDVED-2012": 6,
   "belyye_nochi_2013": 7,
   "buki-2013-avers": 8,
   "Dinozavry-morskiye-2013": 9,
   "dumskaya_bashnya_2010": 10,
   "kavaleriya_1812_2012": 11,
   "klyuch_k_serdtsu_2017": 12,
   "koala_s_opala_2012": 13,
   "koleso_fortuny_2018": 14,
   "lastochkino_gnezdo_2012": 15,
   "livadiyskiy_dvorets_2013": 16,
   "london_2014": 17,
   "lyubov_dragotsenna_2018": 18,
   "matrona_moskvina_2017": 19
}

categoryNames = {
   "Akhaltekinskiy-kon-2011": "Akhaltekinskiy-kon-2011",
   "astronomiya_2009": "astronomiya_2009",
   "bandikut_2011": "bandikut_2011",
   "Barselona-2014": "Barselona-2014",
   "bashnya_2010": "bashnya_2010",
   "Bekenbaue-2012": "Bekenbaue-2012",
   "BELYY-MEDVED-2012": "BELYY-MEDVED-2012",
   "belyye_nochi_2013": "belyye_nochi_2013",
   "buki-2013-avers": "buki-2013-avers",
   "Dinozavry-morskiye-2013": "Dinozavry-morskiye-2013",
   "dumskaya_bashnya_2010": "dumskaya_bashnya_2010",
   "kavaleriya_1812_2012": "kavaleriya_1812_2012",
   "klyuch_k_serdtsu_2017": "klyuch_k_serdtsu_2017",
   "koala_s_opala_2012": "koala_s_opala_2012",
   "koleso_fortuny_2018": "koleso_fortuny_2018",
   "lastochkino_gnezdo_2012": "lastochkino_gnezdo_2012",
   "livadiyskiy_dvorets_2013": "livadiyskiy_dvorets_2013",
   "london_2014": "london_2014",
   "lyubov_dragotsenna_2018": "lyubov_dragotsenna_2018",
   "matrona_moskvina_2017": "matrona_moskvina_2017"
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


def prepareAll(picturesFolder, idx):
    picturesDet = []
    picturesCls = []

    marks = json.load(open(os.path.join(picturesFolder, "mark.json"), "r"))
    pictures = [os.path.join(picturesFolder, name) for name in os.listdir(picturesFolder) if name.endswith(".png")]

    # classifierPicturesFolder = os.path.join(picturesFolder, "cut")
    # if os.path.exists(classifierPicturesFolder):
        #shutil.rmtree(classifierPicturesFolder)

    #os.makedirs(classifierPicturesFolder, exist_ok=True)

    detectorFiles = []
    classifierFiles = []

    for i, imagePath in enumerate(pictures):
        i += idx
        #imageName os.path.basename(imagePath)
        print(f"{imagePath}")
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
        fnameNew = fnameNew.replace("_", "-")
        # fnameNew = imageName.split("_")[:-2]
        # fnameNew = " ".join(fnameNew)
        newName = f"{i}_{fnameNew}.png"

        # if not os.path.exists(os.path.join(classifierPicturesFolder, newName)):
        #     cv2.imwrite(os.path.join(classifierPicturesFolder, newName), bbox)

        #classifierFiles.append(os.path.join(classifierPicturesFolder, newName))

    picturesDet.extend(permutate([name + "\n" for name in detectorFiles]))
    # picturesCls.extend(permutate([name + "\n" for name in classifierFiles]))

    picturesDet = permutate(picturesDet)
    # picturesCls = permutate(picturesCls)

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


# def createLabels(trainFile, json_):
#     marks = json.load(open(json_, "r"))
#
#     with open(trainFile, "r") as file:
#         filePaths = [path.strip() for path in file.readlines()]
#
#     for file in filePaths:
#         name = os.path.basename(file)
#
#         imageMarks = marks.get(name, None)
#         if imageMarks:
#             clsName = imageMarks["name"]
#             coords = imageMarks["coords"]
#             clsIdx = category[clsName.replace("_", "-")]
#
#             image = cv2.imread(file)
#             if image is None:
#                 continue

def main():
    rootDir = r'C:\Projects\data\coins'
    frameDir = os.path.join(rootDir, 'frames')

    fileListD = []
    fileListC = []

    idx = 0

    for cdir in os.listdir(frameDir):
        curDetList, curCategoryList = prepareAll(os.path.join(frameDir, cdir), idx)
        idx += len(curCategoryList) + 1
        # fileListC.extend(curCategoryList)
        fileListD.extend(curDetList)

    # C:\\Projects\\coins\\data\\coins\\frames\\imgs\
    # frameRublesDir = r"C:\Projects\coins\data\coins\frames\imgs"
    # for cdir in os.listdir(frameRublesDir):
    #     curDetList, curCategoryList = prepareAll(os.path.join(frameRublesDir, cdir), idx)
    #     idx += len(curCategoryList) + 1
    #     fileListC.extend(curCategoryList)
    #
    #     fileListD.extend(curDetList)

    # fileListC = permutate(fileListC)
    fileListD = permutate(fileListD)

    # with open("trainC.txt", "w") as file:
    #     file.writelines(fileListC)

    with open("trainD.txt", "w") as file:
        file.writelines(fileListD)


if __name__ == '__main__':
    main()
