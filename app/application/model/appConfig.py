import json
from application.config import config

class SystemSetting:

    camera_active = False
    camera_name = ""
    camera_spec = ""
    camera_device = ""

    focus = 0
    exposure = 0
    white_balance = 0

    telicamAcquisitionFrameRate = 10.0
    telicamGain = 0.0
    telicamExposureTime = 8000.0
    telicamGamma = 1.0
    telicamBlackLevel = 0.0

    low_conf = 0.0
    med_conf = 0.0
    high_conf = 0.0

    @classmethod
    def loadConfig(cls):
        with open(config.SYSTEM_SETTING_PATH, 'r', encoding='utf-8') as f:
            conf = json.load(f)

        cls.camera_active = conf['camera_device']['active']
        cls.camera_name = conf['camera_device']['name']
        cls.camera_spec = conf['camera_device']['spec']
        cls.camera_device = conf['camera_device']['device']

        cls.focus = conf['webcam_setting']['focus']
        cls.exposure = conf['webcam_setting']['exposure']
        cls.white_balance = conf['webcam_setting']['white_balance']

        cls.telicamAcquisitionFrameRate = conf['telicam_setting']['AcquisitionFrameRate']
        cls.telicamGain = conf['telicam_setting']['Gain']
        cls.telicamExposureTime = conf['telicam_setting']['ExposureTime']
        cls.telicamGamma = conf['telicam_setting']['Gamma']
        cls.telicamBalanceWhiteAuto = conf['telicam_setting']['BalanceWhiteAuto']
        cls.telicamBlackLevel = conf['telicam_setting']['BlackLevel']

        cls.low_conf = conf['app_setting']['low_conf']
        cls.med_conf = conf['app_setting']['med_conf']
        cls.high_conf = conf['app_setting']['high_conf']

    @classmethod
    def toDict(cls):
        return {
            'camera_device': {
                'active': cls.camera_active,
                'name': cls.camera_name,
                'spec': cls.camera_spec,
                'device': cls.camera_device
            },
            'webcam_setting': {
                'focus': cls.focus,
                'exposure': cls.exposure,
                'white_balance': cls.white_balance
            },
            'telicam_setting': {
                'AcquisitionFrameRate': cls.telicamAcquisitionFrameRate,
                "Gain": cls.telicamGain,
                "ExposureTime": cls.telicamExposureTime,
                "Gamma": cls.telicamGamma,
                "BalanceWhiteAuto": cls.telicamBalanceWhiteAuto,
                "BlackLevel": cls.telicamBlackLevel
            },
            'app_setting': {
                'low_conf': cls.low_conf,
                'med_conf': cls.med_conf,
                'high_conf': cls.high_conf
            }
        }

    @classmethod
    def save(cls):
        conf = cls.toDict()
        with open(config.SYSTEM_SETTING_PATH, 'w+', encoding='utf-8') as f:
            json.dump(conf, f)