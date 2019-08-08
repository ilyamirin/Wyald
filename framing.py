import os

import cv2

def selectROI(frame):
    bbox = cv2.selectROI('Output', frame)
    print("Press any other key to continue")
    print('Selected bounding boxes {}'.format(bbox))
    return bbox


def framingVideoFile(rawVideoPath, frameDir, vname):
    markedDir = os.path.join(frameDir, "marked")

    if not os.path.exists(markedDir):
        os.makedirs(markedDir)

    vdir = os.path.join(markedDir, vname[:-4])
    if not os.path.exists(vdir):
        os.makedirs(vdir)

    fout = open(os.path.join(vdir, f"training.xml"), "w")
    fout.write("<?xml version='1.0' ?>\n<dataset>\n<images>")

    cap = cv2.VideoCapture(os.path.join(rawVideoPath, vname))
    idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Output', frame)

        fname = f'{vname[:-4]}-{idx}.png'

        key = cv2.waitKey(30)
        if key == 32 or key == 13: # enter or space pressed
            bbox = selectROI(frame)
            if bbox[0] != 0: # id bbox is not empty
                print(f"{fname} : {bbox}")
                fout.write(f"<image file='{fname}'>\n\t<box top='{bbox[1]}' left='{bbox[0]}' width='{bbox[2]}' height='{bbox[3]}'/></image>\n")
                cv2.imwrite(os.path.join(vdir, fname), frame)
        idx += 1

    fout.write("</images>\n</dataset>")
    fout.close()
    return


def main():
    dataDir = '.\\..\\data\\coins'
    frameDir = os.path.join(dataDir, 'frames')
    rawVideoPath = os.path.join(dataDir, 'raw_videos')

    for videoFile in os.listdir(rawVideoPath):
        framingVideoFile(rawVideoPath, frameDir, videoFile)

if __name__ == "__main__":
    main()