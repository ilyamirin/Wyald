import os

import cv2


def processVideoFile(rawVideoPath, frameDir, vname):
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)

    vdir = os.path.join(frameDir, "bright_background", vname[:-4])
    if not os.path.exists(vdir):
        os.makedirs(vdir)

    cap = cv2.VideoCapture(os.path.join(rawVideoPath, vname))
    idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        cv2.imwrite(os.path.join(vdir, f'{vname[:-4]}-{idx}.png'), frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break
        idx += 1
    return


def main():
    dataDir = '.\\..\\data\\coins'
    frameDir = os.path.join(dataDir, 'frames')
    rawVideoPath = os.path.join(dataDir, 'raw_videos')

    for videoFile in os.listdir(rawVideoPath):
        processVideoFile(rawVideoPath, frameDir, videoFile)


if __name__ == "__main__":
    main()