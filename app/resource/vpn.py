import json
import sys
import uuid as uuidlib
from http import HTTPStatus

from flask import make_response, Response

from app.service import UserService

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse


class VPNServersAPI(ResourceAPI):
    __version__ = 1

    __api_url__ = 'vpnc'

    _config = None

    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config

    def post(self) -> Response:
        resp = make_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, uuid: str = None) -> Response:
        if uuid is None:
            data = [{
                "id": uuidlib.uuid4().__str__(),
                "version": "1",
                "type": "0x336BE3A6",
                "status": "0x01",
                "bandwidth": "239423",
                "load": "30",
                "configuration": None,
                "geo": {
                    "latitude": "1",
                    "longtitude": "2",
                    "decode": {
                        "country": 0,
                        "state": 0,
                        "city": 0,
                        "region": {
                            "common": 0,
                            "dvd": 0,
                            "xbox360": 0,
                            "xboxone": 0,
                            "playstation3": 0,
                            "playstation4": 0,
                            "nintendo": 0
                        }
                    }
                }
            }, {
                "id": uuidlib.uuid4().__str__(),
                "version": "2",
                "type": "0x4E2AA4B7",
                "status": "0x03",
                "bandwidth": "23349423",
                "load": "0",
                "configration": None,
                "geo": {
                    "latitude": "2",
                    "longtitude": "3",
                    "decode": {
                        "country": 0,
                        "state": 0,
                        "city": 0,
                        "region": {
                            "common": 0,
                            "dvd": 0,
                            "xbox360": 0,
                            "xboxone": 0,
                            "playstation3": 0,
                            "playstation4": 0,
                            "nintendo": 0
                        }
                    }
                }
            }]
        else:
            data = {
                "id": uuidlib.uuid4().__str__(),
                "version": "2",
                "type": "0x4E2AA4B7",
                "status": "0x03",
                "bandwidth": "23349423",
                "load": "0",
                "configration": None,
                "geo": {
                    "latitude": "2",
                    "longtitude": "3",
                    "decode": {
                        "country": 0,
                        "state": 0,
                        "city": 0,
                        "region": {
                            "common": 0,
                            "dvd": 0,
                            "xbox360": 0,
                            "xboxone": 0,
                            "playstation3": 0,
                            "playstation4": 0,
                            "nintendo": 0
                        }
                    }
                }
            }
        response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK,
                                    data=data)
        resp = make_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
        return resp
