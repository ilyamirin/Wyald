import cv2


def cartoonizeImage(image):
    blured = cv2.bilateralFilter(image.copy(), 1, 75, 75)

    hls = cv2.cvtColor(blured, cv2.COLOR_BGR2HLS_FULL)
    h, l, s = cv2.split(hls)

    yuv = cv2.cvtColor(blured, cv2.COLOR_BGR2YUV)
    y, u, v = cv2.split(yuv)

    y = cv2.adaptiveThreshold(y, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.ADAPTIVE_THRESH_MEAN_C, 3, 1)

    return cv2.merge((y, l, s))