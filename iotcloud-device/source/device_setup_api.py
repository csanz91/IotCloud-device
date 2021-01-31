import logging

import falcon
import utils
import device

logger = logging.getLogger(__name__)


class Info:
    def on_get(self, req, resp):
        resp.media = utils.getResponseModel(True, device.device.exportData())


class Setup:
    def on_post(self, req, resp):
        try:
            assert req.media["token"]
            assert req.media["deviceId"]
            assert req.media["locationId"]
            data = {
                "token": req.media["token"],
                "deviceId": req.media["deviceId"],
                "locationId": req.media["locationId"],
            }
            utils.saveDeviceData(data)
            device.restartDevice()
        except:
            logger.error("Bad data received.", exc_info=True)
            raise falcon.HTTPBadRequest(
                "Bad Request", "The request can not be completed."
            )

        resp.media = utils.getResponseModel(True)
