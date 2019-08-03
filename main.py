import os

import cv2
import numpy as np


def detectCircleOnFrame(frame):
    output = frame.copy()
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    circles = cv2.HoughCircles(gray, cv2.HOUGH_GRADIENT, 1, 100, param1=80, param2=60)

    if circles is None:
        return

    circles = np.round(circles[0, :]).astype("int")

    for (x, y, r) in circles:
        cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

    cv2.imshow("output", output)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()


def processVideoFile(dataDir, rawVideoPath, vname):
    vdir = os.path.join(dataDir, "HandledVideos", vname[:-4])
    if not os.path.exists(vdir):
        os.makedirs(vdir)

    cap = cv2.VideoCapture(os.path.join(rawVideoPath, vname))
    idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        detectCircleOnFrame(frame)

        cv2.imwrite(os.path.join(vdir, f'{vname[:-4]}-{idx}.png'), frame)

        idx += 1
        break


def main():
    dataDir = '.\\..\\data\\coins'
    rawVideoPath = os.path.join(dataDir, 'RawVideos')

    for videoFile in os.listdir(rawVideoPath):
        processVideoFile(dataDir, rawVideoPath, videoFile)


if __name__ == "__main__":
    main()