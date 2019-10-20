import os
import json
import time
import multiprocessing as mp

from colorama import Fore, Style
import cv2

from utils import walk, permutate, clean, makeJSONname, extendName, readLines, writeLines, matchLists, changeExtension
from verifier import fitCoords, openJsonSafely
from config import Extensions, Path, Constants as const


def cleanOldMarks(path):
    print("Cleaning old darknet marks")
    clean(path, targetExtensions=Extensions.txt, through=True)


# def extractMark(framesDir, frameName, ctgIdx, x1, y1, x2, y2, w, h):
#     xc = (x2 + x1) / (2 * w)
#     yc = (y2 + y1) / (2 * h)
#     bw = (x2 - x1) / w
#     bh = (y2 - y1) / h
#
#     s = f"{ctgIdx} {xc} {yc} {bw} {bh}\n"
#
#     with open(os.path.join(framesDir, extendName(frameName, Extensions.txt)), "w") as f:
#         f.write(s)
#
#     if bh < 0.05 or bw < 0.05:  # грубая проверка на адекватность разметки
#         s = ""
#
#
# def extractCrops(cutDir, framePath, idx, x1, y1, x2, y2):
#     image = cv2.imread(framePath)
#     h, w, _ = image.shape
#
#     bbox = image[min(y1 + 10, 0):max(y2 - 10, h), max(x1 - 10, 0):min(x2 + 10, w), :]
#
#     frameName = os.path.splitext(os.path.basename(framePath))[0].replace("_", "-")
#     newName = f"{idx}_{extendName(frameName, Extensions.jpg)}"
#
#     if not os.path.exists(os.path.join(cutDir, newName)):
#         cv2.imwrite(os.path.join(cutDir, newName), bbox)
#
#
# def extractData(categoryDir, idx):
#     # idx = [0]
#     import shutil
#     marksPath = os.path.join(categoryDir, makeJSONname(const.marks))
#     framesDir = os.path.join(categoryDir, const.frames)
#     cutDir = os.path.join(os.path.dirname(framesDir), const.cut)
#     if os.path.exists(cutDir):
#         shutil.rmtree(cutDir)
#
#     os.makedirs(cutDir, exist_ok=True)
#
#     try:
#         marks = json.load(open(marksPath, "r"))
#     except FileNotFoundError:
#         return
#
#     print(f"\n{Fore.GREEN}Processing {marksPath} {Style.RESET_ALL}")
#
#     # i = 0
#     for frameIdx, frameName in enumerate(marks):
#         # if i == 5:
#         #     break
#         # i += 1
#         # # frameIdx += idx[0]
#         frameMarks = marks[frameName]
#         framePath = os.path.join(framesDir, frameMarks[const.image])
#
#         if not os.path.exists(framePath):
#             continue
#
#         y1, x1, y2, x2 = frameMarks[const.coords]
#         h, w = frameMarks[const.imageShape]
#
#         xc = (x2 + x1) / 2
#         yc = (y2 + y1) / 2
#         bw = (x2 - x1)
#         bh = (y2 - y1)
#
#         if not checkBoundingBoxIsCorrect(xc, yc, bw, bh):
#             continue
#         # extractMark(framesDir, frameName, marks[frameName], x1, y1, x2, y2, w, h)
#         # print("\r{:.1f}% of work has been done".format((frameIdx + 1) / len(marks) * 100), end="")
#
#         extractCrops(cutDir, os.path.join(framesDir, extendName(frameName, Extensions.jpg)), idx[0], x1, y1, x2, y2)
#         print("\r{:.1f}% of work has been done".format((frameIdx + 1) / len(marks) * 100), end="")
#
#         idx[0] += 1


def checkBoundingBoxIsCorrect(w, h):
    if w < 0.05 or h < 0.05:
        return False

    aspectRatio = max(w / h, h / w)
    if aspectRatio > 4:
        return False

    return True


def extractCrops(categoryDir, extractionPath=None, extension=Extensions.png, params=None, globalIdx=0):
    marksPath = os.path.join(categoryDir, makeJSONname(const.marks))
    framesDir = os.path.join(categoryDir, const.frames)
    cutDir = os.path.join(categoryDir, const.cut) if extractionPath is None else extractionPath

    os.makedirs(cutDir, exist_ok=True)

    try:
        marks = json.load(open(marksPath, "r"))
    except FileNotFoundError:
        return

    print(f"{Fore.GREEN}Processing crop operation for {marksPath} {Style.RESET_ALL}")
    time.sleep(0.5)

    for frameIdx, frameName in enumerate(marks):
        frameMarks = marks[frameName]
        framePath = os.path.join(framesDir, frameMarks[const.image])

        if not os.path.exists(framePath):
            globalIdx += 1
            continue

        y1, x1, y2, x2 = frameMarks[const.coords]
        fullCategory = frameMarks[const.fullCategory]
        h, w = frameMarks[const.imageShape]

        cutName = f"{globalIdx}_{extendName(fullCategory, extension)}"
        globalIdx += 1

        if not checkBoundingBoxIsCorrect(x2 - x1, y2 - y1):
            continue

        y1, x1, y2, x2 = fitCoords((y1 - 10, x1 - 10, y2 + 10, x2 + 10), (h, w))

        if os.path.exists(os.path.join(cutDir, cutName)):
            print("\r{:.1f}% of work has been done for {} category".
                  format((frameIdx + 1) / len(marks) * 100, fullCategory), end="")
            continue

        frame = cv2.imread(framePath)
        cut = frame[y1:y2, x1:x2, ...]
        cv2.imwrite(os.path.join(cutDir, cutName), cut, params)

        print("\r{:.1f}% of work has been done for {} category".
              format((frameIdx + 1) / len(marks) * 100, fullCategory), end="")

    return globalIdx


def extractCropsThroughDataset(datasetPath, extractionPath=None, categories=None, subcategories=None,
                               extension=Extensions.png, params=None, parallel=True, threads=16):

    frames = walk(datasetPath, targetDirs=const.frames).get("dirs")
    frames = filterFolders(frames, categories, subcategories)

    if parallel:
        threads = min(threads, mp.cpu_count())
    else:
        threads = 1

    globalIdx = 0
    threadsList = []
    with mp.Pool(threads) as pool:
        for dirsSet in frames:
            dirsSet = dirsSet[:-1]
            categoryDir = os.path.join(datasetPath, *dirsSet)

            length = len(openJsonSafely(os.path.join(categoryDir, makeJSONname(const.marks))))

            threadsList.append(
                pool.apply_async(
                    extractCrops,
                    args=(categoryDir, ),
                    kwds={
                        "extractionPath": extractionPath,
                        "extension": extension,
                        "params": params,
                        "globalIdx": globalIdx
                    }
                )
            )

            globalIdx += length

        for r in threadsList:
            r.get()


def extractMarks(categoryDir):
    marksPath = os.path.join(categoryDir, makeJSONname(const.marks))
    framesDir = os.path.join(categoryDir, const.frames)

    try:
        marks = json.load(open(marksPath, "r"))
    except FileNotFoundError:
        return

    print(f"\n{Fore.GREEN}Processing extraction marks for {marksPath} {Style.RESET_ALL}")

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

        if not checkBoundingBoxIsCorrect(bw, bh):
            darknetString = ""

        txtName = os.path.splitext(frameMarks['image'])[0]
        with open(os.path.join(framesDir, extendName(txtName, Extensions.txt)), "w") as f:
            f.write(darknetString)

        print("\r{:.1f}% of work has been done".format((frameIdx + 1) / len(marks) * 100), end="")


def filterFolders(folders, categories, subcategories):
    if categories is not None:
        for dirSet in folders[::-1]:
            if not any(ctg in dirSet for ctg in categories):
                folders.remove(dirSet)

    if subcategories is not None:
        for dirSet in folders[::-1]:
            if not any(subctg in dirSet for subctg in subcategories):
                folders.remove(dirSet)

    return folders


def extractMarksThroughDataset(datasetPath, categories=None, subcategories=None, parallel=False, threads=16):
    # cleanOldMarks(datasetPath)
    frames = walk(datasetPath, targetDirs=const.frames).get("dirs")
    frames = filterFolders(frames, categories, subcategories)

    if parallel:
        threads = min(threads, mp.cpu_count())
    else:
        threads = 1

    threadsList = []
    with mp.Pool(threads) as pool:
        for dirsSet in frames:
            dirsSet = dirsSet[:-1]
            categoryDir = os.path.join(datasetPath, *dirsSet)

            threadsList.append(
                pool.apply_async(
                    extractMarks,
                    args=(categoryDir,)
                )
            )

        for r in threadsList:
            r.get()


def makeSets(directories, wpath=Path.sets, trainPart=0.9, validPart=0.05, ignoreOld=False, matchWithMarks=True):
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
              format(dirIdx / len(directories) * 100), end="")

        dirImages = [os.path.join(path, *img) for img in walk(path, targetExtensions=Extensions.images()).get("extensions")]
        images.extend(dirImages)

        if matchWithMarks:
            dirMarks = [os.path.join(path, *mrk) for mrk in walk(path, targetExtensions=Extensions.txt).get("extensions")]
            marks.extend(dirMarks)

    if matchWithMarks:
        transformer = lambda x: changeExtension(x, Extensions.txt)
        print("Matching images to marks, please wait...")
        images = matchLists(master=marks, slave=images, transformer=transformer)

    # _, images = matchLists(master=inUse, slave=images, getMismatched=True)

    images = permutate(images)

    start = 0
    for set_, info in sets.items():
        part = info["part"]
        end = start + int(part * len(images))

        total = end - start

        info["content"].extend(images[start:end])
        info["content"] = permutate(info["content"])
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


def makeCategoriesList(summarizedPath=Path.summarizedRaw, allowedSubCtgList=None):
    from utils import openJsonSafely, writeLines
    from verifier import getFullCategory

    summarized = openJsonSafely(summarizedPath)

    ctgList = []
    for ctg, value in summarized.items():
        if ctg == const.maxIdx:
            continue

        for subctg in value:
            if allowedSubCtgList is not None and subctg not in allowedSubCtgList:
                continue

            idx = value[subctg][const.ctgIdx]
            ctgList.append((getFullCategory(ctg, subctg), idx))

    ctgList = [ctg for ctg, _ in sorted(ctgList, key=lambda x: x[1])]
    writeLines(ctgList, Path.categories)


def cleanDirs(root, dirNamesList):
    import shutil

    folders = walk(root, targetDirs=dirNamesList).get("dirs")
    for dirSet in folders:
        path = os.path.join(root, *dirSet)
        shutil.rmtree(path, ignore_errors=True)


def main():
    from config import Sets
    from verifier import splitFullCategory

    # cleanDirs(
    #     root=Path.dataset,
    #     dirNamesList=(const.cut)
    # )
    # extractMarksThroughDataset(Path.dataset, subcategories=Sets.subcategories)
    # fullCtgs = readLines(r"E:\pretty_coins\desired_categories.names")
    # categories = set([splitFullCategory(ctg)[0] for ctg in fullCtgs])
    #
    # extractCropsThroughDataset(
    #     datasetPath=Path.dataset,
    #     extractionPath=r"D:\projects\coins\cuts",
    #     categories=categories,
    #     subcategories=(Sets.subcategories),
    #     extension=Extensions.jpg,
    #     params=[cv2.IMWRITE_JPEG_QUALITY, 100],
    #     parallel=True,
    #     threads=16
    # )

    # extractMarks(r"E:\pretty_coins\negatives")
    makeSets(
        [r"E:\pretty_coins\negatives"],
        wpath=r"E:\pretty_coins\sets\pretty_set\final",
        matchWithMarks=False,
        ignoreOld=False
     )

    # makeCategoriesList(Path.summarizedRaw, allowedSubCtgList=Sets.subcategories)

    # fullCtgs = readLines(Path.categories)
    # categories = set([splitFullCategory(ctg)[0] for ctg in fullCtgs])
    # #
    # extractMarksThroughDataset(Path.dataset, categories=categories, subcategories=(const.avers,), parallel=True)
    # #
    # frames = walk(Path.dataset, targetDirs=const.frames).get("dirs")
    # frames = filterFolders(frames, categories, (const.avers,))
    # frames = [os.path.join(Path.dataset, *f[:-1]) for f in frames]
    #
    # makeSets(
    #     directories=frames,
    #     wpath=os.path.join(Path.sets, "pretty_set", "final"),
    #     matchWithMarks=False
    # )


if __name__ == "__main__":
    main()

