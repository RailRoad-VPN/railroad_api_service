import json
import sys
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.service import UserSubscriptionAPIService
from app.exception import RailRoadAPIError

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid, make_api_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIException, APIResourceURL


class UserSubscriptionAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'UserSubscriptionAPI'
    __api_url__ = 'users'

    _config = None
    _user_service = None
    _user_subscription_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, UserSubscriptionAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='<string:suuid>/subscription', methods=['GET']),
        ]
        return api_urls

    def __init__(self, user_subscription_service: UserSubscriptionAPIService,
                 config: dict) -> None:
        super().__init__()
        self._config = config
        self._user_subscription_service = user_subscription_service

    def post(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, suuid: str) -> Response:
        super(UserSubscriptionAPI, self).get(req=request)

        is_valid = check_uuid(suuid=suuid)
        if not is_valid:
            code = HTTPStatus.NOT_FOUND
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                        error=RailRoadAPIError.BAD_USER_IDENTITY.message,
                                        error_code=RailRoadAPIError.BAD_USER_IDENTITY.code)

            resp = make_api_response(data=response_data, http_code=code)
            return resp

        try:
            api_response = self._user_subscription_service.get_by_user_uuid(user_uuid=suuid)

            if api_response.status == APIResponseStatus.failed.value:
                # user subscription does not exist
                code = HTTPStatus.BAD_REQUEST
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                            error=RailRoadAPIError.USER_SUBSCRIPTION_NOT_EXIST.message,
                                            error_code=RailRoadAPIError.USER_SUBSCRIPTION_NOT_EXIST.code)
                resp = make_api_response(data=response_data, http_code=code)
                return resp

            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        data=api_response.data, headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code,
                                        errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp


