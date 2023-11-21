import logging
import math
import time

import utils
import switch_base

logger = logging.getLogger(__name__)


class Analog_Sensor(switch_base.Switch_Base):
    def __init__(
        self,
        sensorId,
        sensorName,
        reportValuePeriod=30.0,
        decimals=2,
        enableFilter=True,
        filterRateChange=0.1,
    ):
        super().__init__(sensorId, sensorName)

        self.reportValuePeriod = reportValuePeriod
        self.decimals = decimals
        self.enableFilter = enableFilter
        self.filterRateChange = filterRateChange
        self.offset = 0.0

        self.sensorType = "analog"
        self.value = 0.0

        self._running_avg_count = 10
        self._running_avg_buffer = [0.0] * self._running_avg_count
        self._next_running_avg = 0
        self._elements_in_buffer = 0

        self._lastTask = 0

    def filterValue(self, newValue) -> float | None:
        # Check forbidden values
        if math.isnan(newValue) or math.isinf(newValue) or newValue is None:
            return None

        if not self.enableFilter:
            return newValue

        # Calculate the running average
        self._running_avg_buffer[self._next_running_avg] = newValue
        self._next_running_avg += 1
        if self._next_running_avg >= self._running_avg_count:
            self._next_running_avg = 0
        if self._elements_in_buffer < self._running_avg_count:
            self._elements_in_buffer += 1
        running_avg_value = (
            sum(self._running_avg_buffer[: self._elements_in_buffer])
            / self._elements_in_buffer
        )

        # Calculate the maximum allowed rate of change
        avg_tolerance = running_avg_value * self.filterRateChange

        # Check if the value is within the tolerances
        if (
            newValue < running_avg_value - avg_tolerance
            or newValue > running_avg_value + avg_tolerance
        ):
            return None

        return newValue

    def setValue(self, value):
        filteredValue = self.filterValue(value)
        if filteredValue is not None:
            self.value = filteredValue + self.offset
            self.reportValue()

    def reportValue(self):
        if self.mqttClient and self.mqttClient.is_connected():
            value = "{:.{}f}".format(self.value, self.decimals)
            logger.debug(f"Reporting value: {value}")
            self.mqttClient.publish(
                self.mqttHeader + self.sensorId + "/value",
                value,
                qos=1,
                retain=True,
            )

    def getValue(self):
        pass

    def init(self, mqttHeader, mqttClient):
        super().init(mqttHeader, mqttClient)

        topic = self.mqttHeader + self.sensorId + "/aux/offset"
        mqttClient.subscribe(topic)

        def on_message(client, obj, msg):
            try:
                offset = utils.parseFloat(msg.payload)
            except:
                logger.error(f"Invalid offset value: {msg.payload}")
                return
            self.offset = offset

        mqttClient.message_callback_add(topic, on_message)

    def loop(self):
        now = time.time()
        elapsed = now - self._lastTask
        if elapsed > self.reportValuePeriod:
            self.getValue()
            self._lastTask = now
