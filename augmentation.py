import os
import json

import cv2
import numpy as np

from colorama import Fore, Style
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

from verifier import downloadActualInfo, getFullCategory
from utils import extendName, makeJSONname, walk, getNested
from config import Extensions, Path, Constants as const


def augmentImage(image, augmentations, repeats=1, boxes=None):
    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2) for y1, x1, y2, x2 in boxes
    ], shape=image)

    images, bbs = augmentations(images=[image for _ in range(repeats)],
                                bounding_boxes=[bbs for _ in range(repeats)])

    return images if boxes is None else (images, bbs)


def augmentCategory(categoryPath, fullCategory, augmentPath, augmentations, extension=Extensions.png, repeats=1,
                    params=None):

    if repeats == 0:
        return

    marksName = makeJSONname(const.marks)
    marksPath = os.path.join(categoryPath, marksName)
    framesPath = os.path.join(categoryPath, const.frames)

    augmentedCategoryPath = os.path.join(augmentPath, *fullCategory.split("_"))

    try:
        marks = json.load(open(marksPath, "r"))
    except:
        print(f"{Fore.RED} There is no marks {marksPath} for frames in {categoryPath} {Style.RESET_ALL}")
        return

    idx = 0
    augmentedMarks = {}
    for name, frameData in marks.items():
        frameName = frameData[const.image]
        box = frameData[const.coords]
        ctgIdx = frameData[const.ctgIdx]
        shape = frameData[const.imageShape]

        frameID = name.split(const.separator)[1]

        image = cv2.imread(os.path.join(framesPath, frameName))
        augmented = augmentImage(image=image, augmentations=augmentations, repeats=repeats, boxes=[box])

        augmentedFramesPath = os.path.join(augmentedCategoryPath, const.frames)
        os.makedirs(augmentedFramesPath, exist_ok=True)

        for image, boxes in augmented:
            augmentedName = f"{fullCategory}{const.separator}{frameID}_{idx}{const.separator}{const.augmented}"
            augmentedFileName = extendName(augmentedName, extension)
            augmentedMarks[augmentedName] = {
                const.image: augmentedFileName,
                const.coords: boxes[0],
                const.fullCategory: fullCategory,
                const.ctgIdx: ctgIdx,
                const.imageShape: shape
            }

            cv2.imwrite(os.path.join(augmentedFramesPath, augmentedFileName), image, params)
            idx += 1

    json.dump(augmentedMarks, open(os.path.join(augmentedCategoryPath, marksName)), indent=3)
    print(f"{Fore.GREEN} Category {fullCategory} has been successfully augmented. "
          f"Reults in {augmentedCategoryPath} {Style.RESET_ALL}")


def getMedianCount(actualInfo):
    counts = []

    for ctg, info in actualInfo.items():
        for subCtg, count in info.items():
            if subCtg == const.overall:
                continue

            counts.append(count)

    return np.median(counts)


def augmentDataset(augmentationName, augmentations, imageExtension, params=None):
    actualInfo = downloadActualInfo().get(const.original, {})

    median = getMedianCount(actualInfo)

    path = os.path.join(Path.dataset, const.original)
    keys = walk(path, targetDirs=const.frames)

    for set_ in keys:
        set_ = set_[:-1]
        count = getNested(actualInfo, set_, 0)

        category, subcategory = set_
        categoryPath = os.path.join(path, category, subcategory)

        if count == 0:
            print(f"{Fore.RED} Update actual info for {categoryPath} {Style.RESET_ALL}")
            continue

        repeats = median // count

        augmentCategory(
            categoryPath=categoryPath,
            fullCategory=getFullCategory(category, subcategory),
            augmentPath=os.path.join(Path.dataset, augmentationName),
            augmentations=augmentations,
            extension=imageExtension,
            repeats=repeats,
            params=params
        )


def main():
    pass


if __name__ == "__main__":
    main()