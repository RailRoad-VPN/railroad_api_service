import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.policy import VPNServerPolicy

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI, APIResourceURL, APIException
from response import APIResponseStatus, APIResponse, make_error_request_response
from utils import check_uuid
from response import make_api_response


class UsersServersConditionsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = __qualname__
    __api_url__ = 'users/<string:user_uuid>/servers/conditions'

    _vpn_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UsersServersConditionsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpn_service: VPNServerPolicy, *args) -> None:
        super().__init__(*args)
        self._vpn_policy = vpn_service

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, user_uuid: str, suuid: str = None) -> Response:
        super(UsersServersConditionsAPI, self).get(req=request)

        type_id = request.args.get('type', None)
        status_id = request.args.get('status', None)

        # TODO make business logic to retrieve only servers for user
        if suuid is None and type_id is None and status_id is None:
            # list of all servers
            try:
                server_list = self._vpn_policy.get_vpn_server_condition_list(pagination=self.pagination)
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        elif suuid is not None:
            # specific server by uuid
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=code,
                                            error=RailRoadAPIError.BAD_USER_IDENTITY.message,
                                            error_code=RailRoadAPIError.BAD_USER_IDENTITY)
                resp = make_api_response(data=response_data, http_code=code)
                return resp
            try:
                server = self._vpn_policy.get_vpn_server_condition(suuid=suuid)
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK, data=server)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        elif type_id is not None:
            # list of all servers with specific type
            try:
                server_list = self._vpn_policy.get_vpn_server_condition_list_by_type(type_id=type_id,
                                                                                     pagination=self.pagination)
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        elif status_id is not None:
            # list of all servers with specific status
            try:
                server_list = self._vpn_policy.get_vpn_server_condition_list_by_status(status_id=status_id,
                                                                                       pagination=self.pagination)
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        else:
            resp = make_api_response(http_code=HTTPStatus.BAD_REQUEST)
            return resp
