from typing import List

from PyQt5.QtCore import QThread, pyqtSlot
from PyQt5.QtWidgets import QWidget, QMessageBox


class BaseWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.threads: List[QThread] = []
        self.initUI()
        self.initThreads()

    def initUI(self):
        pass

    def initThreads(self):
        pass

    def startAllThreads(self):
        for thread in self.threads:
            thread.start()

    def stopAllThreads(self):
        for thread in self.threads:
            thread.stop()
        while True:
            status = 0
            for thread in self.threads:
                status += thread.isRunning()
            if status == 0:
                break

    @pyqtSlot(str)
    def showInfoMessage(self, text):
        infMsg = QMessageBox(self)
        infMsg.setIcon(QMessageBox.Information)
        infMsg.setText(text)
        infMsg.show()

    @pyqtSlot(str)
    def showErrorMessage(self, text):
        errMsg = QMessageBox(self)
        errMsg.setIcon(QMessageBox.Critical)
        errMsg.setText(text)
        errMsg.show()
