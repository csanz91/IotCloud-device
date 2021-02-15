import logging
import samsungctl

import device_base

logger = logging.getLogger(__name__)


class TV(device_base.Device_Base):
    def __init__(self, sensorId, sensorName, configPath):
        super().__init__(sensorId, sensorName)
        self.sensorType = "TV"
        self.sensorMetadata = {"bidirectional": False}

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
        super().init(mqttHeader, mqttClient)

        topic = self.mqttHeader + self.sensorId + "/aux/setToogle"
        mqttClient.subscribe(topic)

        def on_message(client, obj, msg):
            self.setToogle()

        mqttClient.message_callback_add(topic, on_message)
