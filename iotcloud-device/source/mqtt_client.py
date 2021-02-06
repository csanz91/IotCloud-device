import logging
import logging.config
import random
import ssl
import time

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

    def on_message(self, client, userdata, msg):
        msg.payload = msg.payload.decode("utf-8")
        try:
            topics = msg.topic.split("/")
            # version = topics[0]
            # locationId = topics[1]
            # deviceId = topics[2]
            sensorId = topics[3]
            endpoint = topics[4]
        except:
            logger.error(f"Unable to decode topic: {msg.topic}", exc_info=True)
            return

        sensor = self.getSensor(sensorId)
        if not sensor:
            logger.error(f"The sensor with id: {sensorId} was not found")
            return

        if endpoint == "setState":
            try:
                state = utils.decodeBoolean(msg.payload)
            except:
                logger.error(f"Invalid state value: {state}")
                return
            sensor.setState(state)
        elif endpoint == "aux":
            action = topics[5]

            if action == "setToogle":
                sensor.setToogle()
            elif action == "setBrightness":
                try:
                    brightness = utils.parseFloat(msg.payload)
                except:
                    logger.error(f"Invalid brightness value: {brightness}")
                    return
                sensor.setBrightness(brightness)
            elif action == "setColor":
                sensor.setColor(msg.payload)
            elif action == "command":
                sensor.sendCommand(msg.payload)

    def connect(self):

        self.client = mqtt.Client(client_id=self.deviceId + utils.getDeviceId())
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message
        self.client.will_set(self.mqttHeader + "status", "offline", retain=True)
        self.client.username_pw_set(self.token, "_")
        self.client.tls_set(
            ca_certs=None,
            certfile=None,
            keyfile=None,
            cert_reqs=ssl.CERT_REQUIRED,
            tls_version=ssl.PROTOCOL_TLSv1_2,
        )

        self.client.connect("mqtt.iotcloud.es", 8883, 30)
        self.client.loop_start()

    def disconnect(self):
        if self.client:
            self.client.disconnect()
