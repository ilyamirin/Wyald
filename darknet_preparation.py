import  os
import json

from colorama import Fore, Style

from utils import walk, permutate, clean, makeJSONname, extendName, readLines, writeLines, matchLists, changeExtension
from config import Extensions, Path, Constants as const


def cleanOldMarks(path):
    clean(path, targetExtensions=Extensions.txt)


def extractMarks(framesDir):
    marksPath = os.path.join(framesDir, makeJSONname(const.marks))

    try:
        marks = json.load(open(marksPath, "r"))
    except FileNotFoundError:
        return

    print(f"{Fore.GREEN}Processing {marksPath} {Style.RESET_ALL}")

    for frameIdx, frameName in enumerate(marks):
        frameMarks = marks[frameName]
        framePath = os.path.join(framesDir, frameMarks[const.image])

        if not os.path.exists(framePath):
            continue

        y1, x1, y2, x2 = frameMarks[const.coords]
        ctgIdx = frameMarks[const.ctgIdx]
        h, w = frameMarks[const.imageShape]

        xc = (x2 + x1) / (2 * w)
        yc = (y2 - y1) / (2 * h)
        bw = (x2 - x1) / w
        bh = y2 - y1 / h

        darknetString = f"{ctgIdx} {xc} {yc} {bw} {bh}\n"

        with open(os.path.join(framesDir, extendName(frameName, Extensions.txt)), "w") as f:
            f.write(darknetString)

        print("\r{:.1f}% of work has been done".format(frameIdx + 1 / len(marks) * 100), end="")


def makeSets(directories, trainPart=0.8, validPart=0.2, ignoreOld=False):
    assert 0 < trainPart + validPart <= 1

    testPart = 1 - trainPart - validPart

    sets = {
        const.train: {
            "path": os.path.join(Path.sets, extendName(const.train, Extensions.txt)),
            "part": trainPart,
            "content": []
        },
        const.valid: {
            "path": os.path.join(Path.sets, extendName(const.valid, Extensions.txt)),
            "part": validPart,
            "content": []
        },
        const.test: {
            "path": os.path.join(Path.sets, extendName(const.test, Extensions.txt)),
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
    for path in directories:
        images.extend(walk(path, targetExtensions=Extensions.images()).get("files"))
        marks.extend(walk(path, targetExtensions=Extensions.txt).get("files"))

    transformer = lambda x: changeExtension(x, Extensions.txt)
    images = matchLists(master=marks, slave=images, transformer=transformer)
    _, images = matchLists(master=inUse, slave=images, getMismatched=True)

    images = permutate(images)

    start = 0
    for set_, info in sets:
        part = info["part"]
        end = start + int(part * len(images))

        total = end - start

        info["content"].extend(images[start:end])
        start = end

        writeLines(lines=info["content"], path=info["path"])
        print(f"\n{Fore.GREEN} Added {total} paths to {set_} {Style.RESET_ALL}")


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

