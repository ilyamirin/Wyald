import random
from imgaug import augmenters as iaa
from imgaug.augmentables.bbs import BoundingBox, BoundingBoxesOnImage

from verifier import fitCoords
from filters import cartoonizeImage


aug = iaa.Sequential(
        [
            iaa.Sometimes(0.5, iaa.Crop(percent=(0.1, 0.3), keep_size=False)),
            iaa.Sometimes(0.5, iaa.MotionBlur(15, random.randint(0, 360))),
            iaa.OneOf([
                iaa.AllChannelsCLAHE(clip_limit=10),
                iaa.AdditiveGaussianNoise(scale=(10, 35)),
                iaa.FastSnowyLandscape(lightness_threshold=(50, 115), from_colorspace="BGR")
            ]),
            # iaa.Sometimes(0.25, iaa.Affine(scale={"x": (1.0, 1.2), "y": (1.0, 1.2)})),
            iaa.Sometimes(0.25, iaa.Multiply((0.85, 1.15))),
            iaa.Sometimes(0.25, iaa.ContrastNormalization((0.85, 1.15))),
            # iaa.Affine(rotate=(0, 360))
        ], random_order=False
    )


def customAugmentations(image, box):
    y1, x1, y2, x2 = box
    bb = BoundingBox(x1=x1, x2=x2, y1=y1, y2=y2)

    augImage, augBox = aug(image=image, bounding_boxes=bb)
    augBox = fitCoords([augBox.y1_int, augBox.x1_int, augBox.y2_int, augBox.x2_int], augImage.shape[:2])

    return augImage, augBox


def cartoonAugs(image, box):
    image = cartoonizeImage(image)
    return image, box