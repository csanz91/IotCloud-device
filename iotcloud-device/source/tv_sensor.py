import logging
import samsungctl

import utils

logger = logging.getLogger(__name__)


class TV:
    def __init__(self, sensorId, sensorName, configPath):
        self.sensorId = f"{utils.getDeviceId()}_{sensorId}"
        self.sensorName = sensorName
        self.sensorType = "TV"
        self.state = False
        self.version = "v0.3_gw"
        self.sensorMetadata = {"bidirectional": False}
        self.mqttHeader = ""
        self.mqttClient = None

        config = samsungctl.Config.load(configPath)
        self.remote = samsungctl.Remote(config)

    def setToogle(self):
        self.setCommand("KEY_POWER")

    def setCommand(self, command):
        try:
            self.remote.control(command)
        except:
            logger.error(f"Could not send the command: {command}", exc_info=True)

    def init(self, mqttHeader, mqttClient):
        self.mqttHeader = mqttHeader
        self.mqttClient = mqttClient

        mqttClient.subscribe(mqttHeader + self.sensorId + "/aux/setToogle")
        mqttClient.subscribe(mqttHeader + "+/setToogle")

    def exportData(self):
        return {
            "sensorId": self.sensorId,
            "sensorName": self.sensorName,
            "sensorType": self.sensorType,
            "version": self.version,
            "sensorMetadata": self.sensorMetadata,
        }
