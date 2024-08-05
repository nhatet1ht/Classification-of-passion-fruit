import os
import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtGui import QPixmap, QFontDatabase, QIcon
from PyQt5.QtCore import QSize
from PyQt5 import uic

from application.views.components.baseWidget import BaseWidget
from application.config import config
from application.utils import utils
from application.config.config import FOCUS_ABS_MAX, FOCUS_ABS_MIN, EXPOSURE_ABS_MAX, EXPOSURE_ABS_MIN, WB_TEMPERATURE_MAX, WB_TEMPERATURE_MIN
from application.config.config import TELI_GAIN_MIN, TELI_GAIN_MAX, TELI_EXPOSURE_TIME_MIN, TELI_EXPOSURE_TIME_MAX, TELI_BLACK_LEVEL_MIN, TELI_BLACK_LEVEL_MAX, TELI_GAMMA_MIN, TELI_GAMMA_MAX, TELI_FRAME_RATE_MIN, TELI_FRAME_RATE_MAX

cameraSettingStr = utils.getStr('cameraSetting')
simulatorSettingStr = utils.getStr('simulatorSetting')

resetStr = utils.getStr('reset')
settingStr = utils.getStr('setting')
updateStr = utils.getStr('update')
autoStr = utils.getStr('automatic')
focusStr = utils.getStr('focus')
exposureStr = utils.getStr('exposure')
whiteBalanceStr = utils.getStr('whiteBalance')
exitStr = utils.getStr('exit')
canvasSize = utils.getStr('canvasSize')
textThreshold = utils.getStr('textThreshold')
lowText = utils.getStr('lowText')
linkThreshold = utils.getStr('linkThreshold')
language = utils.getStr('language')
focusValueStr = utils.getStr('absoluteFocus')
exposureValueStr = utils.getStr('absoluteExposure')
wbValueStr = utils.getStr('wbTemperature')
cameraNameStr = utils.getStr('cameraName')
paragraphStr = utils.getStr('paragraph')
recogSettingStr = utils.getStr('recogSetting')
confSettingStr = utils.getStr('confSetting')
minTextSizeStr = utils.getStr('minTextSize')
lowConfLblStr = utils.getStr('low')
medConfLblStr = utils.getStr('medium')
highConfLblStr = utils.getStr('high')
lessThanLblStr = utils.getStr('lessThan')
orMoreLblStr = utils.getStr('orMore')

teliGainStr = utils.getStr('teliGain')
teliGainValueStr = utils.getStr('teliGainValue')
teliExposureStr = utils.getStr('teliExposure')
teliExposureTimeStr = utils.getStr('teliExposureTime')
teliWhiteBalanceStr = utils.getStr('teliWhiteBalance')
teliBlackLevelStr = utils.getStr('teliBlackLevel')
teliGammaStr = utils.getStr('teliGamma')
teliGammaValueStr = utils.getStr('teliGammaValue')

class SystemSettingWindow(BaseWidget):
    def initUI(self):
        uic.loadUi('application/views/layout/system_setting.ui', self)
        self.exitButton.setText(exitStr)
        icon = QIcon()
        icon.addPixmap(QPixmap(
            "application/views/resources/icons/exit_green.png"), QIcon.Normal, QIcon.Off)

        self.exitButton.setIcon(icon)
        self.exitButton.setIconSize(QSize(70, 70))
        self.systemSettingTab.setTabText(0, cameraSettingStr)
        self.systemSettingTab.setTabText(1, simulatorSettingStr)

        self.cameraNameLabel.setText(cameraNameStr)
        self.autoLabel.setText(autoStr)
        
        if not os.environ.get('TELICAM'):
            self.focusLabel.setText(focusStr)
            self.focusSlider.setMaximum(FOCUS_ABS_MAX)
            self.focusSlider.setMinimum(FOCUS_ABS_MIN)
            self.exposureLabel.setText(exposureStr)
            self.exposureSlider.setMaximum(EXPOSURE_ABS_MAX)
            self.exposureSlider.setMinimum(EXPOSURE_ABS_MIN)
            self.whiteBalanceLabel.setText(whiteBalanceStr)
            self.whiteBalanceSlider.setMaximum(WB_TEMPERATURE_MAX)
            self.whiteBalanceSlider.setMinimum(WB_TEMPERATURE_MIN)
            self.param1Value.setText(focusValueStr)
            self.param2Value.setText(exposureValueStr)
            self.param3Value.setText(wbValueStr)

            self.gammaLabel.setHidden(True)
            self.gammaSlider.setHidden(True)
            self.param4Value.setHidden(True)
            self.gammaValue.setHidden(True)
            self.param4min.setHidden(True)
            self.param4max.setHidden(True)
        else:
            # Gain
            self.focusLabel.setText(teliGainStr)
            self.focusSlider.setMinimum(TELI_GAIN_MAX * 2)
            self.focusSlider.setMinimum(TELI_GAIN_MIN * 2)
            self.focusSlider.setSingleStep(1)
            self.focusSlider.setPageStep(2)
            self.focusSlider.setTickInterval(5)
            self.param1min.setText(str(TELI_GAIN_MIN))
            self.param1max.setText(str(TELI_GAIN_MAX))
            self.param1Value.setText(teliGainValueStr)

            # Exposure Time
            self.exposureLabel.setText(teliExposureStr)
            self.exposureSlider.setMaximum(TELI_EXPOSURE_TIME_MAX)
            self.exposureSlider.setMinimum(TELI_EXPOSURE_TIME_MIN)
            self.exposureSlider.setSingleStep(500)
            self.exposureSlider.setPageStep(1000)
            self.exposureSlider.setTickInterval(2000)
            self.param2min.setText(str(TELI_EXPOSURE_TIME_MIN))
            self.param2max.setText(str(TELI_EXPOSURE_TIME_MAX))
            self.param2Value.setText(teliExposureTimeStr)

            # white balance and black level
            self.whiteBalanceLabel.setText(teliWhiteBalanceStr)
            self.whiteBalanceSlider.setMaximum(TELI_BLACK_LEVEL_MAX)
            self.whiteBalanceSlider.setMinimum(TELI_BLACK_LEVEL_MIN)
            self.whiteBalanceSlider.setSingleStep(1)
            self.whiteBalanceSlider.setPageStep(1)
            self.whiteBalanceSlider.setTickInterval(1)
            self.param3min.setText(str(TELI_BLACK_LEVEL_MIN))
            self.param3max.setText(str(TELI_BLACK_LEVEL_MAX))
            self.param3Value.setText(teliBlackLevelStr)

             # Gamma
            self.gammaLabel.setText(teliGammaStr)
            self.param4min.setText(str(TELI_GAMMA_MIN))
            self.param4max.setText(str(TELI_GAMMA_MAX))
            self.param4Value.setText(teliGammaValueStr)

        self.updateFocusValueBtn.setText(updateStr)
        self.updateExposureValueBtn.setText(updateStr)
        self.updateWBValueBtn.setText(updateStr)

def main():
    app = QApplication(sys.argv)
    QFontDatabase.addApplicationFont(config.FONT_PATH)
    app.setStyle('Windows')
    with open(config.STYLE_PATH, 'r', encoding="utf-8") as f:
        qss = f.read()
        app.setStyleSheet(qss)
    ex = SystemSettingWindow()
    ex.move(0, 0)
    ex.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
