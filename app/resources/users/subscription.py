import sys
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.exception import RailRoadAPIError
from app.service import UserSubscriptionAPIService

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid, make_api_response, make_error_request_response
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
            return make_error_request_response(HTTPStatus.NOT_FOUND, error=RailRoadAPIError.BAD_IDENTITY_ERROR)

        try:
            api_response = self._user_subscription_service.get_by_user_uuid(user_uuid=suuid)

            if api_response.status == APIResponseStatus.failed.status:
                # user subscription does not exist
                return make_error_request_response(HTTPStatus.NOT_FOUND, error=RailRoadAPIError.USER_SUBSCRIPTION_NOT_EXIST)

            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        data=api_response.data, headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                        errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp
