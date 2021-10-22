import logging
import logging.config
import ssl

import paho.mqtt.client as mqtt

import utils

logger = logging.getLogger()


class MqttClient:
    def __init__(self, token, locationId, deviceId, sensors):
        self.token = token
        self.locationId = locationId
        self.deviceId = deviceId
        self.mqttHeader = f"v1/{locationId}/{deviceId}/"
        self.sensors = sensors
        self.client = None

    def getSensor(self, sensorId):
        for sensor in self.sensors:
            if sensor.sensorId == sensorId:
                return sensor

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected with result code: {rc}")

        client.publish(self.mqttHeader + "status", "online", retain=True)

        for sensor in self.sensors:
            sensor.init(self.mqttHeader, client)

    def on_disconnect(self, client, userdata, rc):
        logger.info(f"Disconnected result code: {rc}")

    def connect(self):

        self.client = mqtt.Client(
            client_id=self.deviceId + utils.getDeviceId(), transport="websockets"
        )
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.will_set(self.mqttHeader + "status", "offline", retain=True)
        self.client.username_pw_set(self.token, "_")
        self.client.tls_set(
            ca_certs=None,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )

        self.client.connect("mqtt.iotcloud.es", 443, 30)
        self.client.loop_start()

    def disconnect(self):
        if self.client:
            self.client.disconnect()
