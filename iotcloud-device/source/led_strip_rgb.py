import logging

import led_strip_base

logger = logging.getLogger(__name__)


class Led_Strip_RGB(led_strip_base.Led_Strip):
    def __init__(self, sensorId, sensorName, macAddr):
        super().__init__(sensorId, sensorName, macAddr)

        self.sensorType = "ledRGB"
        self.selColor = "000F0F0F"

    def setBrightness(self, brightness, retry=2):
        self.brightness = brightness
        self.setColor(self.selColor)

    def reportColor(self):
        if self.mqttClient and self.mqttClient.is_connected():
            self.mqttClient.publish(
                self.mqttHeader + self.sensorId + "/aux/color",
                self.selColor,
                qos=1,
                retain=True,
            )

    def setColor(self, newColor, retry=2):

        self.selColor = newColor

        if self.ledDevice:
            r = int(newColor[2:4], 16)
            g = int(newColor[4:6], 16)
            b = int(newColor[6:8], 16)

            self.ledDevice.setRgbw(r, g, b, brightness=int(self.brightness * 255))

            self.reportColor()
            self.reportBrightness()
        elif retry:
            self.connect()
            self.setColor(newColor, retry=(retry - 1))

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
