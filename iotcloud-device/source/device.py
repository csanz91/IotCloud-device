import logging
import threading
import time

import tv_sensor
import led_strip_white
import led_strip_rgb
import utils
import mqtt_client


logger = logging.getLogger(__name__)


class Device:
    def __init__(self, deviceVersion):
        self.deviceInternalId = utils.getDeviceId()
        self.deviceTargetVersion = deviceVersion
        self.deviceVersion = deviceVersion
        self.sensors = []

    def addSensor(self, sensor):
        self.sensors.append(sensor)

    def exportData(self):
        return {
            "deviceInternalId": self.deviceInternalId,
            "deviceVersion": self.deviceVersion,
            "sensors": [s.exportData() for s in self.sensors],
        }


stopEvent = threading.Event()
restartEvent = threading.Event()

device = Device("v1.0")
device.addSensor(tv_sensor.TV("001_TV", "TV", "../config/samsung.cfg"))
device.addSensor(led_strip_white.Led_Strip_Mono("002_LED", "LED", "C44F33D2B780"))
device.addSensor(led_strip_rgb.Led_Strip_RGB("003_LED", "RGB", "B4E84223BDBC"))


def runDevice():

    while not stopEvent.isSet():

        deviceData = None
        while not deviceData:
            deviceData = utils.getDeviceData()
            time.sleep(5)

        mqttClient = mqtt_client.MqttClient(
            deviceData["token"],
            deviceData["locationId"],
            deviceData["deviceId"],
            device.sensors,
        )

        mqttClient.connect()
        restartEvent.clear()

        restartEvent.wait()

        mqttClient.disconnect()


def stopDevice():
    stopEvent.set()


def restartDevice():
    restartEvent.set()
