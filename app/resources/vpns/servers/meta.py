import json
import sys
from http import HTTPStatus

from flask import make_response, Response, request

from app import VPNServersMetaService
from app.exception import RailRoadAPIError

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import check_uuid, JSONDecimalEncoder


class VPNServersMetaAPI(ResourceAPI):
    __version__ = 1

    __api_url__ = 'vpn/servers/meta'

    _config = None

    vpnserversmeta_service = None

    def __init__(self, vpnserversmeta_service: VPNServersMetaService, config: dict) -> None:
        super().__init__()
        self.vpnserversmeta_service = vpnserversmeta_service

        self._config = config

    def post(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        api_response = self.vpnserversmeta_service.get_meta()

        response_data = APIResponse(status=APIResponseStatus.success.value, code=api_response.code,
                                    data=api_response.data, headers=api_response.headers)
        resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
        return resp
