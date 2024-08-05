import numpy as np
import cv2

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QPainter

from application.utils.utils import rgbToPixmap, resizeAspectRatio

class CameraView(QWidget):
    def __init__(self, *args, **kwargs):
        super(CameraView, self).__init__(*args, **kwargs)
        self._painter = QPainter()
        self.image = None
        self.pixmap = None
        self.lastFrame = False

    @pyqtSlot(np.ndarray)
    def setPixmap(self, image):
        if self.lastFrame:
            return
        self.image = image
        #image = resizeAspectRatio(image, 640)
        self.pixmap = rgbToPixmap(self.image, self.geometry().size())
        self.update()

    def paintEvent(self, event):
        if not self.pixmap:
            return super(CameraView, self).paintEvent(event)
        painter = self._painter
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(self.rect(), self.pixmap)
        painter.end()

    @pyqtSlot(np.ndarray)
    def clear_image(self):
        self.image = None
        blackImage = np.ones(
            (self.geometry().width(), self.geometry().height(), 3), np.uint8) * 185
        self.pixmap = rgbToPixmap(blackImage, self.geometry().size())
        self.update()
