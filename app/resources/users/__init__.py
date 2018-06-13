import sys
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.exception import RailRoadAPIError
from app.service import UserAPIService

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid, make_api_response, make_error_request_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIException, APIResourceURL


class UserAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'UserAPI'
    __api_url__ = 'users'

    _config = None
    _user_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, UserAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['PUT']),
            APIResourceURL(base_url=url, resource_name='uuid/<string:suuid>', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='email/<string:email>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, user_service: UserAPIService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._user_service = user_service

    def post(self) -> Response:
        request_json = request.json

        user_email = request_json['email']

        try:
            api_response = self._user_service.get_user(email=user_email)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code == HTTPStatus.OK:
            # user exist
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.USER_EMAIL_BUSY)

        try:
            api_response = self._user_service.create_user(user_json=request_json)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code == HTTPStatus.CREATED:
            user_uuid = api_response.data['uuid']
            resp = make_api_response(http_code=HTTPStatus.CREATED)
            resp.headers['Location'] = '%s/%s/uuid/%s' % (self._config['API_BASE_URI'], self.__api_url__, user_uuid)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                        errors=api_response.errors, headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=api_response.code)
        return resp

    def put(self, uuid: str = None) -> Response:
        is_valid = check_uuid(suuid=uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        request_json = request.json

        try:
            api_response = self._user_service.get_user(suuid=uuid)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.status == APIResponseStatus.failed.status:
            # user does not exist
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.USER_NOT_EXIST)
        try:
            api_response = self._user_service.update_user(user_json=request_json)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code in [HTTPStatus.OK, HTTPStatus.NO_CONTENT]:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        headers=api_response.headers)
            # 200 OK - means some content in body
            if api_response.code == HTTPStatus.OK:
                response_data.data = api_response.data
        else:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        error=api_response.error, error_code=api_response.error_code,
                                        headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=api_response.code)
        return resp

    def get(self, suuid: str = None, email: str = None) -> Response:
        super(UserAPI, self).get(req=request)
        if suuid is not None:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if suuid is None and email is None:
            # find all users - no parameters set
            return make_error_request_response(HTTPStatus.METHOD_NOT_ALLOWED, err=RailRoadAPIError.PRIVATE_METHOD)

        # uuid or email is not None, let's get user
        try:
            api_response = self._user_service.get_user(suuid=suuid, email=email)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.status == APIResponseStatus.failed.status:
            response_data = APIResponse(status=api_response.status, code=HTTPStatus.BAD_REQUEST,
                                        headers=api_response.headers, errors=api_response.errors)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.BAD_REQUEST)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data,
                                    headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
