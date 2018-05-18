import json
import sys
import uuid as uuidlib
from http import HTTPStatus

from flask import make_response, Response, request

from app.exception import RailRoadAPIError
from app.service import UserService

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import check_uuid


class VPNServersAPI(ResourceAPI):
    __version__ = 1

    __api_url__ = 'vpn/servers'

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

    def get(self, uuid: str = None, status: str = None) -> Response:
        if 'version' in request.args:
            data = {
                'version': 42
            }
            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK,
                                        data=data)
            resp = make_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
            return resp
        if uuid is None and status is None:
            # list of all servers
            data = [{
                "id": "16fd2706-8baf-433b-82eb-8c7fada847da",
                "version": "1",
                "type": "1",
                "status": "2",
                "bandwidth": "40MBit",
                "load": "30",
                "configuration": None,
                "geo": {
                    "latitude": "55.7558",
                    "longitude": "37.6173",
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
                "id": "8d0359a4-64d1-4906-b113-2e36259dd128",
                "version": "2",
                "type": "2",
                "status": "3",
                "bandwidth": "23MBit",
                "load": "0",
                "configuration": None,
                "geo": {
                    "latitude": "55.7558",
                    "longitude": "37.6173",
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
            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK,
                                        data=data)
            resp = make_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
        elif uuid is not None:
            # specific server by uuid
            b = check_uuid(uuid=uuid)
            if not b:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                            error=RailRoadAPIError.BAD_SERVER_IDENTITY.phrase,
                                            error_code=RailRoadAPIError.BAD_SERVER_IDENTITY)

                resp = make_response(json.dumps(response_data.serialize()), code)
                return resp
            data = {
                "id": uuid,
                "version": "2",
                "type": "2",
                "status": "1",
                "bandwidth": "100GBit",
                "load": "0",
                "configuration": None,
                "geo": {
                    "latitude": "55.7558",
                    "longitude": "37.6173",
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
        elif status is not None:
            # list of all servers by status
            if status != 'new':
                data = {}
            else:
                data = [{
                    "id": "16fd2706-8baf-433b-82eb-8c7fada847da",
                    "version": "1",
                    "type": "1",
                    "status": "1",
                    "bandwidth": "40MBit",
                    "load": "30",
                    "configuration": None,
                    "geo": {
                        "latitude": "55.7558",
                        "longitude": "37.6173",
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
                    "id": "8d0359a4-64d1-4906-b113-2e36259dd128",
                    "version": "2",
                    "type": "2",
                    "status": "1",
                    "bandwidth": "23MBit",
                    "load": "0",
                    "configuration": None,
                    "geo": {
                        "latitude": "55.7558",
                        "longitude": "37.6173",
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
            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK,
                                        data=data)
            resp = make_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=HTTPStatus.BAD_REQUEST)
            resp = make_response(json.dumps(response_data.serialize()), HTTPStatus.BAD_REQUEST)
        return resp
