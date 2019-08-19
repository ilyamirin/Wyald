import os

import cv2

# def selectROI(frame):
#     bbox = cv2.selectROI('Output', frame)
#     print("Press any other key to continue")
#     print('Selected bounding boxes {}'.format(bbox))
#     return bbox
lastIdx = dict()

def framingVideoFile(rootDir, frameDir, vname):
    if not os.path.exists(frameDir):
        os.makedirs(frameDir)

    vdir = os.path.join(frameDir, vname[:-4])
    if not os.path.exists(vdir):
        os.makedirs(vdir)
    else:
        return

    cap = cv2.VideoCapture(os.path.join(rootDir, vname))
    # idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        # cv2.waitKey(5)
        categoryName = f'{vname[:-7]}'
        Idx = 0
        if not categoryName in lastIdx:
            lastIdx[categoryName] = Idx
        fname = f'{vname[:-4]}-{lastIdx[categoryName]}.png'
        print(fname)
        t = os.path.join(vdir, fname)
        if not os.path.exists(t):
            cv2.imwrite(t, frame)
            lastIdx[categoryName] += 1


def main():
    rootDir = r'C:\Projects\data\sber'
    frameDir = os.path.join(rootDir, 'frames')
    videoDir = os.path.join(rootDir, 'video')

    for videoFile in os.listdir(videoDir):
        framingVideoFile(videoDir, frameDir, videoFile)

if __name__ == "__main__":
    main()