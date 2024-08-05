### APP VERSION ###
VERSION_INFO="2.00.20240620.rev1"

### STRING ####
STRING_PATH = 'application/views/resources/strings/eng-jpn.csv'

### STYLE ###
STYLE_PATH = 'application/views/resources/style/style.qss'
FONT_PATH = 'application/views/resources/font/FontsFree-Net-SFProDisplay-Regular.ttf'
OPTION_SETTING_PATH = 'application/config/option.json'
SYSTEM_SETTING_PATH = 'application/config/system_setting.json'

### FONT ###
FONT_PATH = 'application/views/resources/font/MS Gothic.ttf'

### SAMPLE IMAGE ###
SAMPLE_IMG_PATH = 'application/views/resources/images/sample.jpg'

### MODE RECOGNITION ###
FULL_CHARACTER_RECOGNITION = 0
SPECIFIC_CHARACTER_RECOGNITION = 1
TABLE_RECOGNITION = 2
OCR_LANGUAGE_CODE =  {"Japanese": "ja", "English": "en"}

### SAVE LOG ###
LOG_DIR = 'logs'

### UI SETTINGS ###
RATIO_W_H = 400/300 #540/720
BASE_H = 720
FONT_SIZE = 18  # 18px

### CAMERA SETTING ###
USB_GSTREAMER = True
RES1080P_WH = (1920, 1080)
WEBCAM_RESOLUTION = {"Logicool BRIO": (3840, 2160), "C922 Pro Stream Webcam": (1920, 1080), "C920 Pro Stream Webcam": (1920, 1080)}
TELICAM_RESOLUTION = (2048, 1536)

FOCUS_ABS_MIN, FOCUS_ABS_MAX = 0, 250
EXPOSURE_ABS_MIN, EXPOSURE_ABS_MAX = 3, 2047
WB_TEMPERATURE_MIN, WB_TEMPERATURE_MAX = 2000, 6500

TELI_GAIN_MIN, TELI_GAIN_MAX = 0.0, 36.0
TELI_EXPOSURE_TIME_MIN, TELI_EXPOSURE_TIME_MAX = 22.0, 99819.0
TELI_BLACK_LEVEL_MIN, TELI_BLACK_LEVEL_MAX = -25.0, 25.0
TELI_GAMMA_MIN, TELI_GAMMA_MAX = 0.45, 1.0
TELI_FRAME_RATE_MIN, TELI_FRAME_RATE_MAX = 0.06, 40.2


BASE_W = 2048
BASE_H = 1536   
CLASSNAMES = ['A', 'B', 'VIP', 'C']
