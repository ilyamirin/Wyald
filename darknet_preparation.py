import  os
import json

from colorama import Fore, Style

from utils import extractBasename, extractCategory, walk, permutate, clean, makeJSONname, extendName
from config import Extensions, Path, Constants as const


def cleanOldMarks(path):
    clean(path, targetExtensions=Extensions.txt)


def extractMarks(framesDir):
    marksPath = os.path.join(framesDir, makeJSONname(const.marks))

    try:
        marks = json.load(open(marksPath, "r"))
    except FileNotFoundError:
        return

    print(f"{Fore.GREEN} Processing {marksPath} {Style.RESET_ALL}")

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

    
def makeSets():
    pass


def main():
    pass


if __name__ == "__main__":
    pass

