import os
import json
import random

import cv2
import numpy as np

from colorama import Fore, Style
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

from verifier import downloadActualInfo, getFullCategory, splitFullCategory
from utils import extendName, makeJSONname, walk, getNested, openJsonSafely
from config import Extensions, Path, Constants as const


def augmentImage(image, augmentations, repeats=1, boxes=None):
    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2) for y1, x1, y2, x2 in boxes
    ], shape=image)

    images, imagesBoxes = augmentations(images=[image for _ in range(repeats)],
                                bounding_boxes=[bbs for _ in range(repeats)])

    prettyBbs = []
    for imageBB in imagesBoxes:
        h, w = imageBB.shape[:2]
        bb = imageBB.bounding_boxes[0] #TODO: рассмотреть случаи, когда больше 1 рамки на фотке
        prettyBbs.append(
            [max(0, bb.y1_int), max(0, bb.x1_int), min(h, bb.y2_int), min(w, bb.x2_int)]
        )

    return images if boxes is None else zip(images, prettyBbs)


def augmentCategory(categoryPath, fullCategory, augmentPath, augmentations, extension=Extensions.png, repeats=1,
                    params=None):

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
        augmented = augmentImage(image=image, augmentations=augmentations, repeats=repeats, boxes=[box])

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


def getMedianCount(actualInfo):
    counts = []

    for ctg, info in actualInfo.items():
        for subCtg, count in info.items():
            if subCtg == const.overall:
                continue

            counts.append(count)

    return np.median(counts)


def augmentDataset(augmentationName, augmentations, imageExtension, repeats=1, params=None):
    actualInfo = downloadActualInfo().get(const.original, {})

    median = getMedianCount(actualInfo)

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

        multiplier = int(median // count)
        ctgRepeats = repeats * multiplier

        augmentCategory(
            categoryPath=categoryPath,
            fullCategory=getFullCategory(category, subcategory),
            augmentPath=os.path.join(Path.dataset, augmentationName),
            augmentations=augmentations,
            extension=imageExtension,
            repeats=ctgRepeats,
            params=params
        )


def createAugmenter():
    aug = iaa.Sequential(
        [
            iaa.Sometimes(0.5, iaa.Crop(percent=(0.1, 0.3), keep_size=False)),
            iaa.Sometimes(0.5, iaa.MotionBlur(20, random.randint(0, 360))),
            iaa.Sometimes(0.5, iaa.AdditiveGaussianNoise(scale=(10, 60))),
            iaa.Sometimes(0.5, iaa.AllChannelsCLAHE(clip_limit=5)),
            iaa.Sometimes(0.5, iaa.Affine(scale={"x": (1.0, 1.35), "y": (1.0, 1.35)})),
            iaa.Affine(rotate=(0, 360))
        ], random_order=True
    )

    return aug


def main():
    pass


if __name__ == "__main__":
    main()