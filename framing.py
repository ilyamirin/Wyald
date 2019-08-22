import os
import imageio
import imgaug as ia
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

import cv2
import json

lastIdx = dict()

def augmentImage(imgDsrDir, fname, category, image, x1, x2, y1, y2, Idx=0):
    print(imgDsrDir)
    print(category)
    images = [ image for i in range(0, 4)]
    seq = iaa.Sequential([
        iaa.MotionBlur(3, 15),
        iaa.AdditiveGaussianNoise(scale=(10, 60)),
        iaa.GammaContrast(1.5)
    ], random_order=True)

    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2) for i in range(0, 4)
    ], shape=images.shape)

    image_aug, bbs_aug = seq(image=images, bounding_boxes=bbs)
    for img in image_aug:
        Idx += 1
        ia.imshow(img)
        cv2.imwrite(os.path.join(imgDsrDir, f'aug-{Idx}-{fname}'), img)
    return images

def framingVideoFile(videoDir, frameDir, videoPath):
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)

    curCoinDir = os.path.basename(videoPath)[:-4]
    frameDstPath = os.path.join(frameDir, curCoinDir)
    if not os.path.exists(frameDstPath):
        os.makedirs(frameDstPath)

    jsonFin = open(os.path.join(frameDir, curCoinDir, 'mark.json'), 'r')
    jsonData = json.load(jsonFin)
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
        # if lastIdx[categoryName] > 15:
        #     break
        fname = f'{curCoinDir}-{lastIdx[categoryName]}.jpg'
        t = os.path.join(frameDstPath, fname)
        print(t)
        if not os.path.exists(t):
            # key = os.path.join(frameDir, vname[:-4], fname)
            # y1, x1, y2, x2 = jsonData[key]["coords"]
            # images = augmentImage(f"{frameDstPath}-aug", fname, jsonData[key]["category"], frame, x1, x2, y1, y2)
            cv2.imwrite(t, frame)
    jsonFin.close()


def main():
    rootDir = r'C:\Projects\data\coins'
    rootDir = r'E:\data\coins\sber'
    frameDir = r'E:\data\coins\frames' # os.path.join(rootDir, frames)
    videoDir = os.path.join(rootDir, 'video')

    for dir in os.listdir(frameDir):
        videoPath = os.path.join(videoDir, f'{dir}.MOV')
        if os.path.exists(videoPath):
            framingVideoFile(videoDir, frameDir, videoPath)

    # for dir in os.listdir(videoDir):
    #     videoSubDir = os.path.join(videoDir, dir)
    #     for videoFile in os.listdir(videoSubDir):
    #         framingVideoFile(videoSubDir, frameDir, videoFile)

if __name__ == "__main__":
    main()