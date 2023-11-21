import logging
import pickle
import uuid

logger = logging.getLogger(__name__)

DATA_PATH = "../device_data/data.p"

DEVICE_INTERNAL_ID = "202481596676681"


def decodeBoolean(value):
    assert value.lower() in ["true", "false"]
    state = value.lower() == "true"
    return state


def decodeStatus(value):
    assert value.lower() in ["online", "offline"]
    status = value.lower() == "online"
    return status


def notIsNaN(num):
    assert num == num


def parseFloat(value):
    parsedFloat = float(value)
    notIsNaN(parsedFloat)
    return parsedFloat


def decodeColor(color):
    r = int(color[2:4], 16)
    g = int(color[4:6], 16)
    b = int(color[6:8], 16)

    return r, g, b


def getResponseModel(result, data=None):
    response = {"result": result}
    if data is not None:
        response["data"] = data

    return response


def saveDeviceData(data):
    with open(DATA_PATH, "wb") as fp:
        pickle.dump(data, fp, protocol=pickle.HIGHEST_PROTOCOL)


def getDeviceData():
    try:
        with open(DATA_PATH, "rb") as fp:
            data = pickle.load(fp)
            return data
    except FileNotFoundError:
        return


def getDeviceId():
    return DEVICE_INTERNAL_ID
