import logging

import device_base

logger = logging.getLogger(__name__)


class Switch_Base(device_base.Device_Base):
    def __init__(self, sensorId, sensorName):
        super().__init__(sensorId, sensorName)

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

        super().init(mqttHeader, mqttClient)

        mqttClient.publish(
            mqttHeader + self.sensorId + "/aux/switch",
            self.version,
            qos=1,
            retain=True,
        )

        self.reportState()
        mqttClient.subscribe(mqttHeader + self.sensorId + "/setState")

