import json
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.service import VPNService

sys.path.insert(0, '../rest_api_library')
from rest import APIException, APIResourceURL
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import check_uuid, make_api_response


class VPNServersAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'VPNServersAPI'
    __api_url__ = 'vpns/servers'

    _vpn_service = None
    _config = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, VPNServersAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET', 'PUT']),
            APIResourceURL(base_url=url, resource_name='type/<int:type_id>', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='status/<int:status_id>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpn_service: VPNService, config: dict) -> None:
        self._vpn_service = vpn_service
        self._config = config

        super().__init__()

    def post(self) -> Response:
        request_json = request.json

        if request_json is None:
            error = RailRoadAPIError.REQUEST_NO_JSON.message
            error_code = RailRoadAPIError.REQUEST_NO_JSON.code
            developer_message = RailRoadAPIError.REQUEST_NO_JSON.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            return make_api_response(data=response_data, http_code=http_code)

        try:
            api_response = self._vpn_service.create_vpn_server(vpnserver=request_json)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=api_response.code)
        # TODO return link to public API, no private API
        # resp.headers['Location'] = '%s/%s/%s' % (self._config['API_BASE_URI'], self.__api_url__, code)
        return resp

    def put(self, suuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            error = RailRoadAPIError.REQUEST_NO_JSON.message
            error_code = RailRoadAPIError.REQUEST_NO_JSON.code
            developer_message = RailRoadAPIError.REQUEST_NO_JSON.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            return make_api_response(data=response_data, http_code=http_code)

        vpnserver_uuid = request_json.get('uuid', None)

        is_valid_suuid = check_uuid(suuid)
        is_valid_vpnserver_uuid = check_uuid(vpnserver_uuid)
        if not is_valid_suuid or not is_valid_vpnserver_uuid:
            error = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.message
            error_code = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.code
            developer_message = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            resp = make_api_response(data=response_data, http_code=http_code)
            return resp

        if suuid != vpnserver_uuid:
            error = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.message
            error_code = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.code
            developer_message = RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            resp = make_api_response(data=response_data, http_code=http_code)
            return resp

        try:
            api_response = self._vpn_service.update_vpn_server(vpnserver=request_json)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code)
        resp = make_api_response(data=response_data, http_code=api_response.code)
        return resp

    def get(self, suuid: str = None, type_id: int = None, status_id: int = None) -> Response:
        super(VPNServersAPI, self).get(req=request)

        is_get_random = request.args.get('random', None)
        if is_get_random is not None:
            try:
                server_uuid = self._vpn_service.get_random_vpn_server(type_id=type_id, status_id=status_id)

                response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                resp.headers['Location'] = '%s/%s/%s' % (self._config['API_BASE_URI'], self.__api_url__, server_uuid)
                return resp
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

        if suuid is None and type_id is None and status_id is None:
            # list of all servers
            try:
                server_list = self._vpn_service.get_vpn_server_list(pagination=self.pagination)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        elif suuid is not None:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                            error=RailRoadAPIError.BAD_USER_IDENTITY.message,
                                            error_code=RailRoadAPIError.BAD_USER_IDENTITY.code)
                resp = make_api_response(data=response_data, http_code=code)
                return resp

            # specific server by uuid
            try:
                server = self._vpn_service.get_vpn_server(suuid=suuid)
                response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK, data=server)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
        elif type_id is not None:
            # list of servers by specific type id
            try:
                server_list = self._vpn_service.get_vpn_server_list_by_type(type_id=type_id, pagination=self.pagination)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        elif status_id is not None:
            # list of servers by specific status id
            try:
                server_list = self._vpn_service.get_vpn_server_list(pagination=self.pagination)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=HTTPStatus.BAD_REQUEST)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.BAD_REQUEST)
            return resp