import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response

from app.exception import RailRoadAPIError
from app.service import VPNServerConnectionsAPIService
from rest import APIException, APIResourceURL
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse, make_error_request_response
from response import make_api_response

logger = logging.getLogger(__name__)


class VPNServersConnectionsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'VPNServersConnectionsAPI'
    __api_url__ = 'users/<string:user_uuid>/servers/<string:server_uuid>/connections'

    _config = None

    _connections_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNServersConnectionsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpnserversconnections_service: VPNServerConnectionsAPIService, config: dict) -> None:
        super().__init__()
        self._connections_api_service = vpnserversconnections_service
        self._config = config

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, server_uuid: str, user_uuid: str, suuid: str = None) -> Response:
        if suuid is None:
            try:
                api_response = self._connections_api_service.get_by_server_and_user(server_uuid=server_uuid,
                                                                                    user_uuid=user_uuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                logger.debug(e.serialize())
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
                api_response = self._connections_api_service.get_by_suuid(suuid=suuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
