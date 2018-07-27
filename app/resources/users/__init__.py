import datetime
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


class UserAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'UserAPI'
    __api_url__ = 'users'

    _config = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, UserAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['POST']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET', 'PUT']),
            APIResourceURL(base_url=url, resource_name='uuid/<string:suuid>', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='email/<string:email>', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='pincode/<string:pin_code>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, user_policy: UserPolicy, config: dict) -> None:
        super().__init__()
        self._config = config
        self._user_policy = user_policy

    def post(self) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        email = request_json.get('email', None)
        password = request_json.get('password', None)
        is_expired = request_json.get('is_expired', False)
        is_locked = request_json.get('is_locked', False)
        is_password_expired = request_json.get('is_password_expired', False)
        enabled = request_json.get('enabled', True)

        user_json = {
            'email': email,
            'password': password
        }

        error_fields = check_required_api_fields(user_json)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._user_policy.get_user(email=email)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code == HTTPStatus.OK:
            # user exist
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.USER_EMAIL_BUSY)

        user_json['password'] = password
        user_json['is_expired'] = is_expired
        user_json['is_locked'] = is_locked
        user_json['is_password_expired'] = is_password_expired
        user_json['enabled'] = enabled

        try:
            api_response = self._user_policy.create_user(email=email, password=password, is_expired=is_expired,
                                                         is_locked=is_locked, is_password_expired=is_password_expired,
                                                         enabled=enabled)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code == HTTPStatus.CREATED:
            user_uuid = api_response.headers['Location'].split('/')[-1]
            response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code)
            resp = make_api_response(data=response_data, http_code=api_response.code)
            resp.headers['Location'] = '%s/%s/uuid/%s' % (self._config['API_BASE_URI'], self.__api_url__, user_uuid)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                        errors=api_response.errors, headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=api_response.code)
        return resp

    def put(self, suuid: str = None) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        user_uuid = request_json.get('uuid', None)

        is_valid_a = check_uuid(suuid=suuid)
        is_valid_b = check_uuid(suuid=user_uuid)
        if not is_valid_a or not is_valid_b or (user_uuid != suuid):
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        email = request_json.get('email', None)
        password = request_json.get('password', None)
        is_expired = request_json.get('is_expired', None)
        is_locked = request_json.get('is_locked', None)
        is_password_expired = request_json.get('is_password_expired', None)
        enabled = request_json.get('enabled', None)
        pin_code = request_json.get('pin_code', None)
        pin_code_expire_date = request_json.get('pin_code_expire_date', None)
        modify_reason = request_json.get('modify_reason', None)

        user_dict = {
            'uuid': suuid,
            'email': email,
            'password': password,
            'modify_reason': modify_reason,
            'is_expired': is_expired,
            'is_locked': is_locked,
            'is_password_expired': is_password_expired,
            'enabled': enabled,
        }

        error_fields = check_required_api_fields(user_dict)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        if pin_code is not None and pin_code_expire_date is None:
            now = datetime.datetime.now()
            pin_code_expire_date = now + datetime.timedelta(minutes=30)

        try:
            api_response = self._user_policy.get_user(suuid=suuid)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if not api_response.is_ok:
            # user does not exist
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.USER_NOT_EXIST)

        user_dict['pin_code'] = pin_code
        user_dict['pin_code_expire_date'] = pin_code_expire_date

        try:

            api_response = self._user_policy.update_user(user_dict=user_dict)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.is_ok:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        headers=api_response.headers)
            # 200 OK - means some content in body
            if api_response.code == HTTPStatus.OK:
                response_data.data = api_response.data
        else:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        errors=api_response.errors, headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=api_response.code)
        return resp

    def get(self, suuid: str = None, email: str = None, pin_code: str = None) -> Response:
        super(UserAPI, self).get(req=request)
        if suuid is not None:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if suuid is None and email is None and pin_code is None:
            # find all users - no parameters set
            return make_error_request_response(HTTPStatus.METHOD_NOT_ALLOWED, err=RailRoadAPIError.PRIVATE_METHOD)

        # uuid or email or pin_code is not None, let's get user
        try:
            api_response = self._user_policy.get_user(suuid=suuid, email=email, pin_code=pin_code)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if not api_response.is_ok:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        headers=api_response.headers, errors=api_response.errors)
            resp = make_api_response(data=response_data, http_code=api_response.code)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data,
                                    headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
