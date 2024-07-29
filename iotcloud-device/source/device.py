import logging
import os
import threading
import time

import device_base
import led_strip_white
import led_strip_rgb
import power_sensor
import utils
import mqtt_client


logger = logging.getLogger()


class Device:
    def __init__(self, deviceVersion):
        self.deviceInternalId = utils.getDeviceId()
        self.deviceTargetVersion = deviceVersion
        self.deviceVersion = deviceVersion
        self.sensors: list[device_base.Device_Base] = []

    def addSensor(self, sensor):
        self.sensors.append(sensor)

    def exportData(self):
        return {
            "deviceInternalId": self.deviceInternalId,
            "deviceVersion": self.deviceVersion,
            "sensors": [s.exportData() for s in self.sensors],
        }
    
    def loop(self):
        for sensor in self.sensors:
            sensor.loop()


stopEvent = threading.Event()
restartEvent = threading.Event()

device = Device("v1.0")
device.addSensor(led_strip_white.Led_Strip_Mono("002_LED", "LED", "192.168.0.200"))
device.addSensor(led_strip_rgb.Led_Strip_RGB("003_LED", "RGB", "192.168.0.201"))
device.addSensor(power_sensor.Power_Sensor("004_P", "Power", "192.168.0.14"))


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

        try:
            mqttClient.connect()
        except Exception as e:
            logger.error(f"Failed to connect to MQTT server: {str(e)}")
            os._exit(1)  # Terminate the thread so it can be restarted

        restartEvent.clear()

        while not stopEvent.isSet() and not restartEvent.isSet():
            time.sleep(0.1)
            device.loop()

        mqttClient.disconnect()
        

def stopDevice():
    stopEvent.set()

def restartDevice():
    restartEvent.set()
