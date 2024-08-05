import cv2
import numpy as np
import torch
import sys
import argparse
from collections import deque

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from application.config import config
from application.utils import utils
#from engines.detector.detetor import 
#from engines.fruit_classifier.classifier import FruitQualityClassifier
#from aiplatform.ioutils.visualization import draw_boxed_text


class FruitClassify(object):
    def __init__(self):
        device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
        # self.detector = Detector(device=torch.device(device))
        # self.tracker = EuclideanDistTracker(frame_size=(1536, 2048))
        # self.classifier = FruitQualityClassifier(device=device, model_path='engines/weights/05-31-resnet_torchvision-best.pth')
        
    def dettrack(self, img):
        # Assume 1 lane 1 object
        lane1FruitObj = []
        lane2FruitObj = []

        '''
        pred, img_info = self.detector.detect(img0=img)

        bboxes = pred[..., :4].tolist()
        cls_conf = pred[..., 4].tolist()
        cls_ids = pred[..., 5].tolist()
        bboxes = [[x1,y1,x2,y2] for (x1,y1,x2,y2) in bboxes if (x2-x1) < 1.5*(y2-y1) and (y2-y1) < 1.5*(x2-x1)]

        bboxes = self.tracker.update(bboxes, distance_threshold=300)

        lane1Boxes = []
        lane1Ids = []
        lane2Boxes = []
        lane2Ids = []

        if len(bboxes) > 0:
            for bbox in bboxes:
                x1, y1, x2, y2, id = bbox
                if (x2 - x1 / 2) < img_info["width"] / 2:
                    lane1Boxes.append((x1, y1, x2, y2))
                    lane1Ids.append(id)
                    lane1FruitObj = bbox
                else:
                    lane2Boxes.append((x1, y1, x2, y2))
                    lane2Ids.append(id)
                    lane2FruitObj = bbox 
        '''
        return lane1FruitObj, lane2FruitObj
    
    def classify(self, image):
        result = None
        confidence = 0
        '''
        result, confidence = self.classifier.classify(image)
        '''
        return result, confidence

class FruitClassifyThread(QThread):
    croppedImageLane1Signal = pyqtSignal(np.ndarray)
    croppedImageLane2Signal = pyqtSignal(np.ndarray)
    lane1ResultSignal = pyqtSignal(int)
    lane2ResultSignal = pyqtSignal(int)
    
    def __init__(self):
        super(FruitClassifyThread, self).__init__()
        self.fruit = FruitClassify()
        self.threadActive = False

        self.image = None
        self.inputImageQueue = deque(maxlen=1)
    
    @pyqtSlot(np.ndarray)
    def setImage(self, image):
        self.inputImageQueue.appendleft(image)

    def run(self):
        self.threadActive = True
        obj_lane1_id = -1
        obj_lane2_id = -1
        no_frame = 0
        while self.threadActive:
            if len(self.inputImageQueue) == 0:
                self.msleep(30)
                continue

            self.image = self.inputImageQueue.pop()
            
            no_frame += 1

            orgImg = self.image.copy()
            # 1. Detect and tracking
            lane1FruitObj, lane2FruitObj = self.fruit.dettrack(orgImg)
            
            # 2. Classify lane 1
            ######################### pseudo code
            dispImg = None
            if len(lane1FruitObj) > 0 or len(lane2FruitObj) > 0:
                dispImg = orgImg.copy()

            if len(lane1FruitObj) > 0:
                # 2.1. Crop the fruit object to display
                x1, y1, x2, y2, id = lane1FruitObj
                fruitImg = orgImg[int(y1):int(y2),int(x1):int(x2)]

                # 2.2. Classify the fruit object
                clsRstF1, scoreF1 = self.fruit.classify(image=fruitImg)

                # 2.3. Compute and send the final result
                finalRst1 = 'A' # Example
                self.lane1ResultSignal.emit(config.CLASSNAMES.index(finalRst1))

                dispImg = cv2.rectangle(dispImg, (int(x1),int(y1)), (int(x2),int(y2)), color=(0,255,0), thickness=2)
                dispImg = cv2.putText(dispImg, "id={id} - type={finalRst1}",  (x1, y1), font=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=2)

                lane1Img_resized = utils.resizeAspectRatio(dispImg, 320)
                self.croppedImageLane1Signal.emit(lane1Img_resized)

            # 3. Classify lane 2
            ######################### pseudo code
            if len(lane2FruitObj) > 0:
                # 2.1. Crop the fruit object to display
                x1, y1, x2, y2, id2 = lane2FruitObj
                fruitImg = orgImg[int(y1):int(y2),int(x1):int(x2)]

                # 2.2. Classify the fruit object
                clsRstF2, scoreF2 = self.fruit.classify(image=fruitImg)

                # 2.3. Compute and send the final result
                finalRst2 = 'VIP' # Example
                self.lane2ResultSignal.emit(config.CLASSNAMES.index(finalRst2))

                dispImg = cv2.rectangle(dispImg, (int(x1),int(y1)), (int(x2),int(y2)), color=(0,255,0), thickness=2)
                dispImg = cv2.putText(dispImg, "id={id2} - type={finalRst2}",  (x1, y1), font=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(0, 255, 0), thickness=2)
                lane2Img_resized = utils.resizeAspectRatio(dispImg, 320)
                self.croppedImageLane2Signal.emit(lane2Img_resized)

            ## For Debug
            # if dispImg is not None:
            #     cv2.imwrite(f"debug/{no_frame}.jpg", dispImg)

    def stop(self):
        self.threadActive = False
        self.wait()
