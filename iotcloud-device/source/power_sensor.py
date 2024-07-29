import logging
import requests
import analog_sensor

import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


class Power_Sensor(analog_sensor.Analog_Sensor):
    def __init__(self, sensorId, sensorName, powerMeterURL, measurement):
        super().__init__(
            sensorId, sensorName, reportValuePeriod=1.0, decimals=0, enableFilter=False
        )

        self.powerMeterURL = powerMeterURL
        self._sensorId = measurement

    def getValue(self) -> float | None:
        # Get the xml file from the power meter
        try:
            response = requests.get(
                f"http://{self.powerMeterURL}/en/status.xml", timeout=10
            )
            data = response.content
        except:
            logger.error(
                "Unable to obtain any response from %s", self.powerMeterURL, exc_info=True
            )
            return

        # Parse the power meter xml file
        try:
            tree = ET.fromstring(data)
        except ET.ParseError as e:
            logger.error(f"Could parse the data from the sensor: {self._sensorId}")
            return None

        # Get the value
        for item in tree:
            sensorId = item.tag
            sensorValue = item.text

            if sensorId == self._sensorId:
                if sensorValue is not None:
                    self.setValue(float(sensorValue))
                break
