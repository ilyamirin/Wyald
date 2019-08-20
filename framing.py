import os
import imageio
import imgaug as ia
from imgaug import augmenters as iaa

import cv2
import json

lastIdx = dict()

def augmentImage(image, bbox):
    images = [ image for i in range(0, 5)]
    seq = iaa.Sequential([
        iaa.AdditiveGaussianNoise(scale=(10, 60)),
        iaa.GammaContrast(1.5),
    ], random_order=True)

    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=0.2 * 447, x2=0.85 * 447, y1=0.3 * 298, y2=0.95 * 298),
        BoundingBox(x1=0.4 * 447, x2=0.65 * 447, y1=0.1 * 298, y2=0.4 * 298)
    ], shape=image.shape)

    return images

def framingVideoFile(rootDir, frameDir, vname):
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)

    frameDstPath = os.path.join(frameDir, vname[:-4])
    if not os.path.exists(frameDstPath):
        os.makedirs(frameDstPath)

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
            images = augmentImage(frame, )
            cv2.imwrite(t, frame)


def main():
    rootDir = r'C:\Projects\data\coins'
    rootDir = r'E:\data\coins\sber'
    frameDir = os.path.join(rootDir, 'frames')
    videoDir = os.path.join(rootDir, 'video')

    # jsonMetaData = {}
    #
    # infoOutput = open('info.txt', "w")
    for videoFile in os.listdir(videoDir):
        framingVideoFile(videoDir, frameDir, videoFile)
        # json.dump(f"{videoFile}: {{ 'frames': {framesCount}, 'completed': {True} }}", infoOutput, indent=3)

if __name__ == "__main__":
    main()