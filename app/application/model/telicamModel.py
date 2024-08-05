"""
 (C) Copyright 2023 ARS Group (Advanced Research & Solutions)
"""
import cv2
import numpy as np
import pytelicam
import time
from loguru import logger

from PyQt5.QtCore import QThread, pyqtSignal
from application.utils.utils import isFloat, getStr

from application.config.config import RATIO_W_H, \
                                    TELI_GAIN_MIN, TELI_GAIN_MAX, \
                                    TELI_EXPOSURE_TIME_MIN, TELI_EXPOSURE_TIME_MAX, \
                                    TELI_BLACK_LEVEL_MIN, TELI_BLACK_LEVEL_MAX, \
                                    TELI_GAMMA_MIN, TELI_GAMMA_MAX, \
                                    TELI_FRAME_RATE_MIN, TELI_FRAME_RATE_MAX

from application.model.appConfig import SystemSetting

BASE_W = 1440
noCameraStr = getStr('systemSettingNoCamera')

def trimImage(frame, ratio):
    h, w = frame.shape[:2]
    if abs(w / h - ratio) < 1e-3:
        return frame
    
    if w/h - ratio > 0: # cut-out width
        offsetX = int((w - ratio * h) / 2)
        offsetY = 0
    else:   # cut-out height
        offsetX = 0
        offsetY = int((h - w / ratio) / 2)

    frame = frame[offsetY:(h - offsetY), offsetX:(w - offsetX)].copy()
    return frame

def resizeAspectRatio(frame, basewidth):
    # Normalize image size
    wpercent = (basewidth/float(frame.shape[1]))
    if wpercent != 1:
        hsize = int((float(frame.shape[0])*float(wpercent)))
        frame = cv2.resize(frame, (basewidth, hsize), interpolation=cv2.INTER_AREA)

    return frame

class TeliCameraModel(QThread):
    sendImageSignal = pyqtSignal(np.ndarray)
    sendErrMsg = pyqtSignal(str)

    camSystem = None
    instanceCount = 0
    timeout = 5000

    def __init__(self,
                parent=None,
                url=None, # None / Camera device index
                frameSize=(1920, 1080)
                ):
        super(TeliCameraModel, self).__init__(parent)
    
        # Initialize necessary variables
        self.url = url

        self._isOpened = False
        self.frame = None
        self._runFlag = False
        self.cap = None
        self.triggerCtrl = None
        self.triggerFlag = False
        self.receive_signal = None

        # Initialize pytelicam and get the object CameraSystem class
        if TeliCameraModel.camSystem == None:
            TeliCameraModel.camSystem = pytelicam.get_camera_system(int(pytelicam.CameraType.U3v))
        self.cam_num = TeliCameraModel.camSystem.get_num_of_cameras()

    def getCameraDeviceList(self):
        camObjects = []
        if self.cam_num == 0:
            print('Camera not found.')
            return camObjects

        for i in range(self.cam_num):
            cam_info = TeliCameraModel.camSystem.get_camera_information(i)
            camObjects.append({
                "device": i,
                "name": cam_info.cam_model,
                "serial_no": cam_info.cam_serial_number,
                "spec": cam_info.cam_version,
                "user_defined_name": cam_info.cam_user_defined_name
            })
        return camObjects

    def getCurrentCamera(self, devID):
        listCam = self.getCameraDeviceList()
        camID = "0"
        camName = ''
        for cam in listCam:
            if str(cam['device']) == str(devID):
                return devID, str(cam['name'])
        if len(listCam):
            camID = listCam[0]['device']
            camName = listCam[0]['name']
        return camID, camName

    def open(self, triggerCtrl=None):
        """ Open video capture from the input arguments
            If arguments are undefined (None), use original sources
        """
        if self._runFlag:
            self.stop() # Already opened -> stop to re-open again

        while self.isRunning():
            self.sleep()
            continue

        self.triggerCtrl = triggerCtrl
        src = self.url
        if src is not None:    # Use pre-defined source
            self.cap = TeliCameraModel.camSystem.create_device_object(src)
            self.cap.open()
            if self.triggerCtrl == "TriggerSoftware":
                res = self.cap.genapi.set_enum_str_value('TriggerMode', 'On')
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set TriggerMode.")

                res = self.cap.genapi.set_enum_str_value('TriggerSource', 'Software')
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set TriggerSource.")

                res = self.cap.genapi.set_enum_str_value('TriggerSequence', 'TriggerSequence0')
                #if res != pytelicam.CamApiStatus.Success:
                #    raise Exception("Can't set TriggerSequence.")
            else:
                res = self.cap.genapi.set_enum_str_value('TriggerMode', 'Off')
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set TriggerMode.")

            self.receive_signal = TeliCameraModel.camSystem.create_signal()
            self.cap.cam_stream.open(self.receive_signal)
            self.cap.cam_stream.start()

            #self.setCameraConfig()
            self._start()
        else:
            #raise RuntimeError("No source type specified!")
            logger.warning(f"No source type specified for camera {self.url}")
            self.sendErrMsg.emit(noCameraStr)

        TeliCameraModel.instanceCount += 1

    def _start(self):

        if self.cap == None:
            self.url = None # Source is invalid, reset it
            self._isOpened = False
            return

        if self.cap.cam_stream.is_open == False or self.cap.is_open == False:
            self._isOpened = False
            logger.warning('Camera: starting while cap is not opened!')
            return

        if self.triggerCtrl == "TriggerSoftware":
            res = self.cap.genapi.execute_command('TriggerSoftware')
            if res != pytelicam.CamApiStatus.Success:
                self._isOpened = False
                logger.warning('Cannot execute TriggerSoftware.')
                return

        res = TeliCameraModel.camSystem.wait_for_signal(self.receive_signal)
        if res != pytelicam.CamApiStatus.Success:
            self._isOpened = False
            logger.warning(f'Grab error! status = {res}')
            self.sendErrMsg.emit(noCameraStr)
            return
        else:
            # try to grab the 1st image and determine width and height
            with self.cap.cam_stream.get_current_buffered_image() as image_data:
                if image_data.status != pytelicam.CamApiStatus.Success:
                    self.url = None # Source is invalid, reset it
                    self._isOpened = False
                    return
                if image_data.pixel_format == pytelicam.CameraPixelFormat.Mono8:
                    np_arr = image_data.get_ndarray(pytelicam.OutputImageType.Raw)
                else:
                    np_arr = image_data.get_ndarray(pytelicam.OutputImageType.Bgr24)
                self.imH, self.imW = np_arr.shape[:2]

        self._isOpened = True

    def isOpened(self):
        return self._isOpened

    def setUrl(self, url, frameSize=(1920, 1080), isRotate=False):
        self.url = url
        self.frameSize = frameSize
        self.isRotate = isRotate
        self.open() # reopen the new camera
        self.start() # start to stream camera

    def getInputSrc(self):
        return self.url

    def setTriggerFlag(self):
        self.triggerFlag = True

    def run(self):
        self._runFlag = True
        while self.isOpened() and self._runFlag:
            if self.triggerCtrl == "TriggerSoftware":
                if self.triggerFlag == False:
                    self.msleep(10)
                    continue
                self.triggerFlag = False

                res = self.cap.genapi.execute_command('TriggerSoftware')
                if res != pytelicam.CamApiStatus.Success:
                    self._runFlag = False
                    break

            res = TeliCameraModel.camSystem.wait_for_signal(self.receive_signal)
            if res != pytelicam.CamApiStatus.Success:
                self._runFlag = False
                break

            image_data = self.cap.cam_stream.get_current_buffered_image()
            if image_data.status != pytelicam.CamApiStatus.Success:
                self._runFlag = False
                break

            if image_data.pixel_format == pytelicam.CameraPixelFormat.Mono8:
                np_arr = image_data.get_ndarray(pytelicam.OutputImageType.Raw)
            else:
                np_arr = image_data.get_ndarray(pytelicam.OutputImageType.Bgr24)

            image_data.release() # release the image data object immediately

            # Preprocess raw frame
            if self.isRotate:
                cvImage = cv2.rotate(np_arr, cv2.ROTATE_90_CLOCKWISE)
            else:
                cvImage = np_arr.copy()

            cvImage = trimImage(cvImage, ratio=RATIO_W_H)
            #cvImage = resizeAspectRatio(cvImage, basewidth=BASE_W)

            frame = cvImage.copy()
            self.sendImageSignal.emit(frame)

            self.msleep(10)

        #self.release()

    def release(self):
        if self.cap != None:
            if self.cap.cam_stream.is_open == True:
                self.cap.cam_stream.stop()
                self.cap.cam_stream.close()

                if self.cap.is_open == True:
                    self.cap.close()

            self.cap = None
        if self.receive_signal != None:
            TeliCameraModel.camSystem.close_signal(self.receive_signal)
            self.receive_signal = None

    def stop(self):
        self._runFlag = False
        self.wait()
        self.release()

    def terminateCam(self):
        TeliCameraModel.instanceCount -= 1
        if TeliCameraModel.instanceCount == 0:
            TeliCameraModel.camSystem.terminate()
            TeliCameraModel.camSystem = None

    def getTeliCameraGainAuto(self):
        val = None
        if self.cap is not None:
            res, val = self.cap.genapi.get_enum_str_value('GainAuto')
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't get GainAuto.")
        return val

    def setTeliCameraGainAuto(self, gainAuto):
        if self.cap is not None:
            res = self.cap.genapi.set_enum_str_value('GainAuto', gainAuto)
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't set GainAuto.")

    def getTeliCameraGain(self):
        val = None
        if self.cap is not None:
            res, val = self.cap.genapi.get_float_value('Gain')
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't set Gain.")
        return val

    def setTeliCameraGain(self, gain):
        if self.cap is not None:
            if isFloat(gain) and TELI_GAIN_MIN <= float(gain) <= TELI_GAIN_MAX:
                res = self.cap.genapi.set_float_value('Gain', float(gain))
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set Gain.")
            else:
                logger.warning(f"Cannot configure because the parameter is invalid: Gain (float, range:{TELI_GAIN_MIN}-{TELI_GAIN_MAX}, actual: {gain})")

    def getTeliCameraExposureAuto(self):
        val = None
        if self.cap is not None:
            res, val = self.cap.genapi.get_enum_str_value('ExposureAuto')
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't get ExposureAuto.")
        return val

    def setTeliCameraExposureAuto(self, exposureAuto):
        if self.cap is not None:
            res = self.cap.genapi.set_enum_str_value('ExposureAuto', exposureAuto)
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't set ExposureAuto.")

    def getTeliCameraExposureTime(self):
        val = None
        if self.cap is not None:
            res, val = self.cap.genapi.get_float_value('ExposureTime')
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't get ExposureTime.")
        return val

    def setTeliCameraExposureTime(self, exposureTime):
        if self.cap is not None:
            if isFloat(exposureTime) and TELI_EXPOSURE_TIME_MIN <= float(exposureTime) <= TELI_EXPOSURE_TIME_MAX:
                res = self.cap.genapi.set_float_value('ExposureTime', float(exposureTime))
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set ExposureTime.")
            else:
                logger.warning(f"Cannot configure because the parameter is invalid: ExposureTime (float, range:{TELI_EXPOSURE_TIME_MIN}-{TELI_EXPOSURE_TIME_MAX}, actual: {exposureTime})")

    def getTeliCameraBalanceWhiteAuto(self):
        val = None
        if self.cap is not None:
            res, val = self.cap.genapi.get_enum_str_value('BalanceWhiteAuto')
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't set BalanceWhiteAuto.")
        return val

    def setTeliCameraBalanceWhiteAuto(self, balanceWhiteAuto):
        if self.cap is not None:
            res = self.cap.genapi.set_enum_str_value('BalanceWhiteAuto', balanceWhiteAuto)
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't set BalanceWhiteAuto.")

    def getTeliCameraBlackLevel(self):
        val = None
        if self.cap is not None:
            res, val = self.cap.genapi.get_float_value('BlackLevel')
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't get BlackLevel.")
        return val

    def setTeliCameraBlackLevel(self, blackLevel):
        if self.cap is not None:
            if isFloat(blackLevel) and TELI_BLACK_LEVEL_MIN <= float(blackLevel) <= TELI_BLACK_LEVEL_MAX:
                res = self.cap.genapi.set_float_value('BlackLevel', float(blackLevel))
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set BlackLevel.")
            else:
                logger.warning(f"Cannot configure because the parameter is invalid: BlackLevel (float, range:{TELI_BLACK_LEVEL_MIN}-{TELI_BLACK_LEVEL_MAX}, actual: {blackLevel})")

    def getTeliCameraGamma(self):
        val = None
        if self.cap is not None:
            res, val = self.cap.genapi.get_float_value('Gamma')
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't get Gamma.")
        return val

    def setTeliCameraGamma(self, gamma):
        if self.cap is not None:
            if isFloat(gamma) and TELI_GAMMA_MIN <= float(gamma) <= TELI_GAMMA_MAX:
                res = self.cap.genapi.set_float_value('Gamma', float(gamma))
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set Gamma.")
            else:
                logger.warning(f"Cannot configure because the parameter is invalid: Gamma (float, range:{TELI_GAMMA_MIN}-{TELI_GAMMA_MAX}, actual: {gamma})")

    def setTeliCameraAcquisitionFrameRateEnable(self, frameRateEnable):
        if self.cap is not None:
            res = self.cap.genapi.set_bool_value('AcquisitionFrameRateEnable', frameRateEnable)
            if res != pytelicam.CamApiStatus.Success:
                raise Exception("Can't set AcquisitionFrameRateEnable.")

    def setTeliCameraAcquisitionFrameRate(self, frameRate):
        if self.cap is not None:
            if isFloat(frameRate) and TELI_FRAME_RATE_MIN <= float(frameRate) <= TELI_FRAME_RATE_MAX:
                res = self.cap.genapi.set_float_value('AcquisitionFrameRate', float(frameRate))
                if res != pytelicam.CamApiStatus.Success:
                    raise Exception("Can't set AcquisitionFrameRate.")
            else:
                logger.warning(f"Cannot configure because the parameter is invalid: FrameRate (float, range:{TELI_FRAME_RATE_MIN}-{TELI_FRAME_RATE_MAX}, actual: {frameRate})")

    def setCameraConfig(self):
        # Acquisition setting
        self.setTeliCameraAcquisitionFrameRateEnable(frameRateEnable=True)
        self.setTeliCameraAcquisitionFrameRate(SystemSetting.telicamAcquisitionFrameRate)

        # Gain Auto Off and Gain value setting
        self.setTeliCameraGainAuto("Off")
        self.setTeliCameraGain(SystemSetting.telicamGain)

        # Exposure Auto Off and Exposure Time value setting
        self.setTeliCameraExposureAuto("Off")
        self.setTeliCameraExposureTime(SystemSetting.telicamExposureTime)

        # Set Gamma Correction
        self.setTeliCameraGamma(SystemSetting.telicamGamma)

        # BlanceWhiteAuto
        if SystemSetting.telicamBalanceWhiteAuto == "Once":
            logger.info("WhiteBalanceAuto is currently Once, should not set it during opening application!")
        elif SystemSetting.telicamBalanceWhiteAuto == "Off":
            self.setTeliCameraBalanceWhiteAuto("Off")

        # Black level
        self.setTeliCameraBlackLevel(SystemSetting.telicamBlackLevel)
