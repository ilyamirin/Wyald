import os
import random
import imageio
import imgaug as ia
from imgaug import augmenters as iaa
import json
import cv2
from colorama import Fore, Style
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

from verifier import downloadActualInfo, actualizeInfoWithFrames
from utils import extendName, makeJSONname, walk
from config import Extensions, Path, Constants as const


def augmentImage(image, augmentations, repeats=1, boxes=None):
    bbs = BoundingBoxesOnImage([
        BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2) for y1, x1, y2, x2 in boxes
    ], shape=image)

    images, bbs = augmentations(images=[image for _ in range(repeats)],
                                bounding_boxes=[bbs for _ in range(repeats)])

    return images if boxes is None else (images, bbs)


def augmentCategory(categoryPath, augmentPath, augmentations, extension=Extensions.png, repeats=1, params=None):
    marksName = makeJSONname(const.marks)
    marksPath = os.path.join(categoryPath, marksName)
    framesPath = os.path.join(categoryPath, const.frames)

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
        fullCategory = frameData[const.fullCategory]
        ctgIdx = frameData[const.ctgIdx]
        shape = frameData[const.imageShape]

        frameID = name.split(const.separator)[1]

        image = cv2.imread(os.path.join(framesPath, frameName))
        augmented = augmentImage(image=image, augmentations=augmentations, repeats=repeats, boxes=[box])

        category, subcategory = fullCategory.split("_")
        augmentedCategoryPath = os.path.join(augmentPath, category, subcategory)

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


def saveAugmentedImages(imgDsrDir, fname, category, images_aug, bbs, Idx=0):
    print(f"Start augmentation of image {fname} \n Location: {imgDsrDir}-aug \t Category: {category} ")

    for img in images_aug:
         Idx += 1
         # ia.imshow(img)

         augDir = f"{imgDsrDir}-aug"
         if not os.path.exists(augDir):
             os.mkdir(augDir)
             print(f"Directory {augDir} was create")

         imgPath = os.path.join(augDir, f'aug-{Idx}-{fname}')
         cv2.imwrite(imgPath, img)
         print(f"{Fore.GREEN} Augmented image {imgPath} was created")



def videoAug(path, ToShow=False):
    cap = cv2.VideoCapture(path)
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # hsv = cv2.cvtColor(frame, cv2.COLOR_BGR_VNG)
        m_img = cv2.medianBlur(frame, 5)
        # cimg = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        ret, th1 = cv2.threshold(m_img, 120, 255, cv2.CAP_PROP_INTELPERC_DEPTH_CONFIDENCE_THRESHOLD)
        # timg = cv2.inpaint(m_img, th1, 3, cv2.INPAINT_NS)

        cv2.imshow(f"{path}", th1)
        cv2.waitKey(5)


def main():
    # image = imageio.imread(r"D:\Projects\coins-project\data\sber\pretty_names\video\Tigrenok_2010-v1.MOV")
    # ia.seed(4)
    # rotate = iaa.Affine(rotate=(-25, -25))
    # image_aug = rotate.augment_image(image)
    # cv2.imwrite("temp.png", image_aug)
    path = r"D:\Projects\coins-project\data\sber\video\viktor_tsoy_2012_v2.MOV"
    videoAug(path, ToShow=True)


if __name__ == "__main__":
    main()