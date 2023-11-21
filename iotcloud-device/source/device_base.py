import logging
import threading

import utils

logger = logging.getLogger()


class Device_Base:
    def __init__(self, sensorId, sensorName):
        self.sensorId = f"{utils.getDeviceId()}_{sensorId}"
        self.sensorName = sensorName
        self.sensorType = ""
        self.state = False
        self.version = "v0.3_gw"
        self.sensorMetadata = {}
        self.mqttHeader = ""
        self.mqttClient = None

    def init(self, mqttHeader, mqttClient):

        self.mqttHeader = mqttHeader
        self.mqttClient = mqttClient

    def exportData(self):
        return {
            "sensorId": self.sensorId,
            "sensorName": self.sensorName,
            "sensorType": self.sensorType,
            "version": self.version,
            "sensorMetadata": self.sensorMetadata,
        }
    
    def loop(self):
        pass
