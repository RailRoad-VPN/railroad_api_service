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


class VPNServersAPI(ResourceAPI):
    __version__ = 1

    __api_url__ = 'vpns/servers'

    _vpn_service = None
    _config = None

    def __init__(self, vpn_service: VPNService, config: dict) -> None:
        self._vpn_service = vpn_service
        self._config = config

        super().__init__()

    def post(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self, suuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            error = RailRoadAPIError.REQUEST_NO_JSON.phrase
            error_code = RailRoadAPIError.REQUEST_NO_JSON
            developer_message = RailRoadAPIError.REQUEST_NO_JSON.description
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            return make_api_response(json.dumps(response_data.serialize()), http_code)

        vpnserver_suuid = request_json.get('uuid', None)

        is_valid_suuid = check_uuid(suuid)
        is_valid_vpnserver_suuid = check_uuid(vpnserver_suuid)
        if not is_valid_suuid or not is_valid_vpnserver_suuid:
            error = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.phrase
            error_code = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR
            developer_message = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.description
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            resp = make_api_response(json.dumps(response_data.serialize()), http_code)
            return resp

        if suuid != vpnserver_suuid:
            error = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.phrase
            error_code = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR
            developer_message = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.description
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            resp = make_api_response(json.dumps(response_data.serialize()), http_code)
            return resp

        try:
            self._vpn_service.update_vpn_server(vpnserver=request_json)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code,
                                        error=e.message, error_code=e.code)
            resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
            return resp

        resp = make_api_response('', HTTPStatus.NO_CONTENT)
        return resp

    def get(self, suuid: str = None) -> Response:
        super(VPNServersAPI, self).get(req=request)
        if suuid is None:
            # list of all servers
            try:
                server_list = self._vpn_service.get_vpn_server_list(pagination=self.pagination)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code,
                                            error=e.message, error_code=e.code)
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
                server = self._vpn_service.get_vpn_server(suuid=suuid)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code,
                                            error=e.message, error_code=e.code)
                resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK, data=server)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
            return resp
        else:
            resp = make_api_response('', HTTPStatus.BAD_REQUEST)
        return resp
