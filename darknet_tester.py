import os
from io import BytesIO
import numpy as np
import sys

import cv2
from PIL import Image

from Renderers.OpenCVRenderer import drawBoxes


class Config:
    DARKNET_PATH = ""
    CONFIG_PATH = ""

    config_path = os.path.join(CONFIG_PATH, "yolov3.cfg")
    meta_path = os.path.join(CONFIG_PATH, "coins.data")
    weight_path = os.path.join(CONFIG_PATH, "yolov3_best.weights")


def area(box):
    return abs(box[2] - box[0]) * abs(box[3] - box[1])


def sorted_faces(faces, boxes, n=5):
    idxs = np.array([i for (b, i) in sorted([(area(b), i) for i, b in enumerate(boxes)], reverse=True)[:n]])
    return np.array(faces)[idxs], np.array(boxes)[idxs]


def get_image_data_from_bytes_data(bytes_data):
    image_bytes_data = bytes_data[13:]
    image_bytes_data = BytesIO(image_bytes_data)
    img = Image.open(image_bytes_data)
    img_data = np.array(img)
    timestamp = float(bytes_data[:13]) / 1000
    return timestamp, img_data


class CoinRecognition:
    def __init__(self, augmentation=None, *args, **kwargs):
        print("coin worker created", flush=True)
        sys.path.append(Config.DARKNET_PATH)
        import darknet
        sys.path.pop()
        self.dn = darknet

        self.net_main = darknet.load_net_custom(Config.config_path.encode("ascii"), Config.weight_path.encode("ascii"), 0, 1)
        self.meta_main = darknet.load_meta(Config.meta_path.encode("ascii"))
        with open(Config.meta_path) as metaFH:
            meta_contents = metaFH.read()
            import re
            match = re.search("names *= *(.*)$", meta_contents, re.IGNORECASE | re.MULTILINE)
            result = match.group(1) if match else None
            if os.path.exists(result):
                with open(result) as namesFH:
                    names_list = namesFH.read().strip().split("\n")
                    self.alt_names = [x.strip() for x in names_list]

        print(f"({self.dn.network_width(self.net_main)} {self.dn.network_height(self.net_main)}")
        self.darknet_image = darknet.make_image(darknet.network_width(self.net_main), darknet.network_height(self.net_main), 3)

        self.augmentation = augmentation if augmentation is not None else lambda x: x


    def recognizeImageTensor(self, tensor):
        try:
            frame_rgb = cv2.cvtColor(tensor, cv2.COLOR_BGR2RGB)
            frame_resized = cv2.resize(frame_rgb,
                                       (self.dn.network_width(self.net_main),
                                        self.dn.network_height(self.net_main)),
                                       interpolation=cv2.INTER_LINEAR)

            frame_augmented = self.augmentation(frame_resized)

            print((self.dn.network_width(self.net_main),
                   self.dn.network_height(self.net_main)))

            self.dn.copy_image_from_bytes(self.darknet_image, frame_augmented.tobytes())

            detections = self.dn.detect_image(self.net_main, self.meta_main, self.darknet_image, thresh=0.3)

            kx = frame_rgb.shape[1] / self.dn.network_width(self.net_main)
            ky = frame_rgb.shape[0] / self.dn.network_height(self.net_main)

            results = {
                "boxes": [],
                "texts": []
            }
            for label, confidence, (xc, yc, width, height) in detections:
                label = label.decode()

                xc *= kx
                yc *= ky
                width *= kx
                height *= ky

                box = [
                    yc - height / 2,
                    xc - width / 2,
                    yc + height / 2,
                    xc + width / 2
                ]

                results["boxes"].append(box)
                results["texts"].append("{} {:.1f}".format(label, confidence))

            tensor = drawBoxes(tensor, boxes=results["boxes"], text=results["texts"])

        except Exception as e:
            print(e)

        finally:
            return tensor


    def recognizeWebcam(self, webcamID=0):
        captureSize = (640, 480)

        stream = cv2.VideoCapture(webcamID)

        stream.set(cv2.CAP_PROP_FRAME_WIDTH, captureSize[0])
        stream.set(cv2.CAP_PROP_FRAME_HEIGHT, captureSize[1])

        frameIdx = 0
        while True:
            grabbed, frame = stream.read()
            if not grabbed:
                break

            frame = self.recognizeImageTensor(frame)

            assert captureSize == frame.shape[:-1][::-1]

            cv2.namedWindow("coins", cv2.WINDOW_NORMAL)
            cv2.imshow("coins", frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


def main():
    recognizer = CoinRecognition()
    recognizer.recognizeWebcam(0)


if __name__ == "__main__":
    main()