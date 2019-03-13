import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.policy import VPNServerPolicy

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI, APIResourceURL, APIException
from response import APIResponseStatus, APIResponse
from utils import check_uuid
from response import make_api_response, make_error_request_response


class UsersServersAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'users/<string:user_uuid>/servers'

    _vpn_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UsersServersAPI.__api_url__}"
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

    def put(self, suuid: str) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, user_uuid: str, suuid: str = None) -> Response:
        super(UsersServersAPI, self).get(req=request)

        type_id = request.args.get('type_id', None)
        status_id = request.args.get('status_id', None)
        is_get_random = request.args.get('random', None)

        # TODO make business logic to retrieve only servers for user
        if is_get_random is not None:
            try:
                server_uuid = self._vpn_policy.get_random_vpn_server(type_id=type_id)

                if server_uuid is None:
                    response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.NOT_FOUND)
                    resp = make_api_response(data=response_data, http_code=HTTPStatus.NOT_FOUND)
                    return resp

                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data={'uuid': server_uuid})
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)

                api_url = self.__api_url__.replace("<string:user_uuid>", user_uuid)
                resp.headers['Location'] = f"{self._config['API_BASE_URI']}/{api_url}/{server_uuid}"
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

        if suuid:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

            # specific server by uuid
            try:
                server = self._vpn_policy.get_vpn_server(suuid=suuid)
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK, data=server)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
        else:
            # list of servers
            try:
                server_list = self._vpn_policy.get_vpn_server_list(type_id=type_id, status_id=status_id, pagination=self.pagination)
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK, data=server_list,
                                        limit=self.pagination.limit, offset=self.pagination.offset)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
