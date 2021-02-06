import logging
import threading
import time

import led_strip_base

logger = logging.getLogger(__name__)


class Led_Strip_Mono(led_strip_base.Led_Strip):
    def __init__(self, sensorId, sensorName, macAddr):
        super().__init__(sensorId, sensorName, macAddr)

        self.increaseBrightnessDuration = 600.0  # seconds
        self.timerPeriod = 0.1  # seconds
        self.startIncreasingBrightness = False

        self.timer = threading.Thread(target=self.runTimer)
        self.timer.daemon = True
        self.timer.start()

    def runTimer(self):
        while True:
            if self.startIncreasingBrightness:
                self.setBrightness(
                    self.brightness + self.timerPeriod / self.increaseBrightnessDuration
                )
            time.sleep(self.timerPeriod)

    def reportBrightness(self):
        if self.mqttClient and self.mqttClient.is_connected():
            self.mqttClient.publish(
                self.mqttHeader + self.sensorId + "/aux/brightness",
                self.brightness,
                qos=1,
                retain=True,
            )

    def setBrightness(self, brightness, retry=2):
        self.brightness = brightness
        if self.ledDevice:
            self.ledDevice.setBrightness(brightness)
            self.ledDevice.refreshState()

        elif retry:
            self.connect()
            self.setBrightness(brightness, retry=(retry - 1))

        if brightness == 0.0 and self.state:
            self.startIncreasingBrightness = False
            self.state = False
            self.reportState()
        elif brightness > 0.0 and not self.state:
            self.state = True
            self.reportState()

        self.reportBrightness()

    def setState(self, newState, retry=2):
        self.startIncreasingBrightness = newState

        if self.ledDevice:
            if not newState:
                self.ledDevice.turnOff()
                self.brightness = 0.0
            self.state = newState

            self.reportState()
            self.reportBrightness()
        elif retry:
            self.connect()
            self.setState(newState, retry=(retry - 1))

    def init(self, mqttHeader, mqttClient):

        super().init(mqttHeader, mqttClient)

