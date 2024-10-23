import requests
import urllib3
from api.logging_config import setup_logging

from api.utils import JsonException

logger = setup_logging(__name__)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def rest_call(url: str, method: str, headers=None, payload=None):
    """
    :param url:
    :param method:
    :param headers:
    :param payload:
    :return:
    """
    operations = {
        "get": lambda: requests.get(url, headers=headers, verify=False),
        "post": lambda: requests.post(url, headers=headers, data=payload, verify=False),
        "put": lambda: requests.put(url, json=payload, verify=False),
        "delete": lambda: requests.delete(url, headers=headers, verify=False),
    }
    try:
        res = operations[method]()
        if res.status_code in [401, 403]:
            raise JsonException(res.json(), res.status_code)
        elif (
            "Content-Type" in res.headers
            and "application/json" in res.headers["Content-Type"]
        ):
            return res.json()
        else:
            return {}
    except requests.exceptions.RequestException as err:
        logger.error(f"Request error: {err}")
        raise Exception(err)
    except JsonException as err:
        logger.error(f"JsonException In rest call Function-  {err.detail}")
        raise JsonException(detail=err.detail, status_code=err.status_code) from err
    except Exception as err:
        logger.error(f"Exception In rest call Function-  {err}")
        raise err
