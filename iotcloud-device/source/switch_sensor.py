import logging

import utils

logger = logging.getLogger(__name__)


class Switch:
    def __init__(self, sensorId, sensorName):
        self.sensorId = f"{utils.getDeviceId()}_{sensorId}"
        self.sensorName = sensorName
        self.sensorType = "switch"
        self.state = False
        self.version = "v0.3_gw"
        self.sensorMetadata = {}
        self.mqttHeader = ""
        self.mqttClient = None

    def reportState(self):
        if self.mqttClient and self.mqttClient.is_connected():
            self.mqttClient.publish(
                self.mqttHeader + self.sensorId + "/state",
                self.state,
                qos=1,
                retain=True,
            )

    def setState(self, newState):
        self.state = newState
        self.reportState()

    def init(self, mqttHeader, mqttClient):

        self.mqttHeader = mqttHeader
        self.mqttClient = mqttClient

        mqttClient.publish(
            mqttHeader + self.sensorId + "/aux/switch", self.version, qos=1, retain=True
        )

        mqttClient.publish(
            mqttHeader + self.sensorId + "/state", self.state, qos=1, retain=True
        )

        mqttClient.subscribe(mqttHeader + self.sensorId + "/setState")

    def exportData(self):
        return {
            "sensorId": self.sensorId,
            "sensorName": self.sensorName,
            "sensorType": self.sensorType,
            "version": self.version,
            "sensorMetadata": self.sensorMetadata,
        }
