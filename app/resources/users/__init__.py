import json
import sys
from http import HTTPStatus

from flask import request, Response

from app.exception import RailRoadAPIError
from app.service import UserService

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid, make_api_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIException


class UserAPI(ResourceAPI):
    __version__ = 1

    __api_url__ = 'users'

    _config = None
    _user_service = None

    def __init__(self, user_service: UserService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._user_service = user_service

    def post(self) -> Response:
        request_json = request.json

        user_email = request_json['email']

        try:
            api_response = self._user_service.get_user(email=user_email)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, error=e.message,
                                        error_code=e.code)
            resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
            return resp

        if api_response.code == HTTPStatus.OK:
            # user exist
            code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=code, headers=api_response.headers,
                                        error=RailRoadAPIError.USER_EMAIL_BUSY.phrase,
                                        error_code=RailRoadAPIError.USER_EMAIL_BUSY)
            resp = make_api_response(json.dumps(response_data.serialize()), code)
            return resp

        try:
            api_response = self._user_service.create_user(user_json=request_json)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, error=e.message,
                                        error_code=e.code)
            resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
            return resp

        if api_response.code == HTTPStatus.CREATED:
            user_uuid = api_response.data['uuid']
            resp = make_api_response("", HTTPStatus.CREATED)
            resp.headers['Location'] = '%s/%s/uuid/%s' % (self._config['API_BASE_URI'], self.__api_url__, user_uuid)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=api_response.code,
                                        errors=api_response.errors, headers=api_response.headers)
            resp = make_api_response(json.dumps(response_data.serialize()), api_response.code)
        return resp

    def put(self, uuid: str = None) -> Response:
        is_valid = check_uuid(suuid=uuid)
        if not is_valid:
            code = HTTPStatus.NOT_FOUND
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                        error=RailRoadAPIError.BAD_USER_IDENTITY.phrase,
                                        error_code=RailRoadAPIError.BAD_USER_IDENTITY)

            resp = make_api_response(json.dumps(response_data.serialize()), code)
            return resp

        request_json = request.json

        try:
            api_response = self._user_service.get_user(suuid=uuid)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, error=e.message,
                                        error_code=e.code)
            resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
            return resp

        if api_response.status == APIResponseStatus.failed.value:
            # user does not exist
            code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                        error=RailRoadAPIError.USER_NOT_EXIST.phrase,
                                        error_code=RailRoadAPIError.USER_NOT_EXIST)
            resp = make_api_response(json.dumps(response_data.serialize()), code)
            return resp

        try:
            api_response = self._user_service.update_user(user_json=request_json)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code,
                                        error=e.message, error_code=e.code)
            resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
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
        resp = make_api_response(json.dumps(response_data.serialize()), api_response.code)
        return resp

    def get(self, suuid: str = None, email: str = None) -> Response:
        super(UserAPI, self).get(req=request)
        if suuid is not None:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                            error=RailRoadAPIError.BAD_USER_IDENTITY.phrase,
                                            error_code=RailRoadAPIError.BAD_USER_IDENTITY)

                resp = make_api_response(json.dumps(response_data.serialize()), code)
                return resp

        if suuid is None and email is None:
            # find all users - no parameters set
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                        error=RailRoadAPIError.PRIVATE_METHOD.phrase,
                                        error_code=RailRoadAPIError.PRIVATE_METHOD, limit=self.pagination.limit,
                                        offset=self.pagination.offset)

            resp = make_api_response(json.dumps(response_data.serialize()), code)
            return resp

        # uuid or email is not None, let's get user
        try:
            api_response = self._user_service.get_user(suuid=suuid, email=email)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code, error=e.message,
                                        error_code=e.code)
            resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
            return resp

        if api_response.status == APIResponseStatus.failed.value:
            response_data = APIResponse(status=api_response.status, code=HTTPStatus.BAD_REQUEST.phrase,
                                        headers=api_response.headers, errors=api_response.errors)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.BAD_REQUEST)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data,
                                    headers=api_response.headers)
        resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
        return resp
