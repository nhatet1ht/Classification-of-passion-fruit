from loguru import logger

from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import pyqtSlot
from application.views.screens.system_setting import SystemSettingWindow
from application.views.screens.confirmation_dialog import ConfirmationDialog
from application.views.components.cameraSettingView import CameraSettingView
from application.model.appConfig import SystemSetting
from application.model.videoModel import setCameraFocus, getCameraFocus, setCameraExposure, getCameraExposure, setCameraWhiteBalance, getCameraWhiteBalance
from application.config.config import WEBCAM_RESOLUTION, RES1080P_WH
from application.utils import utils

inactiveStr = utils.getStr('inactive')
changedMsg = utils.getStr('sysSettingChangedMsg')
unchangedMsg = utils.getStr('sysSettingUnchangedMsg')
changeConfimationTitle = utils.getStr('sysSettingChangeParamTitle')
changeConfimationMsg = utils.getStr('sysSettingChangeParamMsg')
resetConfimationTitle = utils.getStr('sysSettingUnchangeParamTitle')
resetConfimationMsg = utils.getStr('sysSettingUnchangeParamMsg')
sysSettingInstructionStr = utils.getStr('sysSettingInstruction')

class SystemSettingController(SystemSettingWindow):
    def __init__(self, videoModel, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.devID = 0
        self.webCameraThread = videoModel

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
        if self.webCameraThread.isRunning():
            self.webCameraThread.stop()
            self.webCameraThread.sendImageSignal.disconnect()
        super().hideEvent(event)

    def initCameraParameters(self):
        self.devID, self.camName = self.webCameraThread.getCurrentCamera(SystemSetting.camera_device)

        # Loading camera parameters
        focus = SystemSetting.focus
        exposure = SystemSetting.exposure
        whiteBalance = SystemSetting.white_balance
        # logger.debug("SETTING SCREEN: focus {}, exposure {}, whiteBalance {}".format(focus, exposure, whiteBalance))

        # Run camera
        frameSize = WEBCAM_RESOLUTION[self.camName] if self.camName in WEBCAM_RESOLUTION.keys() else RES1080P_WH
        self.webCameraThread.setUrl(self.devID, frameSize, False)
        self.webCameraThread.sendImageSignal.connect(self.cameraSettingView.setPixmap)

        # Set initial status
        self.deviceName.setText(str(self.camName))
        if self.camName == "Logicool BRIO":
            self.focusSlider.setMaximum(255)
            self.exposureSlider.setMaximum(2047)
            self.whiteBalanceSlider.setMaximum(7500)

        # Display the current values to UI
        def setParamItem(value, slider, autoCheckBox, updateButton, valueLabel):
            autoCheckBox.setChecked(False)
            updateButton.setEnabled(False)
            valueLabel.setText(str(value))
            if self.webCameraThread.isRunning():
                slider.setValue(value)
                slider.setEnabled(True)
            else:
                slider.setSliderPosition(0)
                slider.setEnabled(False)
                autoCheckBox.setEnabled(False)
        setParamItem(focus, self.focusSlider, self.focusCheckBox, self.updateFocusValueBtn, self.focusValue)
        setParamItem(exposure, self.exposureSlider, self.exposureCheckBox, self.updateExposureValueBtn, self.exposureValue)
        setParamItem(whiteBalance, self.whiteBalanceSlider, self.whiteBalanceCheckBox, self.updateWBValueBtn, self.whiteBalanceValue)

