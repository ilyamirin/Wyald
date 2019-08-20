import imageio
import imgaug as ia
from imgaug import augmenters as iaa
import cv2

def main():
    image = imageio.imread(r"E:\data\coins\sber\frames\Akhaltekinskiy-kon-2011-v1\Akhaltekinskiy-kon-2011-v1-2.png ")
    ia.seed(4)
    rotate = iaa.Affine(rotate=(-25, -25))
    image_aug = rotate.augment_image(image)
    cv2.imwrite("temp.png", image_aug)


if __name__ == "__main__":
    main()