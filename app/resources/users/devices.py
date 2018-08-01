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
from rest import APIException, APIResourceURL

logger = logging.getLogger(__name__)


class UserDeviceAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'UserDeviceAPI'
    __api_url__ = 'users/<string:user_uuid>/devices'

    _config = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UserDeviceAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST', ]),
            APIResourceURL(base_url=url, resource_name='<string:user_device_uuid>', methods=['GET', 'PUT', ]),
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
        location = request_json.get('location', None)
        is_active = request_json.get('is_active', True)

        req_fields = {
            'user_uuid': user_uuid,
            'device_id': device_id,
            'is_active': is_active,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._user_policy.create_user_device(user_uuid=user_uuid, device_id=device_id,
                                                                device_token=device_token, location=location,
                                                                is_active=is_active)
            user_device = api_response.data

            logger.debug("Get X-Device-Token from headers")
            x_device_token = api_response.headers['X-Device-Token']

            logger.debug(f'Get user by uuid: {user_uuid}')
            try:
                api_response = self._user_policy.get_user(suuid=user_uuid)
            except APIException as e:
                logger.debug(f"Failed to get user by uuid: {user_uuid}")
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                return make_api_response(data=response_data, http_code=e.http_code)

            user_dict = api_response.data
            logger.debug(f'Got user {user_dict}')

            logger.debug('Add modify_reason')
            user_dict['modify_reason'] = 'update pin code expire date'

            logger.debug('Set pin code activate True')
            user_dict['is_pin_code_activated'] = True

            self._user_policy.update_user(user_dict=user_dict)

            logger.debug("Get user device uuid from response of creating user device")
            ud_uuid = user_device['uuid']
            logger.debug(f"User Device uuid: {ud_uuid}")

            logger.debug("Prepare API URL")
            api_url = self.__api_url__.replace('<string:user_uuid>', user_uuid)
            logger.debug(f"API URL: {api_url}")

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.CREATED)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.CREATED)
            location_header = f"{self._config['API_BASE_URI']}/{api_url}/{ud_uuid}"

            logger.debug(f"Set Location Header: {location_header}")
            resp.headers['Location'] = location_header

            logger.debug(f"Set X-Device-Token: {x_device_token}")
            resp.headers['X-Device-Token'] = x_device_token

            logger.debug("Return response")
            return resp
        except APIException as e:
            logging.debug(e.serialize())
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
        location = request_json.get('location', None)
        is_active = request_json.get('is_active', None)
        modify_reason = request_json.get('modify_reason', None)

        req_fields = {
            'uuid': suuid,
            'user_uuid': user_uuid,
            'device_token': device_token,
            'device_id': device_id,
            'is_active': is_active,
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
            self._user_policy.update_user_device(req_fields)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def get(self, user_uuid: str, user_device_uuid: str = None) -> Response:
        super(UserDeviceAPI, self).get(req=request)

        is_valid = check_uuid(suuid=user_uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if user_device_uuid is not None:
            is_valid = check_uuid(suuid=user_device_uuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)
            # get all user device by uuid
            api_response = self._user_policy.get_user_device_by_uuid(user_uuid=user_uuid, suuid=user_device_uuid)
            if api_response.is_ok:
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                            data=api_response.data)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            else:
                response_data = APIResponse(status=api_response.status, code=api_response.code,
                                            data=api_response.data, errors=api_response.errors)
                resp = make_api_response(data=response_data, http_code=api_response.code)
                return resp
        else:
            # get all user devices
            try:
                api_response = self._user_policy.get_user_devices(user_uuid=user_uuid)
                if api_response.is_ok:
                    subs = api_response.data
                    response_data = APIResponse(status=api_response.status, code=api_response.code,
                                                data=subs)
                    resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                else:
                    response_data = APIResponse(status=api_response.status, code=api_response.code,
                                                data=api_response.data,
                                                errors=api_response.errors)
                    resp = make_api_response(data=response_data, http_code=api_response.code)
                return resp
            except APIException as e:
                logging.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
