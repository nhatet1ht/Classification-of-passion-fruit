import numpy as np
import time
from PyQt5.QtWidgets import QWidget, QLabel, QToolTip
from PyQt5.QtCore import pyqtSignal, pyqtSlot, QPoint, Qt, QRect
from PyQt5.QtGui import QPixmap, QPainter, QPolygon

from application.utils.utils import rgbToPixmap


class DetectionView(QWidget):
    clickedSignal = pyqtSignal(int)

    def __init__(self, *args, **kwargs):
        super(DetectionView, self).__init__(*args, **kwargs)
        self._painter = QPainter()
        self.image = None
        self.pixmap = None
        self.resultOCR = None

    @pyqtSlot(np.ndarray)
    def setPixmap(self, image):
        self.image = image
        self.pixmap = rgbToPixmap(image, self.geometry().size())
        self.update()

    def paintEvent(self, event):
        if not self.pixmap:
            return super(DetectionView, self).paintEvent(event)
        painter = self._painter
        painter.begin(self)
        painter.drawPixmap(self.rect(), self.pixmap)
        painter.end()

    def clear_image(self):
        self.image = None
        blackImage = np.ones(
            (self.geometry().width(), self.geometry().height(), 3), np.uint8) * 255
        self.pixmap = QPixmap('application/views/resources/images/thumbnail.jpg')
        self.update()
