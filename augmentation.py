import os
import json
import random

import multiprocessing as mp
import cv2
import numpy as np

from colorama import Fore, Style
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

from verifier import downloadActualInfo, getFullCategory, splitFullCategory, fitCoords
from utils import extendName, makeJSONname, walk, getNested, openJsonSafely
from config import Extensions, Path, Constants as const
from augmentations_kit import customAugmentations
from filters import cartoonizeImage

def makeBoxesPretty(augBoxes):
    prettyBbs = []
    for imageBB in augBoxes:
        bb = imageBB.bounding_boxes[0]  # TODO: рассмотреть случаи, когда больше 1 рамки на фотке
        prettyBbs.append(
            fitCoords([bb.y1_int, bb.x1_int, bb.y2_int, bb.x2_int], imageBB.shape[:2])
        )

    return prettyBbs


def augmentImageRepeated(image, augmentations, repeats=1, boxes=None):
    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2) for y1, x1, y2, x2 in boxes
    ], shape=image)

    images, imagesBoxes = augmentations(images=[image for _ in range(repeats)],
                                bounding_boxes=[bbs for _ in range(repeats)])

    prettyBbs = makeBoxesPretty(imagesBoxes)

    return images if boxes is None else zip(images, prettyBbs)


def applyAugmentations(image, box, augmentations):
    augImage, augBox = augmentations(image, box)
    return augImage, augBox


def augmentCategoryWithRepeats(categoryPath, fullCategory, augmentPath, augmentations, extension=Extensions.png,
                               repeats=1, params=None):

    print(f"Category {fullCategory} is being augmented")
    if repeats == 0:
        print(f"{Fore.RED}Too many original images for {categoryPath}, aborting augmentation {Style.RESET_ALL}")
        return

    marksName = makeJSONname(const.marks)
    marksPath = os.path.join(categoryPath, marksName)
    framesPath = os.path.join(categoryPath, const.frames)

    augmentedCategoryPath = os.path.join(augmentPath, *splitFullCategory(fullCategory))

    try:
        marks = json.load(open(marksPath, "r"))
    except:
        print(f"{Fore.RED}There is no marks {marksPath} for frames in {categoryPath} {Style.RESET_ALL}")
        return

    idx = 0
    augmentedMarks = {}
    for i, name in enumerate(marks):
        print("\r{:.1f}% of work has been done".format((i + 1) / len(marks) * 100), end="")

        frameData = marks[name]
        frameName = frameData[const.image]
        box = frameData[const.coords]
        ctgIdx = frameData[const.ctgIdx]
        shape = frameData[const.imageShape]

        frameID = name.split(const.separator)[1]

        image = cv2.imread(os.path.join(framesPath, frameName))
        augmented = augmentImageRepeated(image=image, augmentations=augmentations, repeats=repeats, boxes=[box])

        augmentedFramesPath = os.path.join(augmentedCategoryPath, const.frames)
        os.makedirs(augmentedFramesPath, exist_ok=True)

        for augImage, augBox in augmented:
            augmentedName = f"{fullCategory}{const.separator}{frameID}_{idx}{const.separator}{const.augmented}"
            augmentedFileName = extendName(augmentedName, extension)
            augmentedMarks[augmentedName] = {
                const.image: augmentedFileName,
                const.coords: augBox,
                const.fullCategory: fullCategory,
                const.ctgIdx: ctgIdx,
                const.imageShape: shape
            }

            cv2.imwrite(os.path.join(augmentedFramesPath, augmentedFileName), augImage, params)
            idx += 1

    print()
    json.dump(augmentedMarks, open(os.path.join(augmentedCategoryPath, marksName), "w"), indent=3)
    print(f"{Fore.GREEN}Category {fullCategory} has been successfully augmented. "
          f"Results in {augmentedCategoryPath} {Style.RESET_ALL}")


def getTargetCount(actualInfo, targetType="median"):
    counts = []

    for ctg, info in actualInfo.items():
        for subCtg, count in info.items():
            if subCtg == const.overall:
                continue

            counts.append(count)

    if targetType == "median":
        tcount = np.median(counts)
    elif targetType == "max":
        tcount = np.max(counts)
    elif targetType == "min":
        tcount = np.min(counts)

    return tcount


def augmentDatasetWithRepeats(augmentationName, augmentations, imageExtension, repeats=1, params=None):
    actualInfo = downloadActualInfo().get(const.original, {})

    target = getTargetCount(actualInfo, targetType="max") # вообще не самый хороший выбор

    path = os.path.join(Path.dataset, const.original)
    keys = walk(path, targetDirs=const.frames).get("dirs")

    for set_ in keys:
        set_ = set_[:-1]
        count = getNested(dictionary=actualInfo, keys=set_, default=0)

        category, subcategory = set_
        categoryPath = os.path.join(path, category, subcategory)

        if count == 0:
            print(f"{Fore.RED}Update actual info for {categoryPath} {Style.RESET_ALL}")
            continue

        multiplier = int(target // count)
        ctgRepeats = repeats * multiplier

        augmentCategoryWithRepeats(
            categoryPath=categoryPath,
            fullCategory=getFullCategory(category, subcategory),
            augmentPath=os.path.join(Path.dataset, augmentationName),
            augmentations=augmentations,
            extension=imageExtension,
            repeats=ctgRepeats,
            params=params
        )


def augmentationGenerator(framesPath, marks, augmentations, number):
    keys = list(marks.keys())

    for idx in range(number):
        name = keys[random.randint(0, len(marks) - 1)]
        frameData = marks[name]

        frameName = frameData[const.image]
        fullCategory = frameData[const.fullCategory]
        box = frameData[const.coords]
        ctgIdx = frameData[const.ctgIdx]
        frameID = name.split(const.separator)[1]

        frame = cv2.imread(os.path.join(framesPath, frameName))

        augFrame, augBox = applyAugmentations(frame, box, augmentations)

        augmentedName = f"{fullCategory}{const.separator}{frameID}_{idx}{const.separator}{const.augmented}"
        augFrameData = {
            const.image: augmentedName,
            const.coords: augBox,
            const.fullCategory: fullCategory,
            const.ctgIdx: ctgIdx,
            const.imageShape: augFrame.shape[:2]
        }

        yield augFrame, augFrameData


def augmentCategoryWithGenerator(categoryPath, fullCategory, augmentPath, augmentations, augmentationsNumber,
                                 extension=Extensions.png, params=None):
    print('category: {:>50} \t process_id: {:>10} \t process_name: {}'.format(fullCategory, os.getpid(), mp.current_process()))
    time.sleep(0.5)

    augmentations = customAugmentations if augmentations is None else augmentations # хардкод для запуска мультипроцессинга
    # print(f"Category {fullCategory} is being augmented")
    if augmentationsNumber == 0:
        print(f"{Fore.RED}No augmentations for {categoryPath}{Style.RESET_ALL}")
        return

    marksName = makeJSONname(const.marks)
    marksPath = os.path.join(categoryPath, marksName)
    framesPath = os.path.join(categoryPath, const.frames)

    augmentedCategoryPath = os.path.join(augmentPath, *splitFullCategory(fullCategory))

    try:
        marks = json.load(open(marksPath, "r"))
    except:
        print(f"{Fore.RED}There is no marks {marksPath} for frames in {categoryPath} {Style.RESET_ALL}")
        return

    augGenerator = augmentationGenerator(framesPath, marks, augmentations, augmentationsNumber)

    augmentedFramesPath = os.path.join(augmentedCategoryPath, const.frames)
    os.makedirs(augmentedFramesPath, exist_ok=True)

    augmentedMarks = {}
    for i, aug in enumerate(augGenerator):
        print("\r{} {:.1f} is ready".format(fullCategory, i/augmentationsNumber*100), end="")

        augFrame, augFrameData = aug

        augmentedName = augFrameData.pop(const.image)
        augmentedFileName = extendName(augmentedName, extension)
        augFrameData[const.image] = augmentedFileName
        cv2.imwrite(os.path.join(augmentedFramesPath, augmentedFileName), augFrame, params)

        augmentedMarks[augmentedName] = augFrameData

    print()
    json.dump(augmentedMarks, open(os.path.join(augmentedCategoryPath, marksName), "w"), indent=3)
    print(f"\n{Fore.GREEN}Category {fullCategory} has been successfully augmented. "
          f"Results in {augmentedCategoryPath} {Style.RESET_ALL}")


def augmentDatasetWithGenerator(augmentationName, augmentations, imageExtension, multiplier, params=None, parallel=False):
    actualInfo = downloadActualInfo().get(const.original, {})

    target = getTargetCount(actualInfo, targetType="max") # вообще не самый хороший выбор

    path = os.path.join(Path.dataset, const.original)
    keys = walk(path, targetDirs=const.frames).get("dirs")

    nCPU = mp.cpu_count()
    cpu = 0
    processes = []
    for i in range(0, nCPU):
        processes.append([])

    for set_ in keys:
        set_ = set_[:-1]
        count = getNested(dictionary=actualInfo, keys=set_, default=0)

        category, subcategory = set_
        categoryPath = os.path.join(path, category, subcategory)

        if count == 0:
            print(f"{Fore.RED}Update actual info for {categoryPath} {Style.RESET_ALL}")
            continue

        number = int(multiplier * target) - count

        fullCategory = getFullCategory(category, subcategory)
        augmentPath = os.path.join(Path.dataset, augmentationName)

        if parallel:
            proc = mp.Process(target=augmentCategoryWithGenerator,
                           args=(categoryPath, fullCategory, augmentPath, None, number),
                           kwargs={"extension": imageExtension, "params": params})
            processes[cpu].append(proc)
            cpu = (cpu + 1) % nCPU

        else:
            augmentCategoryWithGenerator(
                categoryPath=categoryPath,
                fullCategory=fullCategory,
                augmentPath=augmentPath,
                augmentations=augmentations,
                augmentationsNumber=number,
                extension=imageExtension,
                params=params
            )

    if parallel:
        for i in range(0, len(processes[0])):
            for cpu in range(0, nCPU):
                if i == 0 or not processes[cpu][i - 1].is_alive():
                    processes[cpu][i].start()
            for cpu in range(0, nCPU):
                if i == 0 or not processes[cpu][i - 1].is_alive():
                    processes[cpu][i].join()


def main():
    pass


if __name__ == "__main__":
    main()