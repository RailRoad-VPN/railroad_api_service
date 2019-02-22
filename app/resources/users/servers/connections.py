import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.policy import UserPolicy
from app.service import VPNServerConnectionsAPIService
from rest import APIException, APIResourceURL

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid
from api import ResourceAPI
from response import APIResponseStatus, APIResponse, make_error_request_response, check_required_api_fields
from response import make_api_response


class UsersServersConnectionsAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'users/<string:user_uuid>/servers/<string:server_uuid>/connections'

    _connections_api_service = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UsersServersConnectionsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET', 'PUT']),
        ]
        return api_urls

    def __init__(self, vpnserversconnections_service: VPNServerConnectionsAPIService, user_policy: UserPolicy,
                 *args) -> None:
        super().__init__(*args)
        self._connections_api_service = vpnserversconnections_service
        self._user_policy = user_policy

    def post(self, server_uuid: str, user_uuid: str) -> Response:
        super(UsersServersConnectionsAPI, self).post(req=request)

        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        user_device_uuid = request_json.get('user_device_uuid')
        bytes_i = request_json.get('bytes_i')
        bytes_o = request_json.get('bytes_o')
        connected_since = request_json.get('connected_since')
        device_ip = request_json.get('device_ip')
        is_connected = request_json.get('is_connected', True)
        virtual_ip = request_json.get('virtual_ip')

        try:
            response_data = self._connections_api_service.create(server_uuid=server_uuid, user_uuid=user_uuid,
                                                                 device_ip=device_ip,
                                                                 virtual_ip=virtual_ip, bytes_i=bytes_i,
                                                                 bytes_o=bytes_o,
                                                                 is_connected=is_connected,
                                                                 connected_since=connected_since,
                                                                 user_device_uuid=user_device_uuid)
            self.logger.debug("parse location to get connection uuid")
            connection_uuid = response_data.headers['Location'].split("/")[-1]
            self.logger.debug(f"connection uuid: {connection_uuid}")

            self.logger.debug(f"{self.__class__}: Prepare API URL")
            api_url = self.__api_url__.replace('<string:user_uuid>', user_uuid)
            api_url = api_url.replace('<string:server_uuid>', server_uuid)
            self.logger.debug(f"{self.__class__}: API URL: {api_url}")

            resp = make_api_response(data=response_data, http_code=HTTPStatus.CREATED)
            location_header = f"{self._config['API_BASE_URI']}/{api_url}/{connection_uuid}"

            self.logger.debug(f"{self.__class__}: Set Location Header: {location_header}")
            resp.headers['Location'] = location_header
            return resp
        except APIException as e:
            self.logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                        errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def put(self, server_uuid: str, user_uuid: str, suuid: str) -> Response:
        super(UsersServersConnectionsAPI, self).put(req=request)

        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        bytes_i = request_json.get('bytes_i', None)
        bytes_o = request_json.get('bytes_o', None)
        connected_since = request_json.get('connected_since', None)
        device_ip = request_json.get('device_ip', None)
        is_connected = request_json.get('is_connected', None)
        user_device_uuid = request_json.get('user_device_uuid', None)
        user_uuid = request_json.get('user_uuid', None)
        uuid = request_json.get('uuid', None)
        virtual_ip = request_json.get('virtual_ip', None)

        req_fields = {
            'bytes_i': bytes_i,
            'bytes_o': bytes_o,
            'is_connected': is_connected,
            'server_uuid': server_uuid,
            'uuid': suuid
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            self._vpnserverconn_api_service.update(server_connection_dict=req_fields)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=e.errors)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

    def get(self, server_uuid: str, user_uuid: str, suuid: str = None) -> Response:
        super(UsersServersConnectionsAPI, self).get(req=request)

        if suuid is None:
            try:
                api_response = self._connections_api_service.get_by_server_and_user(server_uuid=server_uuid,
                                                                                    user_uuid=user_uuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
        else:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=code,
                                            error=RailRoadAPIError.BAD_USER_IDENTITY.message,
                                            error_code=RailRoadAPIError.BAD_USER_IDENTITY)
                resp = make_api_response(data=response_data, http_code=code)
                return resp
            try:
                api_response = self._connections_api_service.get_by_server_and_suuid(suuid=suuid,
                                                                                     server_uuid=server_uuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
