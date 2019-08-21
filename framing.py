import os
import imageio
import imgaug as ia
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

import cv2
import json

lastIdx = dict()

def augmentImage(image, x1, x2, y1, y2):
    images = [ image for i in range(0, 5)]
    seq = iaa.Sequential([
        iaa.AdditiveGaussianNoise(scale=(10, 60)),
        iaa.GammaContrast(1.5),
    ], random_order=True)

    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2),
    ], shape=image.shape)

    
    return images

def framingVideoFile(rootDir, frameDir, vname):
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)

    frameDstPath = os.path.join(frameDir, vname[:-4])
    if not os.path.exists(frameDstPath):
        os.makedirs(frameDstPath)

    jsonFin = open(os.path.join(frameDir, vname[:-4], 'mark.json'), 'r')
    jsonData = json.load(jsonFin)
    cap = cv2.VideoCapture(os.path.join(rootDir, vname))
    # idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # cv2.waitKey(5)
        categoryName = f'{vname[:-7]}'
        if not categoryName in lastIdx:
            lastIdx[categoryName] = 0
        lastIdx[categoryName] += 1
        if lastIdx[categoryName] > 15:
            break
        fname = f'{vname[:-4]}-{lastIdx[categoryName]}.png'
        t = os.path.join(frameDstPath, fname)
        print(t)
        if not os.path.exists(t):
            y1, x1, y2, x2 = jsonData[os.path.join(frameDir, vname[:-4], fname)]
            images = augmentImage(frame, x1, x2, y1, y2)
            cv2.imwrite(t, frame)
    jsonFin.close()


def main():
    rootDir = r'C:\Projects\data\coins'
    rootDir = r'E:\data\coins\sber'
    frameDir = os.path.join(rootDir, 'frames')
    videoDir = os.path.join(rootDir, 'video')

    for videoFile in os.listdir(videoDir):
        framingVideoFile(videoDir, frameDir, videoFile)

if __name__ == "__main__":
    main()