import logging
import sys
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.exception import RailRoadAPIError
from app.policy import UserPolicy

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid
from response import make_api_response, make_error_request_response, check_required_api_fields
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIException, APIResourceURL, APINotFoundException


class UsersDevicesAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'users/<string:user_uuid>/devices'

    _config = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UsersDevicesAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST', ]),
            APIResourceURL(base_url=url, resource_name='<string:user_device_uuid>', methods=['GET', 'PUT', 'DELETE']),
        ]
        return api_urls

    def __init__(self, user_policy: UserPolicy, config: dict) -> None:
        super().__init__()
        self._config = config
        self._user_policy = user_policy

    def post(self, user_uuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        is_valid = check_uuid(suuid=user_uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        user_uuid = request_json.get('user_uuid', None)
        device_token = request_json.get('device_token', None)
        device_id = request_json.get('device_id', None)
        platform_id = request_json.get('platform_id', None)
        vpn_type_id = request_json.get('vpn_type_id', None)
        location = request_json.get('location', None)
        is_active = request_json.get('is_active', True)
        virtual_ip = request_json.get('virtual_ip', True)
        device_ip = request_json.get('device_ip', True)
        connected_since = request_json.get('connected_since', True)

        req_fields = {
            'user_uuid': user_uuid,
            'device_id': device_id,
            'platform_id': platform_id,
            'vpn_type_id': vpn_type_id,
            'is_active': is_active,
            'virtual_ip': virtual_ip,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._user_policy.create_user_device(user_uuid=user_uuid, device_id=device_id,
                                                                virtual_ip=virtual_ip,
                                                                device_ip=device_ip, device_token=device_token,
                                                                location=location, is_active=is_active,
                                                                connected_since=connected_since,
                                                                platform_id=platform_id,
                                                                vpn_type_id=vpn_type_id)
            user_device = api_response.data

            self.logger.debug("Get X-Device-Token from headers")
            x_device_token = api_response.headers['X-Device-Token']

            self.logger.debug(f'Get user by uuid: {user_uuid}')
            try:
                api_response = self._user_policy.get_user(suuid=user_uuid)
            except APIException as e:
                self.logger.debug(f"Failed to get user by uuid: {user_uuid}")
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                return make_api_response(data=response_data, http_code=e.http_code)

            user_dict = api_response.data
            self.logger.debug(f'Got user {user_dict}')

            self.logger.debug('Add modify_reason')
            user_dict['modify_reason'] = 'update pin code expire date'

            self.logger.debug('Set pin code activate True')
            user_dict['is_pin_code_activated'] = True

            self._user_policy.update_user(user_dict=user_dict)

            self.logger.debug("Get user device uuid from response of creating user device")
            ud_uuid = user_device['uuid']
            self.logger.debug(f"User Device uuid: {ud_uuid}")

            self.logger.debug("Prepare API URL")
            api_url = self.__api_url__.replace('<string:user_uuid>', user_uuid)
            self.logger.debug(f"API URL: {api_url}")

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.CREATED)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.CREATED)
            location_header = f"{self._config['API_BASE_URI']}/{api_url}/{ud_uuid}"

            self.logger.debug(f"Set Location Header: {location_header}")
            resp.headers['Location'] = location_header

            self.logger.debug(f"Set X-Device-Token: {x_device_token}")
            resp.headers['X-Device-Token'] = x_device_token

            self.logger.debug("Return response")
            return resp
        except APIException as e:
            self.logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def put(self, user_uuid: str, user_device_uuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        device_uuid = request_json.get('uuid', None)

        is_valid_a = check_uuid(suuid=user_device_uuid)
        is_valid_b = check_uuid(suuid=device_uuid)
        if not is_valid_a or not is_valid_b or (user_device_uuid != device_uuid):
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        suuid = request_json.get('uuid', None)
        user_uuid = request_json.get('user_uuid', None)
        device_token = request_json.get('device_token', None)
        device_id = request_json.get('device_id', None)
        platform_id = request_json.get('platform_id', None)
        vpn_type_id = request_json.get('vpn_type_id', None)
        location = request_json.get('location', None)
        is_active = request_json.get('is_active', None)
        virtual_ip = request_json.get('virtual_ip', True)
        device_ip = request_json.get('device_ip', True)
        connected_since = request_json.get('connected_since', True)
        modify_reason = request_json.get('modify_reason', None)

        req_fields = {
            'uuid': suuid,
            'user_uuid': user_uuid,
            'device_token': device_token,
            'device_id': device_id,
            'platform_id': platform_id,
            'vpn_type_id': vpn_type_id,
            'is_active': is_active,
            'virtual_ip': virtual_ip,
            'modify_reason': modify_reason,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            # check does user device exists
            self._user_policy.get_user_device_by_uuid(user_uuid=user_uuid, suuid=user_device_uuid)
            # reuse variable
            req_fields['location'] = location
            req_fields['device_ip'] = device_ip
            req_fields['connected_since'] = connected_since
            self._user_policy.update_user_device(req_fields)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            self.logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def get(self, user_uuid: str, user_device_uuid: str = None) -> Response:
        super(UsersDevicesAPI, self).get(req=request)

        self.logger.debug(f"UsersDevicesAPI get method with parameters user_uuid: {user_uuid}, "
                          f"user_device_uuid: {user_device_uuid}")

        is_valid = check_uuid(suuid=user_uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if user_device_uuid is not None:
            self.logger.debug("user device uuid is not None, get all user devices")

            is_valid = check_uuid(suuid=user_device_uuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

            # get all user devices
            try:
                api_response = self._user_policy.get_user_device_by_uuid(user_uuid=user_uuid, suuid=user_device_uuid)
                self.logger.debug("user device uuid is not None, get all user devices")
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APINotFoundException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.NOT_FOUND,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.NOT_FOUND)
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.BAD_REQUEST)
                return resp
        else:
            # get all user devices
            try:
                api_response = self._user_policy.get_user_devices(user_uuid=user_uuid)
                user_device_list = api_response.data
                response_data = APIResponse(status=api_response.status, code=api_response.code, data=user_device_list)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

    def delete(self, user_uuid: str, user_device_uuid: str) -> Response:
        is_valid_a = check_uuid(suuid=user_device_uuid)
        is_valid_b = check_uuid(suuid=user_uuid)
        if not is_valid_a or not is_valid_b:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        try:
            self._user_policy.delete_user_device(user_uuid=user_uuid, suuid=user_device_uuid)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            self.logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp
