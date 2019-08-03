import os
import cv2
import numpy as np

def processFile(fpath):
    img = cv2.imread(fpath)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    contrast_gray = cv2.addWeighted(gray, 0.5, np.zeros(gray.shape, gray.dtype), 0, 0)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, dp=3, minDist=5, param1=100, param2=60, minRadius=50, maxRadius=150)

    circles = np.uint16(np.around(circles))
    for i in circles[0, :]:
        cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
        cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)

    cv2.imshow("src",  img)
    cv2.imshow("output", gray)

    cv2.imshow("output2", img)
    cv2.waitKey(50000)
    cv2.destroyAllWindows()

def main():
    fpath = "C:/Projects/data/coins/HandledVideos/1-ruble-avers(2)/1-ruble-avers(2).mp4-19.png"
    processFile(fpath)

if __name__ == "__main__":
    main()