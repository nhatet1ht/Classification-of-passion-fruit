import csv
import os
import sys
import cv2
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from application.config import config
import re
from itertools import product

EPS = 1e-6
lang = os.environ.get('OCRLANG', 'eng')
dir_path = os.path.dirname(os.path.realpath(__file__))
with open(config.STRING_PATH, 'r', encoding="utf-8") as cfgFile:
    reader = csv.reader(cfgFile)
    data = list(reader)
transdict = {}
for d in data[1:]:
    transdict[d[0]] = {'eng': d[1], 'jpn(fake)': d[2], 'jpn': d[3]}

def getStr(name) -> str:
    if not lang:
        return transdict[name]['eng']
    if lang == 'jpn':
        # Return string in this order
        # Corrected Japanese
        # Google Translate Japanese
        # English
        return transdict[name][lang] or transdict[name]['jpn(fake)'] or transdict[name]['eng']
    return transdict[name]['eng']

def rescaleT(img, baseH=1080):
    hpercent = (baseH / float(img.shape[0]))
    if hpercent < 1:
        wsize = int((float(img.shape[1])*float(hpercent)))
        img = cv2.resize(img, (wsize, baseH), interpolation=cv2.INTER_AREA)
    return img

def rgbToPixmap(bgrImage, qSize):
    if bgrImage is None:
        return None
    #bgrImage = rescaleT(bgrImage, config.BASE_H)
    rgbImage = cv2.cvtColor(bgrImage, cv2.COLOR_BGR2RGB)
    h, w, ch = rgbImage.shape
    bytesPerLine = ch * w
    qImg = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
    qPixmap = QPixmap.fromImage(qImg)
    scaled = qPixmap.scaled(qSize, Qt.KeepAspectRatio)
    return scaled

def isFloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

def isInteger(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

def resizeAspectRatio(frame, basewidth):
    # Normalize image size
    wpercent = (basewidth/float(frame.shape[1]))
    if wpercent != 1:
        hsize = int((float(frame.shape[0])*float(wpercent)))
        frame = cv2.resize(frame, (basewidth, hsize))

    return frame