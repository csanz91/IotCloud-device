import logging
import logging.config
import threading

import falcon

import device_setup_api
import utils
import advise_device
import device

# Logging setup
logger = logging.getLogger()
handler = logging.handlers.RotatingFileHandler(
    "../logs/device.log", mode="a", maxBytes=1024 * 1024 * 10, backupCount=2
)
formatter = logging.Formatter(
    "%(asctime)s <%(levelname).1s> %(funcName)s:%(lineno)s: %(message)s"
)
logger.setLevel(logging.INFO)
handler.setFormatter(formatter)
logger.addHandler(handler)

app = falcon.API()
app.req_options.auto_parse_form_urlencoded = True

logger.info("Starting")


app.add_route("/getDeviceInfo", device_setup_api.Info())
app.add_route("/deviceSetup", device_setup_api.Setup())

adviseDeviceThread = threading.Thread(target=advise_device.adviceDevice)
adviseDeviceThread.start()

runDeviceThread = threading.Thread(target=device.runDevice)
runDeviceThread.start()
