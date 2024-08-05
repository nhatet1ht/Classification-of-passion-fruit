from loguru import logger

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot
from application.views.screens.system_setting import SystemSettingWindow
from application.views.screens.confirmation_dialog import ConfirmationDialog
from application.views.components.cameraSettingView import CameraSettingView
from application.model.appConfig import SystemSetting
from application.config.config import TELICAM_RESOLUTION, RES1080P_WH
from application.utils import utils

inactiveStr = utils.getStr('inactive')
changedMsg = utils.getStr('sysSettingChangedMsg')
unchangedMsg = utils.getStr('sysSettingUnchangedMsg')
changeConfimationTitle = utils.getStr('sysSettingChangeParamTitle')
changeConfimationMsg = utils.getStr('sysSettingChangeParamMsg')
resetConfimationTitle = utils.getStr('sysSettingUnchangeParamTitle')
resetConfimationMsg = utils.getStr('sysSettingUnchangeParamMsg')
sysSettingInstructionStr = utils.getStr('sysSettingInstruction')

INC = 2
DEC_GAMMA = 100

class SystemSettingController2(SystemSettingWindow):
    def __init__(self, videoModel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.devID = 0
        self.teliCameraThread = videoModel

    def initUI(self):
        super().initUI()
        cameraSettingView = CameraSettingView(self.imageFromCamera.parent())
        cameraSettingView.setGeometry(self.imageFromCamera.geometry())
        self.cameraSettingView = cameraSettingView

    def showEvent(self, event):
        super().showEvent(event)
        logger.info("SETTING SCREEN >> Openning Screen...")
        self.messageText.setText(sysSettingInstructionStr)

        # Load the current parameters to UI
        SystemSetting.loadConfig()
        self.initCameraParameters()

    def hideEvent(self, event):
        logger.info("SETTING SCREEN >> Closing Screen...")
        if self.teliCameraThread.isRunning():
            self.teliCameraThread.stop()
            self.teliCameraThread.sendImageSignal.disconnect()
        super().hideEvent(event)

    def initCameraParameters(self):
        self.devID, self.camName = self.teliCameraThread.getCurrentCamera(SystemSetting.camera_device)
        # Loading camera parameters
        gain = SystemSetting.telicamGain
        exposureTime = SystemSetting.telicamExposureTime
        blackLevel = SystemSetting.telicamBlackLevel
        gamma = SystemSetting.telicamGamma

        # logger.debug("SETTING SCREEN: focus {}, exposure {}, whiteBalance {}".format(focus, exposure, whiteBalance))

        # Run camera
        frameSize = TELICAM_RESOLUTION
        self.teliCameraThread.setUrl(int(self.devID), frameSize, False)
        self.teliCameraThread.sendImageSignal.connect(self.cameraSettingView.setPixmap)

        # Set initial status
        self.deviceName.setText(str(self.camName))

        # Display the current values to UI
        def setParamItem(value, slider, autoCheckBox, updateButton, valueLabel, factor=1):
            autoCheckBox.setChecked(False)
            updateButton.setEnabled(False)
            valueLabel.setText(str(value))
            if self.teliCameraThread.isRunning():
                slider.setValue(value * factor)
                slider.setEnabled(True)
            else:
                slider.setSliderPosition(0)
                slider.setEnabled(False)
                autoCheckBox.setEnabled(False)

        setParamItem(gain, self.focusSlider, self.focusCheckBox, self.updateFocusValueBtn, self.focusValue, factor=INC)
        setParamItem(exposureTime, self.exposureSlider, self.exposureCheckBox, self.updateExposureValueBtn, self.exposureValue)
        setParamItem(blackLevel, self.whiteBalanceSlider, self.whiteBalanceCheckBox, self.updateWBValueBtn, self.whiteBalanceValue)
        setParamItem(gamma, self.gammaSlider, self.whiteBalanceCheckBox, self.updateWBValueBtn, self.gammaValue, factor=DEC_GAMMA)
