import sys
from http import HTTPStatus
from typing import List

import dateutil
from flask import Response, request

from app.exception import RailRoadAPIError
from app.policy import UserPolicy, logging
from app.service import VPNServerConnectionsAPIService

sys.path.insert(0, '../rest_api_library')
from rest import APIResourceURL, APIException, APINotFoundException
from api import ResourceAPI
from response import APIResponseStatus, APIResponse, make_error_request_response, check_required_api_fields
from response import make_api_response

logger = logging.getLogger(__name__)


class VPNSServersConnectionsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = __qualname__
    __api_url__ = 'vpns/servers/<string:server_uuid>/connections'

    _config = None

    _vpnserverconn_api_service = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{VPNSServersConnectionsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
        ]
        return api_urls

    def __init__(self, vpnserverconn_api_service: VPNServerConnectionsAPIService, user_policy: UserPolicy,
                 config: dict) -> None:
        super().__init__()
        self._vpnserverconn_api_service = vpnserverconn_api_service
        self._user_policy = user_policy

        self._config = config

    def post(self, server_uuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        server = request_json.get('server', None)
        server_uuid = server.get('uuid', None)
        server_type = server.get('type', None)
        # TODO think about user count
        users_count = server.get('users_count', None)

        user_list = request_json.get('users', None)

        req_fields = {
            'server': server,
            'type': server_type,
            'users_count': users_count,
            'uuid': server_uuid,
            'users': user_list,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            for user in user_list:
                email = user.get('email')
                bytes_i = user.get('bytes_i')
                bytes_o = user.get('bytes_o')
                connected_since = user.get('connected_since')
                connected_since = dateutil.parser.parse(connected_since)
                device_ip = user.get('device_ip')
                virtual_ip = user.get('virtual_ip')

                api_response = self._user_policy.get_user(email=email)
                user_d = api_response.data
                user_uuid = user_d.get('uuid')

                api_response = self._user_policy.get_user_devices(user_uuid=user_uuid)
                user_devices = api_response.data

                user_device = None
                for ud in user_devices:
                    if ud.get('virtual_ip') == virtual_ip:
                        user_device = ud
                        user_device['connected_since'] = connected_since
                        user_device['device_ip'] = device_ip
                        user_device['modify_reason'] = 'update connection information'
                        break

                if user_device is None:
                    logger.error(f"We did not found user device for received connection information")
                    resp = make_error_request_response(http_code=HTTPStatus.NOT_FOUND)
                    return resp

                try:
                    self._user_policy.update_user_device(user_device=user_device)
                except APIException as e:
                    logger.error(e)
                    logger.error(f"Error while update user device: {user_device}")

                try:
                    api_response = self._vpnserverconn_api_service.get_by_server_and_user(server_uuid=server_uuid,
                                                                                          user_uuid=user_uuid)
                    server_connection = api_response.data
                    logger.debug(f"Got VPN server connection: {server_connection}")

                    server_connection['device_ip'] = device_ip
                    server_connection['virtual_ip'] = virtual_ip
                    server_connection['bytes_i'] = bytes_i
                    server_connection['bytes_o'] = bytes_o
                    server_connection['connected_since'] = connected_since
                    server_connection['is_connected'] = True
                    server_connection['modify_reason'] = 'update server connection'
                    try:
                        self._vpnserverconn_api_service.update(server_connection_dict=server_connection)
                    except APIException as e:
                        logger.error("Error while updating vpn server connection")
                        logger.error(e)
                        response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                                    errors=e.errors)
                        resp = make_api_response(data=response_data, http_code=e.http_code)
                        return resp
                except APINotFoundException as e:
                    logger.debug(e.serialize())
                    logger.error("Error when getting vpn server connection")
                    response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                                errors=e.errors)
                    resp = make_api_response(data=response_data, http_code=e.http_code)
                    return resp
                except APIException:
                    logger.info("No existed vpn server connection.")
                    try:
                        self._vpnserverconn_api_service.create(server_uuid=server_uuid,
                                                               user_uuid=user_device.get('user_uuid'),
                                                               user_device_uuid=user_device.get('uuid'),
                                                               device_ip=device_ip, virtual_ip=virtual_ip,
                                                               bytes_i=bytes_i, bytes_o=bytes_o,
                                                               is_connected=True,
                                                               connected_since=connected_since)
                    except APIException as e:
                        logger.error(e)
                        logger.error(f"Error while create server connection")
                        response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                                    errors=e.errors)
                        resp = make_api_response(data=response_data, http_code=e.http_code)
                        return resp

                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp

        except APIException as e:
            logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def put(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp