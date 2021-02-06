import logging

import led_strip_base

logger = logging.getLogger(__name__)


class Led_Strip_RGB(led_strip_base.Led_Strip):
    def __init__(self, sensorId, sensorName, macAddr):
        super().__init__(sensorId, sensorName, macAddr)

        self.sensorType = "ledRGB"
        self.r = 255
        self.g = 255
        self.b = 255

    def setBrightness(self, brightness, retry=2):
        self.brightness = brightness
        self.setColor(self.r, self.g, self.b)

    def reportColor(self):
        if self.mqttClient and self.mqttClient.is_connected():
            self.mqttClient.publish(
                self.mqttHeader + self.sensorId + "/aux/color",
                "ff{:02x}{:02x}{:02x}".format(self.r, self.g, self.b),
                qos=1,
                retain=True,
            )

    def setColor(self, r, g, b, retry=2):
        self.r = r
        self.g = g
        self.b = b

        if self.ledDevice:

            self.ledDevice.setRgbw(r, g, b, brightness=int(self.brightness * 255))

            self.reportColor()
            self.reportBrightness()
        elif retry:
            self.connect()
            self.setColor(r, g, b, retry=(retry - 1))

    def setState(self, newState, retry=2):
        self.startIncreasingBrightness = newState

        if self.ledDevice:
            if not newState:
                self.ledDevice.turnOff()
                self.brightness = 0.0
                self.reportBrightness()
            else:
                self.setBrightness(0.7)

            self.state = newState
            self.reportState()
        elif retry:
            self.connect()
            self.setState(newState, retry=(retry - 1))

    def init(self, mqttHeader, mqttClient):

        super().init(mqttHeader, mqttClient)

        self.reportColor()
        self.mqttClient.subscribe(self.mqttHeader + self.sensorId + "/aux/setColor")
