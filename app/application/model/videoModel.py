import cv2
import numpy as np
import subprocess
import time
from loguru import logger

from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot
from application.utils import utils
from application.config.config import USB_GSTREAMER, RATIO_W_H, \
                                        FOCUS_ABS_MAX, FOCUS_ABS_MIN, \
                                        EXPOSURE_ABS_MAX, EXPOSURE_ABS_MIN, \
                                        WB_TEMPERATURE_MAX, WB_TEMPERATURE_MIN
from application.model.appConfig import SystemSetting

noCameraStr = utils.getStr('systemSettingNoCamera')

def trimImage(frame, ratioWH):
    h, w = frame.shape[:2]
    if abs(w / h - ratioWH) < 1e-3:
        return frame
    if w / h - ratioWH > 0: # cut-out width
        offsetX = int((w - ratioWH * h) / 2)
        offsetY = 0
    else:   # cut-out height
        offsetX = 0
        offsetY = int((h - w / ratioWH) / 2)
    frame = frame[offsetY:(h - offsetY), offsetX:(w - offsetX)].copy()
    return frame

def openCamera(dev, width, height):
    """Open a USB webcam."""
    if USB_GSTREAMER:
        gst_str = ('v4l2src device=/dev/video{} ! jpegdec ! '
                   'video/x-raw, width=(int){}, height=(int){} ! '
                   'videoconvert ! appsink').format(dev, width, height)
        cap = cv2.VideoCapture(gst_str, cv2.CAP_GSTREAMER)
        return cap
    else:
        cap = cv2.VideoCapture(int(dev))
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        return cap

class VideoThread(QThread):
    sendImageSignal = pyqtSignal(np.ndarray)
    sendErrMsg = pyqtSignal(str)

    def __init__(self, parent=None, url=None, frameSize=(1920, 1080)):
        super(VideoThread, self).__init__(parent)
        self.url = url
        self.frameSize = frameSize
        self.isRotate = False
        self.threadActive = False

    def getCameraDeviceList(self):
        """ Get the list of v4l2 camera devices
        """
        try:
            out = subprocess.run("v4l2-ctl --list-devices",
                                    shell=True, stdout=subprocess.PIPE)
        except subprocess.CalledProcessError as e:
            return []

        camList = out.stdout.decode().split(
            '\n\n')[:-1]  # Remove the empty last str
        camObjects = []
        for cam in camList:
            longName, device = cam.split('\n\t')[:2]
            camName = '('.join(longName.split('(')[:-1]).strip()
            camSpec = longName.split('(')[-1].split(')')[0]
            device = int(device[10:])

            camObjects.append({
                "name": camName,
                "spec": camSpec,
                "device": str(device)
            })

        camObjects = sorted(camObjects, key=lambda cam: int(cam['device']))
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

    @pyqtSlot(str)
    def setUrl(self, url, frameSize=(1920, 1080), isRotate=False):
        self.url = url
        self.frameSize = frameSize
        self.isRotate = isRotate
        self.stop()
        while self.isRunning():
            print('Waiting for restarted')
            self.sleep()
            continue
        self.threadActive = True
        self.start()

    def run(self):
        if self.url is None:
            self.sendErrMsg.emit(noCameraStr)
            return
        #cap = openCamera(self.url, width=self.frameSize[0], height=self.frameSize[1])
        ####
        cap = cv2.VideoCapture("video/2023-07-20-09-23-45.avi") # /hdd/project/Fruit/Dataset/0_Raw/2023-08-12/Telicam/ExpNo12003.avi
        logger.info("Device {} started ".format(self.url))
        ret, _ = cap.read()
        if not ret:
            self.sendErrMsg.emit(noCameraStr)
        setCameraFocus(focus=SystemSetting.focus, devID=self.url)
        setCameraExposure(exposure=SystemSetting.exposure, devID=self.url)
        setCameraWhiteBalance(white_balance=SystemSetting.white_balance, devID=self.url)

        while self.threadActive:
            ret, frame = cap.read()
            if ret:
                if self.isRotate:
                    frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
                frame = trimImage(frame, RATIO_W_H)
                self.sendImageSignal.emit(frame)
            else:
                break
            self.msleep(30)
        cap.release()

    def stop(self):
        self.threadActive = False
        self.wait()

def setCameraFocus(focus, devID):
    if focus == "AUTO_MODE":
        subprocess.call(
            f'v4l2-ctl -d /dev/video{devID} --set-ctrl=focus_auto=1', shell=True)
    elif focus == "MANU_MODE":
        subprocess.call(
            f'v4l2-ctl -d /dev/video{devID} --set-ctrl=focus_auto=0', shell=True)
    elif isinstance(focus, int):
        if FOCUS_ABS_MIN <= int(focus) <= FOCUS_ABS_MAX:
            subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=focus_auto=0', shell=True)
            time.sleep(0.01)
            subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=focus_absolute={int(focus)}', shell=True)
        else:
            logger.warning(
                f"Cannot configure because the parameter is invalid: Focus Absolute (integer, range:{FOCUS_ABS_MIN}-{FOCUS_ABS_MAX}, actual: {focus})")
    else:
        logger.warning(f"Do nothing with the focus argument: {focus}")

def getCameraFocus(devID):
    rst = subprocess.check_output(
        f'v4l2-ctl -d /dev/video{devID} --get-ctrl=focus_absolute', shell=True)
    focus_absolute = rst.decode('UTF-8').split(":")[-1].replace("\n", "")
    return int(focus_absolute)

def setCameraExposure(exposure, devID):
    if exposure == "AUTO_MODE":
        subprocess.call(
            f'v4l2-ctl -d /dev/video{devID} --set-ctrl=exposure_auto=3', shell=True)
    elif exposure == "MANU_MODE":
        subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=exposure_auto=1', shell=True)
    elif isinstance(exposure, int):
        if EXPOSURE_ABS_MIN <= int(exposure) <= EXPOSURE_ABS_MAX:
            subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=exposure_auto=1', shell=True)
            time.sleep(0.01)
            subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=exposure_absolute={int(exposure)}', shell=True)
        else:
            logger.warning(
                f"Cannot configure because the parameter is invalid: Exposure Absolute (integer, range:{EXPOSURE_ABS_MIN}-{EXPOSURE_ABS_MAX}, actual: {exposure})")
    else:
        logger.warning(f"Do nothing with the exposure argument: {exposure}")

def getCameraExposure(devID):
    rst = subprocess.check_output(
        f'v4l2-ctl -d /dev/video{devID} --get-ctrl=exposure_absolute', shell=True)
    exposure_absolute = rst.decode(
        'UTF-8').split(":")[-1].replace("\n", "")
    return int(exposure_absolute)

def setCameraWhiteBalance(white_balance, devID):
    if white_balance == "AUTO_MODE":
        subprocess.call(
            f'v4l2-ctl -d /dev/video{devID} --set-ctrl=white_balance_temperature_auto=1', shell=True)
    elif white_balance == "MANU_MODE":
        subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=white_balance_temperature_auto=0', shell=True)
    elif isinstance(white_balance, int):
        if WB_TEMPERATURE_MIN <= int(white_balance) <= WB_TEMPERATURE_MAX:
            subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=white_balance_temperature_auto=0', shell=True)
            time.sleep(0.01)
            subprocess.call(
                f'v4l2-ctl -d /dev/video{devID} --set-ctrl=white_balance_temperature={int(white_balance)}', shell=True)
        else:
            logger.warning(
                f"Cannot configure because the parameter is invalid: WB Temperature (integer, range:{WB_TEMPERATURE_MIN}-{WB_TEMPERATURE_MAX}, actual: {white_balance})")
    else:
        logger.warning(f"Do nothing with the white balance argument: {white_balance}")

def getCameraWhiteBalance(devID):
    rst = subprocess.check_output(
        f'v4l2-ctl -d /dev/video{devID} --get-ctrl=white_balance_temperature', shell=True)
    white_balance_temperature = rst.decode(
        'UTF-8').split(":")[-1].replace("\n", "")
    return int(white_balance_temperature)

