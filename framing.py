import os
import random
import json

import cv2

from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage
from colorama import Fore, Back, Style

from verifier import actualizeInfoWithFrames
from utils import makeJSONname, extractCategory, extractBasename, extendName
from config import Extensions, Path, Constants as const


lastIdx = dict()


def loadCategories(path):
    if not os.path.exists(path):
        return []

    with open(path, "r") as f:
        ctgs = f.readlines()

    ctgs = [l.strip() for l in ctgs]

    return ctgs


def updateCategories(categories, path):
    categories = [ctg + "\n" for ctg in categories]

    with open(path, "w") as f:
        f.writelines(categories)


def frameVideo(filePath, marksPath, framesPath, globalIdx=0, overwrite=False, extension=Extensions.png, params=None):
    categories = loadCategories(Path.categories)
    basename = extractBasename(filePath)

    try:
        jsonName = makeJSONname(basename)
        marks = json.load(open(os.path.join(marksPath, jsonName), "r"))
    except:
        print(f"{Fore.RED} There is no json file {jsonName} for {filePath} {marksPath} {Style.RESET_ALL}")
        return

    framesGenerator = generateFrames(filePath)

    marksSeparated = {}
    total = 0
    for idx, frame in enumerate(framesGenerator):
        frameID = f"frame_{idx}"
        if frameID not in marks:
            continue
        else:
            frameMarks = marks[frameID]

        category = marks.get(const.category)
        subcategory = marks.get(const.subcategory, "")

        dirPath = os.path.join(framesPath, const.original, category, subcategory, const.frames)
        os.makedirs(dirPath, exist_ok=True)

        if subcategory:
            key = subcategory
            subcategory = "_" + subcategory
        else:
            key = const.merged

        if key not in marksSeparated:
            marksSeparated[key] = {}

        idx += globalIdx
        frameID = f"frame_{idx}"
        fullCategory = f"{category}{subcategory}"

        if fullCategory not in categories:
            categories.append(fullCategory)

        ctgIdx = categories.index(fullCategory)
        frameName = f"{fullCategory}{const.separator}{frameID}{const.separator}{const.original}"

        marksSeparated[key][frameName] = {
            const.image: extendName(frameName, extension),
            const.coords: frameMarks[const.coords],
            const.fullCategory: fullCategory,
            const.ctgIdx: ctgIdx,
            const.imageShape: frame.shape[:2]
        }

        framePath = os.path.join(dirPath, frameName)
        if not overwrite and os.path.exists(framePath):
            continue

        cv2.imwrite(framePath, frame, params)
        total += 1

        print("\rFrame #{} has been added".format(idx), end="")

    updateCategories(categories, Path.categories)
    print(f"\n{Fore.GREEN} Updated categories file {Path.categories} {Style.RESET_ALL}")
    print(f"\n{Fore.GREEN} Added {total} frames in total {Style.RESET_ALL}")


def generateFrames(videoPath):
    cap = cv2.VideoCapture(videoPath)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        yield frame


def processVideoFolder(folderPath, marksPath, framesPath, overwrite=False, extension=Extensions.png, params=None):
    videos = [video for video in os.listdir(folderPath) if video.endswith(Extensions.mov)]

    actualInfo = {}
    try:
        actualInfo = json.load(open(Path.actualInfo, "r"))
    except Exception as e:
        print(e)

    for video in videos:
        filePath = os.path.join(folderPath, video)

        category = extractCategory(video)
        globalIdx = actualInfo.get(category, {}).get(const.original, {}).get(const.overall, 0)

        print(f"\n{Fore.GREEN} Video {filePath} is being processed {Style.RESET_ALL}")
        frameVideo(
            filePath=filePath,
            marksPath=marksPath,
            framesPath=framesPath,
            globalIdx=globalIdx,
            overwrite=overwrite,
            extension=extension,
            params=params
        )

    actualizeInfoWithFrames(framesPath)


def augmentImage(image, x1, x2, y1, y2):
    augMethods = [
        iaa.MotionBlur(20, random.randint(0, 360)),
        iaa.AdditiveGaussianNoise(scale=(10, 60)),
        iaa.AllChannelsCLAHE(clip_limit=5)
    ]
    aug = iaa.OneOf(augMethods)

    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2)
    ], shape=image)

    images_aug, bbs_aug = aug(images=[ image for _ in range(len(augMethods)) ],
                              bounding_boxes=[ bbs for _ in range(len(augMethods)) ])
    return images_aug, bbs_aug


def saveAugmentedImages(imgDsrDir, fname, category, images_aug, bbs, Idx=0):
    print(f"Start augmentation of image {fname} \n Location: {imgDsrDir}-aug \t Category: {category} ")

    for img in images_aug:
         Idx += 1
         # ia.imshow(img)

         augDir = f"{imgDsrDir}-aug"
         if not os.path.exists(augDir):
             os.mkdir(augDir)
             print(f"Directory {augDir} was create")

         imgPath = os.path.join(augDir, f'aug-{Idx}-{fname}')
         cv2.imwrite(imgPath, img)
         print(f"{Fore.GREEN} Augmented image {imgPath} was created")


def framingVideoFile(videoDir, frameDir, videoPath):
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)
        print(f"{Fore.GREEN} Directory {frameDir} was created")

    curCoinDir = os.path.basename(videoPath)[:-4]
    frameDstPath = os.path.join(frameDir, curCoinDir)
    if not os.path.exists(frameDstPath):
        os.makedirs(frameDstPath)
        print(f"{Fore.GREEN} Directory {frameDstPath} was created")

    jsonData = json.load(open(os.path.join(frameDir, curCoinDir, 'mark.json'), 'r'))
    cap = cv2.VideoCapture(videoPath)
    # idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # cv2.waitKey(5)
        categoryName = f'{curCoinDir[:-3]}'
        if not categoryName in lastIdx:
            lastIdx[categoryName] = 0
        lastIdx[categoryName] += 1
        if lastIdx[categoryName] > 5:
             break
        fname = f'{curCoinDir}-{lastIdx[categoryName]}.png'
        t = os.path.join(frameDstPath, fname)
        print(t)
        if not os.path.exists(t):
            cv2.imwrite(t, frame)

            y1, x1, y2, x2 = jsonData[t]["coords"]
            for i in range(6):
                images, bbs = augmentImage(frame, x1, x2, y1, y2)
                saveAugmentedImages(frameDstPath, fname, jsonData[t]["category"], images, bbs)


def main():
    rootDir = r'D:\Projects\coins-project\data'
    frameDir = os.path.join(rootDir, 'frames')
    keys = ['sber', 'rubles']
    coinsDirs = { 'sber': os.path.join(rootDir, 'sber'), 'rubles' : os.path.join(rootDir, 'rubles')}
    videoDirs = { 'sber' : os.path.join(coinsDirs['sber'], 'video'), 'rubles': os.path.join(coinsDirs['rubles'], 'video')}

    for dir in os.listdir(frameDir):
        for k in keys:
            videoPath = os.path.join(videoDirs[k], f'{dir}.{ "MOV" if k == "sber" else "mp4"}')
            if not os.path.exists(videoPath):
                print(f"{Fore.RED} File {videoPath} was not found")
                continue
            framingVideoFile(videoDirs[k], frameDir, videoPath)
            break


if __name__ == "__main__":
    main()