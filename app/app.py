
import os
import sys
import signal
import argparse
from loguru import logger

from PyQt5.QtWidgets import QApplication, QWidget, QStackedWidget, QHBoxLayout
from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QIcon

from application.controller.recognizeController import RecognizeWindowController
from application.views.screens.menu import MainMenu
from application.model.appConfig import SystemSetting
from application.model.fruitModel import FruitClassifyThread

MENU_WINDOW = 0
RECOGNITION_WINDOW = 1
SYSTEMSETTING_WINDOW = 2

signal.signal(signal.SIGINT, signal.SIG_DFL)

os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
os.environ['CUDA_VISIBLE_DEVICES'] = "0"

parser = argparse.ArgumentParser(description='Fruit Classification Demo')
parser.add_argument('--telicam', action='store_true', help='Use webcamera instead')
parser.add_argument('--debug', action='store_true', help='Use debug mode')
args = parser.parse_args()

if args.telicam:
    os.environ['TELICAM'] = 'True'
    from application.model.telicamModel import TeliCameraModel as VideoThread
    from application.controller.systemSettingController2 import SystemSettingController2 as SystemSettingController
else:
    from application.model.videoModel import VideoThread
    from application.controller.systemSettingController import SystemSettingController

if args.debug:
    os.environ['DEBUG'] = 'True'
else:
    logger.remove()

class FruitClassifier(QWidget):
    def __init__(self):
        super(FruitClassifier, self).__init__()
        self.setFixedSize(1280, 720)
        # self.setFixedSize(1920, 1080)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('application/views/resources/icons/ars_logo.png'))

        # Initalize models and load data
        SystemSetting.loadConfig()
        
        self.videoModel = VideoThread(self)
        self.fruitModel = FruitClassifyThread()

        # Initalize view and Controllers
        self.menuWindow = MainMenu()
        self.recognizeWindow = RecognizeWindowController(videoModel=self.videoModel, classifyModel=self.fruitModel)
        self.systemSettingWindow = SystemSettingController(videoModel=self.videoModel)

        self.windowStack = QStackedWidget(self)
        self.windowStack.addWidget(self.menuWindow)
        self.windowStack.addWidget(self.recognizeWindow)
        self.windowStack.addWidget(self.systemSettingWindow)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.windowStack)
        hbox.setContentsMargins(QMargins(0, 0, 0, 0))
        self.setLayout(hbox)

        self.menuWindow.exitButton.clicked.connect(self.close)
        self.menuWindow.recButton.clicked.connect(
            lambda: self.display(RECOGNITION_WINDOW))
        self.menuWindow.sysButton.clicked.connect(
            lambda: self.display(SYSTEMSETTING_WINDOW))

        self.recognizeWindow.exitButton.clicked.connect(
            lambda: self.display(MENU_WINDOW))
        self.systemSettingWindow.exitButton.clicked.connect(
            lambda: self.display(MENU_WINDOW))

        self.setFocus()
        logger.info("Started application")

    def display(self, i):
        self.windowStack.setCurrentIndex(i)

    def close(self) -> bool:
        logger.info("Closed application!")
        if args.telicam:
            self.videoModel.terminateCam()
        return super().close()


def main():
    app = QApplication(sys.argv)
    ex = FruitClassifier()
    ex.show()
    ex.move(200, 200)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
