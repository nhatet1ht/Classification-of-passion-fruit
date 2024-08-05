import sys

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QFontDatabase, QPixmap
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5 import uic

from application.utils import utils
from application.config import config

titleStr = utils.getStr('title')
fruitClassificationStr = utils.getStr('fruitClassificationTitle')
systemSettingStr = utils.getStr('systemSettingTitle')
exitStr = utils.getStr('exit')


class MainMenu(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.setWindowTitle(' ')
        uic.loadUi('application/views/layout/menu.ui', self)
        #self.exitButton.setText(exitStr)
        icon = QIcon()
        icon.addPixmap(QPixmap(
            "application/views/resources/icons/exit_green.png"), QIcon.Normal, QIcon.Off)
        self.exitButton.setIcon(icon)
        self.exitButton.setIconSize(QSize(70, 70))

        self.recLabel.setObjectName('mainButtonLabel')
        #self.recLabel.setText(fruitClassificationStr)
        self.sysLabel.setObjectName('mainButtonLabel')
        #self.sysLabel.setText(systemSettingStr)

        # Set the version information
        self.versionInfo.setText("Version " + config.VERSION_INFO)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Q:
            self.close()


def main():
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(config.FONT_PATH)
    app.setStyle('Windows')
    with open(config.STYLE_PATH, 'r', encoding="utf-8") as f:
        qss = f.read()
        app.setStyleSheet(qss)
    ex = MainMenu()
    ex.move(0, 0)
    ex.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
