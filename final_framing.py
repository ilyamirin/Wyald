import os

import cv2
from config import Path, Constants, Extensions


Categories = dict()


def parseTxtFile(filePath):
    rectangles = []
    if not os.path.exists(filePath):
        return rectangles

    with open(filePath, "r") as file:
        for line in file.readlines():
            rectangles.append(list(map(float, line.rstrip().split(' '))))

    return rectangles


def testMarkOnFrame(dirName):
    frameDir = os.path.join(Path.root, 'marked', Constants.frames)
    txtDir = os.path.join(Path.root, 'marked', dirName)

    for filename in os.listdir(frameDir):
        framePath = os.path.join(frameDir, filename)

        frame = cv2.imread(framePath)
        h, w, d = frame.shape

        name, ext = os.path.splitext(filename)
        rects = parseTxtFile(os.path.join(txtDir, f"{name}{Extensions.txt}"))

        for ctgTdx, xc, yc, tw, th in rects:
            x1 = int((xc - tw*0.5)*w)
            y1 = int((yc + th*0.5)*h)
            x2 = int(x1 + tw*w)
            y2 = int(y1 - th*h)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 00), 2)

        cv2.imshow("output", frame)
        cv2.waitKey(3)


def parseCategories(path):
    res = []
    with open(path, "r") as file:
        for line in file.readlines():
            res.extend(line.rstrip().split(' '))
    return res


def fixCategoriesIndexes(ctgList):
    correctIdx = 0
    for idx, ctg in enumerate(ctgList):
        if idx == 60:
            continue
        Categories[ctg] = correctIdx
        correctIdx += 1


def framingVersion3(videoPath, targetDir):
    from utils import writeLines
    # txtDir, ext = os.path.splitext(videoPath)
    cap = cv2.VideoCapture(videoPath)
    # ctgList = parseCategories(os.path.join(Path.root, "categories.txt"))

    idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        name = "frame_{:06d}".format(idx)
        cv2.imwrite(os.path.join(targetDir, f"{name}{Extensions.jpg}"), frame)
        rects = parseTxtFile(os.path.join(videoPath[:-4], f"{name}{Extensions.txt}"))

        for r in rects:
            if r[0] > 57:
                r[0] -= 1

        lines = []
        for r in rects:
            ctgIdx = int(r[0])
            xc, yc, tw, th = r[1], r[2], r[3], r[4]
            lines.append(f"{ctgIdx} {xc} {xc} {tw} {th}")
        writeLines(lines, os.path.join(targetDir, f"{name}{Extensions.txt}"))
        idx += 1


def main(videoDir, targetDir):
    os.makedirs(targetDir, exist_ok=True)

    ctgList = parseCategories(os.path.join(Path.root, "categories.txt"))
    fixCategoriesIndexes(ctgList)

    for video in os.listdir(videoDir):
        if not video.endswith(".MOV"):
            continue

        name, ext = os.path.splitext(video)
        frameDir = os.path.join(targetDir, name, 'frames')
        if os.path.exists(frameDir):
            continue

        os.makedirs(frameDir, exist_ok=True)

        print(f"Start process video {video}")
        framingVersion3(
            videoPath=os.path.join(videoDir, video),
            targetDir=frameDir
        )


if __name__ == "__main__":
    # name = os.path.join(Path.raw, 'IMG_0003.MOV')
    # txtDirName, ext = os.path.splitext('IMG_0003.MOV')
    # testMarkOnFrame(txtDirName)

    main(
        videoDir=os.path.join(Path.raw_final),
        targetDir=os.path.join(Path.dataset, 'mix')
    )