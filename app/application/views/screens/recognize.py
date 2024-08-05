import sys

from PyQt5.QtWidgets import QWidget, QPushButton, QLabel, QPlainTextEdit, QApplication
from PyQt5.QtGui import QPixmap, QFont, QFontDatabase, QIcon
from PyQt5.QtCore import QSize
from PyQt5 import uic

from application.views.components.baseWidget import BaseWidget

class RecognizeWindow(BaseWidget):
    def initUI(self):
        uic.loadUi('application/views/layout/recognize.ui', self)
        icon = QIcon()
        icon.addPixmap(QPixmap(
            "application/views/resources/icons/exit_green.png"), QIcon.Normal, QIcon.Off)
        self.exitButton.setIcon(icon)
        self.exitButton.setIconSize(QSize(70, 70))

        ## Set Result as readonly mode
        self.classifyLane1Box.setEnabled(False)
        self.classifyLane1Box.setStyleSheet("QComboBox { color: black;}")
        self.classifyLane2Box.setEnabled(False)
        self.classifyLane2Box.setStyleSheet("QComboBox { color: black;}")