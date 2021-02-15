import logging

import paho.mqtt.subscribe as subscribe
import utils
import device_base

logger = logging.getLogger(__name__)


class Switch_Base(device_base.Device_Base):
    def reportState(self):
        if self.mqttClient and self.mqttClient.is_connected():
            self.mqttClient.publish(
                self.mqttHeader + self.sensorId + "/state",
                self.state,
                qos=1,
                retain=True,
            )

    def setState(self, newState):
        self.state = newState
        self.reportState()

    def init(self, mqttHeader, mqttClient):

        super().init(mqttHeader, mqttClient)

        mqttClient.publish(
            mqttHeader + self.sensorId + "/aux/switch",
            self.version,
            qos=1,
            retain=True,
        )

        topic = mqttHeader + self.sensorId + "/setState"
        mqttClient.subscribe(topic)

        def on_message(client, obj, msg):
            msg.payload = msg.payload.decode("utf-8")
            try:
                state = utils.decodeBoolean(msg.payload)
            except:
                logger.error(f"Invalid state value: {msg.payload}")
                return
            self.setState(state)

        mqttClient.message_callback_add(topic, on_message)

        self.reportState()
