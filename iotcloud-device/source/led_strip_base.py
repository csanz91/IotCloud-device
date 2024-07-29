import logging

import utils
import switch_base
from flux_led import WifiLedBulb, BulbScanner

logger = logging.getLogger()


class Led_Strip(switch_base.Switch_Base):
    def __init__(self, sensorId, sensorName, ipAddr):
        super().__init__(sensorId, sensorName)

        self.sensorType = "led"
        self.brightness = 0.0

        self.ipAddr = ipAddr
        self.ledDevice = None

        self.connect()

    def connect(self):
        try:
            self.ledDevice = WifiLedBulb(self.ipAddr)
            self.ledDevice.refreshState()
        except:
            logger.error(
                f"It is not possible to connect to the device with ip: {self.ipAddr}", exc_info=True
            )

    def reportBrightness(self):
        if self.mqttClient and self.mqttClient.is_connected():
            self.mqttClient.publish(
                self.mqttHeader + self.sensorId + "/aux/brightness",
                self.brightness,
                qos=1,
                retain=True,
            )

    def setBrightness(self, brightness):
        self.brightness = brightness

        newState = brightness > 0.0
        if newState != self.state:
            super().setState(newState)

        self.reportBrightness()

    def setState(self, newState, retry=2):
        if self.ledDevice:
            if not newState:
                self.ledDevice.turnOff()
                self.brightness = 0.0
            else:
                self.ledDevice.turnOn()
            self.state = newState

            self.reportState()
        elif retry:
            self.connect()
            self.setState(newState, retry=(retry - 1))

    def init(self, mqttHeader, mqttClient):
        super().init(mqttHeader, mqttClient)

        self.reportBrightness()

        topic = self.mqttHeader + self.sensorId + "/aux/setBrightness"
        mqttClient.subscribe(topic)

        def on_message(client, obj, msg):
            try:
                brightness = utils.parseFloat(msg.payload)
                assert 0.0 <= brightness <= 1.0
            except:
                logger.error(f"Invalid brightness value: {msg.payload}")
                return
            self.setBrightness(brightness)

        mqttClient.message_callback_add(topic, on_message)
