import sys

"""
 (C) Copyright 2023 ARS Group (Advanced Research & Solutions)
"""

import os
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QPoint, pyqtSlot
from PyQt5 import uic

from application.utils import utils

regionMessageDialogStr = utils.getStr('regionMessageDialog')
cancelStr = utils.getStr('cancel')

class ConfirmationDialog(QDialog):
    def __init__(self, logType, title, message, parent=None):
        super(ConfirmationDialog, self).__init__(parent)
        uic.loadUi("application/views/layout/confirmation_dialog.ui", self)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(250, 450, self.width(), self.height())
        self.buttonBox.button(QDialogButtonBox.Cancel).setText(cancelStr)
        self.buttonBox.button(QDialogButtonBox.Ok).setText("OK")

        self.showLogMessage(logType, title, message)
        self.buttonBox.accepted.connect(self.onOKClick)
        self.buttonBox.rejected.connect(self.onCancelClick)

    def showLogMessage(self, logType, title, message):
        # Set title
        self.titleMessage.setText(title)

        # Set image icon
        if logType == "INFO":
            iconPath = "application/views/resources/icons/info_icon.jpg"
        elif logType == "WARN":
            iconPath = "application/views/resources/icons/warning_icon.png"
        else:
            iconPath = "application/views/resources/icons/error_icon.png"
        pixmap = QPixmap(iconPath)
        self.logIcon.setPixmap(pixmap.scaled(self.logIcon.size(), Qt.KeepAspectRatio))

        # Set message text
        self.messageLogTextEdit.insertPlainText(message)

    @pyqtSlot()
    def onOKClick(self):
        self.accept()

    @pyqtSlot()
    def onCancelClick(self):
        self.reject()
