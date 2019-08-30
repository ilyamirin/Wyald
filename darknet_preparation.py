import  os
import json

from colorama import Fore, Style
import cv2

from utils import walk, permutate, clean, makeJSONname, extendName, readLines, writeLines, matchLists, changeExtension
from config import Extensions, Path, Constants as const


def cleanOldMarks(path):
    print("Cleaning old darknet marks")
    clean(path, targetExtensions=Extensions.txt, through=True)


def extractMark(framesDir, frameName, ctgIdx, x1, y1, x2, y2, w, h):
    xc = (x2 + x1) / (2 * w)
    yc = (y2 + y1) / (2 * h)
    bw = (x2 - x1) / w
    bh = (y2 - y1) / h

    s = f"{ctgIdx} {xc} {yc} {bw} {bh}\n"

    with open(os.path.join(framesDir, extendName(frameName, Extensions.txt)), "w") as f:
        f.write(s)

    if bh < 0.05 or bw < 0.05:  # грубая проверка на адекватность разметки
        s = ""


def extractCrops(framesDir, frameName, idx, x1, y1, x2, y2):
    image = cv2.imread(os.path.join(framesDir, extendName(frameName, Extensions.jpg)))
    bbox = image[y1 + 10:y2 - 10, x1 - 10:x2 + 10, :]

    frameName = frameName.replace("_", "-")
    newName = f"{idx}_{extendName(frameName, Extensions.jpg)}"

    cutDir = os.path.join(framesDir, const.cut)
    os.makedirs(cutDir, exist_ok=True)
    if not os.path.exists(os.path.join(cutDir, newName)):
        cv2.imwrite(os.path.join(cutDir, newName), bbox)


def extractData(categoryDir):
    idx = [0]
    marksPath = os.path.join(categoryDir, makeJSONname(const.marks))
    framesDir = os.path.join(categoryDir, const.frames)

    try:
        marks = json.load(open(marksPath, "r"))
    except FileNotFoundError:
        return

    print(f"\n{Fore.GREEN}Processing {marksPath} {Style.RESET_ALL}")

    for frameIdx, frameName in enumerate(marks):
        frameIdx += idx[0]
        frameMarks = marks[frameName]
        framePath = os.path.join(framesDir, frameMarks[const.image])

        if not os.path.exists(framePath):
            continue

        y1, x1, y2, x2 = frameMarks[const.coords]
        h, w = frameMarks[const.imageShape]

        extractMark(framesDir, frameName, marks[frameName], x1, y1, x2, y2, w, h)
        print("\r{:.1f}% of work has been done".format((frameIdx + 1) / len(marks) * 100), end="")

        extractCrops(framesDir, frameName, frameIdx, x1, y1, x2, y2)
        print("\r{:.1f}% of work has been done".format((frameIdx + 1) / len(marks) * 100), end="")

    idx[0] += len(marks.keys()) + 1


def extractMarks(categoryDir):
    marksPath = os.path.join(categoryDir, makeJSONname(const.marks))
    framesDir = os.path.join(categoryDir, const.frames)

    try:
        marks = json.load(open(marksPath, "r"))
    except FileNotFoundError:
        return

    print(f"\n{Fore.GREEN}Processing {marksPath} {Style.RESET_ALL}")

    for frameIdx, frameName in enumerate(marks):
        frameMarks = marks[frameName]
        framePath = os.path.join(framesDir, frameMarks[const.image])

        if not os.path.exists(framePath):
            continue

        y1, x1, y2, x2 = frameMarks[const.coords]
        ctgIdx = frameMarks[const.ctgIdx]
        h, w = frameMarks[const.imageShape]

        xc = (x2 + x1) / (2 * w)
        yc = (y2 + y1) / (2 * h)
        bw = (x2 - x1) / w
        bh = (y2 - y1) / h

        darknetString = f"{ctgIdx} {xc} {yc} {bw} {bh}\n"

        if bh < 0.05 or bw < 0.05: # грубая проверка на адекватность разметки
            darknetString = ""

        with open(os.path.join(framesDir, extendName(frameName, Extensions.txt)), "w") as f:
            f.write(darknetString)

        print("\r{:.1f}% of work has been done".format((frameIdx + 1) / len(marks) * 100), end="")


def extractMarksThroughDataset(datasetPath):
    cleanOldMarks(datasetPath)
    frames = walk(datasetPath, targetDirs=const.frames).get("dirs")

    for dirsSet in frames:
        dirsSet = dirsSet[:-1]

        categoryDir = os.path.join(datasetPath, *dirsSet)
        extractMarks(categoryDir)
        # extractData(categoryDir)


def makeSets(directories, wpath=Path.sets, trainPart=0.8, validPart=0.2, ignoreOld=False):
    assert 0 < trainPart + validPart <= 1
    os.makedirs(wpath, exist_ok=True)

    testPart = 1 - trainPart - validPart

    sets = {
        const.train: {
            "path": os.path.join(wpath, extendName(const.train, Extensions.txt)),
            "part": trainPart,
            "content": []
        },
        const.valid: {
            "path": os.path.join(wpath, extendName(const.valid, Extensions.txt)),
            "part": validPart,
            "content": []
        },
        const.test: {
            "path": os.path.join(wpath, extendName(const.test, Extensions.txt)),
            "part": testPart,
            "content": []
        }
    }

    inUse = []
    for set_, info in sets.items():
        info["content"] = readLines(info["path"]) if not ignoreOld else []
        inUse.extend(info["content"])

    images = []
    marks = []
    for dirIdx, path in enumerate(directories):
        print("\rSearching for images and marks in listed directories, {:.1f}% has been done".
              format(dirIdx / len(directories) * 100))

        dirImages = [os.path.join(path, *img) for img in walk(path, targetExtensions=Extensions.images()).get("extensions")]
        images.extend(dirImages)
        dirMarks = [os.path.join(path, *mrk) for mrk in walk(path, targetExtensions=Extensions.txt).get("extensions")]
        marks.extend(dirMarks)

    transformer = lambda x: changeExtension(x, Extensions.txt)
    print("Matching images to marks, please wait...")
    images = matchLists(master=marks, slave=images, transformer=transformer)
    _, images = matchLists(master=inUse, slave=images, getMismatched=True)

    images = permutate(images)

    start = 0
    for set_, info in sets.items():
        part = info["part"]
        end = start + int(part * len(images))

        total = end - start

        info["content"].extend(images[start:end])
        start = end

        writeLines(lines=info["content"], path=info["path"])
        print(f"\n{Fore.GREEN}Added {total} paths to {set_} {Style.RESET_ALL}")


def purifySets():
    sets = {
        const.train: os.path.join(Path.sets, extendName(const.train, Extensions.txt)),
        const.valid: os.path.join(Path.sets, extendName(const.valid, Extensions.txt)),
        const.test: os.path.join(Path.sets, extendName(const.test, Extensions.txt)),
    }

    for set_, path in sets.items():
        files = readLines(path)
        total = len(files)
        files = [f for f in files if os.path.exists(f)]
        writeLines(files, path)

        print(f"Cleaned {total - len(files)} from {path}")


def main():
    pass


if __name__ == "__main__":
    pass

