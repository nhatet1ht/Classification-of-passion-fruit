import numpy as np
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from application.utils.utils import rgbToPixmap


class CameraSettingView(QWidget):
    def __init__(self, *args, **kwargs):
        super(CameraSettingView, self).__init__(*args, **kwargs)
        self._painter = QPainter()
        self.image = None
        self.pixmap = None

    @pyqtSlot(np.ndarray)
    def setPixmap(self, image):
        self.image = image
        self.pixmap = rgbToPixmap(image, self.geometry().size())
        self.update()

    def paintEvent(self, event):
        if not self.pixmap:
            return super(CameraSettingView, self).paintEvent(event)
        painter = self._painter
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)
        painter.drawPixmap(self.rect(), self.pixmap)
        painter.end()

    def clear_image(self):
        self.image = None
        blackImage = np.ones(
            (self.geometry().width(), self.geometry().height(), 3), np.uint8) * 255
        self.pixmap = rgbToPixmap(blackImage, self.geometry().size())
        self.update()