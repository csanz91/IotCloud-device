import logging
import threading
import time

import led_strip_base

logger = logging.getLogger(__name__)


class Led_Strip_Mono(led_strip_base.Led_Strip):
    def __init__(self, sensorId, sensorName, macAddr):
        super().__init__(sensorId, sensorName, macAddr)

        self.increaseBrightnessDuration = 600.0  # seconds
        self.timerPeriod = 1.0  # seconds
        self.startIncreasingBrightness = False

        self.timer = threading.Thread(target=self.runTimer)
        self.timer.daemon = True
        self.timer.start()

    def runTimer(self):
        def clamp(n, minn, maxn):
            return max(min(maxn, n), minn)

        tick = 0
        while True:
            if self.startIncreasingBrightness:
                try:
                    newBrightness = pow(
                        tick * self.timerPeriod / self.increaseBrightnessDuration, 2
                    )
                    tick += 1
                    self.setBrightness(clamp(newBrightness, 0.004, 1.0))
                except:
                    logger.error("Timer error.", exc_info=True)
            else:
                tick = 0
            time.sleep(self.timerPeriod)

    def setBrightness(self, brightness, retry=2):
        self.brightness = brightness
        if self.ledDevice:
            self.ledDevice.setBrightness(brightness)
            self.ledDevice.refreshState()

        elif retry < 1:
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
        elif retry < 1:
            self.connect()
            self.setState(newState, retry=(retry - 1))
