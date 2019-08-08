import sys
import os

import cv2
from random import randint

trackerTypes = ['BOOSTING', 'MIL', 'KCF', 'TLD', 'MEDIANFLOW', 'GOTURN', 'MOSSE', 'CSRT']


def createTrackerByName(trackerType):
    # Create a tracker based on tracker name
    if trackerType == trackerTypes[0]:
        tracker = cv2.TrackerBoosting_create()
    elif trackerType == trackerTypes[1]:
        tracker = cv2.TrackerMIL_create()
    elif trackerType == trackerTypes[2]:
        tracker = cv2.TrackerKCF_create()
    elif trackerType == trackerTypes[3]:
        tracker = cv2.TrackerTLD_create()
    elif trackerType == trackerTypes[4]:
        tracker = cv2.TrackerMedianFlow_create()
    elif trackerType == trackerTypes[5]:
        tracker = cv2.TrackerGOTURN_create()
    elif trackerType == trackerTypes[6]:
        tracker = cv2.TrackerMOSSE_create()
    elif trackerType == trackerTypes[7]:
        tracker = cv2.TrackerCSRT_create()
    else:
        tracker = None
        print('Incorrect tracker name')
        print('Available trackers are:')
        for t in trackerTypes:
            print(t)

    return tracker


def selectROI(frame):
    bboxes = []
    colors = []
    # while True:
    bbox = cv2.selectROI('MultiTracker', frame)
    bboxes.append(bbox)
    #colors.append((randint(0, 255), randint(0, 255), randint(0, 255)))
    print("Press q to quit selecting boxes and start tracking")
    print("Press any other key to select next object")
        # k = cv2.waitKey(0) & 0xFF
        # if (k == 113):  # q is pressed
        #     break
    print('Selected bounding boxes {}'.format(bbox))
    return bbox, colors


def processVideo(vcap, colors, tracker):
    # Process video and track objects
    while vcap.isOpened():
        success, frame = vcap.read()
        if not success:
            break

        # get updated location of objects in subsequent frames
        success, boxes = tracker.update(frame)

        # draw tracked objects
        for i, newbox in enumerate(boxes):
            p1 = (int(newbox[0]), int(newbox[1]))
            p2 = (int(newbox[0] + newbox[2]), int(newbox[1] + newbox[3]))
            cv2.rectangle(frame, p1, p2, colors, 2, 1)

        # show frame
        cv2.imshow('MultiTracker', frame)

        # quit on ESC button
        if cv2.waitKey(1) & 0xFF == 27:  # Esc pressed
            break


def main():
    dir = r"C:\Projects\coins\data\coins\raw_videos"
    videoPaths = []
    for vfile in os.listdir(dir):
        videoPaths.append(os.path.join(dir, vfile))

    for videoPath in videoPaths:
        cap = cv2.VideoCapture(videoPath)
        success, frame = cap.read()
        if not success:
            print('Failed to read video')
            sys.exit(1)

        print("Select ROI")
        bboxes, colors = selectROI(frame)
        trackerType = 'KCF'
        multiTracker = cv2.MultiTracker_create()
        for bbox in bboxes:
            multiTracker.add(createTrackerByName(trackerType), frame, bbox)

        processVideo(cap, colors, multiTracker)

# import numpy as np
#
# frame = np.random.randint(0, 255, (224, 224, 4))
#
# multiTracker = cv2.MultiTracker_create()
# multiTracker.add(createTrackerByName('CSRT'), frame, (100, 100, 120, 120))

if __name__ == "__main__":
    main()