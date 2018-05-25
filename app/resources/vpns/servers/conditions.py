import json
import sys

from http import HTTPStatus

from flask import Response, request

from app.exception import RailRoadAPIError

from app.service import VPNService

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import check_uuid, make_api_response


class VPNServerConditionsAPI(ResourceAPI):
    __version__ = 1

    __api_url__ = 'vpns/servers/conditions'

    _vpn_service = None
    _config = None

    def __init__(self, vpn_service: VPNService, config: dict) -> None:
        self._vpn_service = vpn_service
        self._config = config

        super().__init__()

    def post(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, suuid: str = None) -> Response:
        super(VPNServerConditionsAPI, self).get(req=request)
        if suuid is None:
            # list of all servers
            try:
                server_list = self._vpn_service.get_vpn_server_condition_list(pagination=self.pagination)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
                resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
            return resp
        elif suuid is not None:
            # specific server by uuid
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                            error=RailRoadAPIError.BAD_USER_IDENTITY.phrase,
                                            error_code=RailRoadAPIError.BAD_USER_IDENTITY)
                resp = make_api_response(json.dumps(response_data.serialize()), code)
                return resp

            try:
                server = self._vpn_service.get_vpn_server_condition(suuid=suuid)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
                resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK, data=server)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
            return resp
        else:
            resp = make_api_response('', HTTPStatus.BAD_REQUEST)
        return resp
