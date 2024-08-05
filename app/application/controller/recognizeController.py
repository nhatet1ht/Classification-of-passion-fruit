import cv2
from datetime import datetime
import csv
import os
import time
from loguru import logger
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QElapsedTimer

from application.views.components.cameraView import CameraView
from application.views.components.detectionView import DetectionView
from application.views.screens.recognize import RecognizeWindow

from application.model.appConfig import SystemSetting

from application.config.config import RATIO_W_H, WEBCAM_RESOLUTION, RES1080P_WH

class RecognizeWindowController(RecognizeWindow):
    def __init__(self, videoModel, classifyModel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.recogTimer = QElapsedTimer()
        self.videoThread = videoModel
        self.classifyThread = classifyModel

        self.onlineStatus = False

        normalCamView = self.baseCameraView
        cameraView = CameraView(normalCamView.parent())
        cameraView.setGeometry(normalCamView.geometry())
        self.cameraView = cameraView

        detViewLane1 = DetectionView(self.camViewLane1.parent())
        detViewLane1.setGeometry(self.camViewLane1.geometry())
        self.detViewLane1 = detViewLane1

        detViewLane2 = DetectionView(self.camViewLane2.parent())
        detViewLane2.setGeometry(self.camViewLane2.geometry())
        self.detViewLane2 = detViewLane2

        # Signal and Slot initialization
        self.startButton.clicked.connect(lambda: self.onStartButtonClick())

        self.videoThread.sendImageSignal.connect(self.cameraView.setPixmap)
        self.videoThread.sendImageSignal.connect(self.classifyThread.setImage)
        self.classifyThread.croppedImageLane1Signal.connect(self.detViewLane1.setPixmap)
        self.classifyThread.croppedImageLane2Signal.connect(self.detViewLane2.setPixmap)
        self.classifyThread.lane1ResultSignal.connect(self.updateLane1Result)
        self.classifyThread.lane2ResultSignal.connect(self.updateLane2Result)

    def onStartButtonClick(self):
        if not self.onlineStatus:   # Start recognition
            self.onlineStatus = True
            self.startButton.setText("STOP")
            self.progStatus.setText("RUNNING")
            
            frameSize = WEBCAM_RESOLUTION[SystemSetting.camera_name] if SystemSetting.camera_name in WEBCAM_RESOLUTION.keys() else RES1080P_WH
            self.videoThread.setUrl(SystemSetting.camera_device, frameSize, False)
            self.classifyThread.start()

        else:   # Stop recognition
            self.onlineStatus = False
            if self.videoThread.isRunning():
                self.videoThread.stop()
            if self.classifyThread.isRunning():
                self.classifyThread.stop()

            self.startButton.setText("START")
            self.progStatus.setText("IDLE")
            time.sleep(0.5)
            self.reset()

    @pyqtSlot(int)
    def updateLane1Result(self, result):
        lane1Idx = result
        self.classifyLane1Box.setCurrentIndex(lane1Idx)

    @pyqtSlot(int)
    def updateLane2Result(self, result):
        lane2Idx = result
        self.classifyLane2Box.setCurrentIndex(lane2Idx)

    def reset(self):
        self.cameraView.clear_image()
        self.detViewLane1.clear_image()
        self.detViewLane2.clear_image()
        self.classifyLane1Box.setCurrentIndex(0)
        self.classifyLane2Box.setCurrentIndex(0)

    def showEvent(self, event):
        super().showEvent(event)
        logger.info("RECOGNIZE SCREEN >> Openning Screen...")

    def hideEvent(self, event):
        logger.info("RECOGNIZE SCREEN >> Closing Screen...")
    
        if self.videoThread.isRunning():
            self.videoThread.stop()
        if self.classifyThread.isRunning():
            self.classifyThread.stop()

        self.reset()        
        super().hideEvent(event)
