import logging
import pickle
import uuid

logger = logging.getLogger(__name__)

DATA_PATH = "../device_data/data.p"

DEVICE_INTERNAL_ID = str(uuid.getnode())


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
