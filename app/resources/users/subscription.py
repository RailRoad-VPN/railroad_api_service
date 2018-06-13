import sys
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.exception import RailRoadAPIError
from app.service import UserSubscriptionAPIService

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid, make_api_response, make_error_request_response, check_required_api_fields
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIException, APIResourceURL


class UserSubscriptionAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'UserSubscriptionAPI'
    __api_url__ = 'users/<string:user_uuid>/subscriptions'

    _config = None
    _user_service = None
    _user_subscription_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, UserSubscriptionAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST', ]),
            APIResourceURL(base_url=url, resource_name='<string:user_subscription_uuid>', methods=['GET', 'PUT', ]),
        ]
        return api_urls

    def __init__(self, user_subscription_service: UserSubscriptionAPIService,
                 config: dict) -> None:
        super().__init__()
        self._config = config
        self._user_subscription_service = user_subscription_service

    def post(self, user_uuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        is_valid = check_uuid(suuid=user_uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        user_uuid = request_json.get('user_uuid', None)
        subscription_id = request_json.get('subscription_id', None)
        expire_date = request_json.get('expire_date', None)
        order_uuid = request_json.get('order_uuid', None)

        error_fields = check_required_api_fields(user_uuid, subscription_id, expire_date, order_uuid)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        us_json = {
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'expire_date': expire_date,
            'order_uuid': order_uuid,
        }

        try:
            api_response = self._user_subscription_service.create(us_json=us_json)
            if api_response.is_ok:
                user_subscription_uuid = api_response.data['uuid']
                resp = make_api_response(http_code=HTTPStatus.CREATED)

                api_url = self.__api_url__ % user_uuid
                resp.headers['Location'] = '%s/%s/uuid/%s' % (
                    self._config['API_BASE_URI'], api_url, user_subscription_uuid)
                return resp
            else:
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                            errors=api_response.errors, headers=api_response.headers)
                return make_api_response(data=response_data, http_code=api_response.code)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def put(self, user_uuid: str, user_subscription_uuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        us_uuid = request_json.get('uuid', None)

        is_valid_a = check_uuid(suuid=user_subscription_uuid)
        is_valid_b = check_uuid(suuid=us_uuid)
        if not is_valid_a or not is_valid_b or (user_subscription_uuid != us_uuid):
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        user_uuid = request_json.get('user_uuid', None)
        subscription_id = request_json.get('subscription_id', None)
        expire_date = request_json.get('expire_date', None)
        order_uuid = request_json.get('order_uuid', None)
        modify_date = request_json.get('modify_date', None)
        modify_reason = request_json.get('modify_reason', None)

        error_fields = check_required_api_fields(us_uuid, user_uuid, subscription_id, expire_date, order_uuid,
                                                 modify_date, modify_reason)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        us_json = {
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'expire_date': expire_date,
            'order_uuid': order_uuid,
        }

        try:
            api_response = self._user_subscription_service.get_user_subscription_by_uuid(suuid=user_subscription_uuid)
            if not api_response.is_ok:
                # user subscription does not exist
                return make_error_request_response(HTTPStatus.NOT_FOUND,
                                                   err=RailRoadAPIError.USER_SUBSCRIPTION_NOT_EXIST)
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        try:
            api_response = self._user_subscription_service.update(us_json=us_json)
            if api_response.is_ok:
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.NO_CONTENT,
                                            headers=api_response.headers)
            else:
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                            headers=api_response.headers, errors=api_response.errors)
            resp = make_api_response(data=response_data, http_code=api_response.code)
            return resp
        except APIException as e:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def get(self, user_uuid: str, user_subscription_uuid: str = None) -> Response:
        super(UserSubscriptionAPI, self).get(req=request)

        is_valid = check_uuid(suuid=user_uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if user_subscription_uuid is not None:
            is_valid = check_uuid(suuid=user_subscription_uuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)
            # get user subscription by subscription uuid
            api_response = self._user_subscription_service.get_user_subscription_by_uuid(suuid=user_subscription_uuid)
            if api_response.is_ok:
                pass
            else:
                pass
        else:
            # get all user subscriptions
            try:
                api_response = self._user_subscription_service.get_user_subscriptions_by_user_uuid(user_uuid=user_uuid)
                if api_response.is_ok:
                    response_data = APIResponse(status=api_response.status, code=api_response.code,
                                                data=api_response.data, headers=api_response.headers)
                    resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                else:
                    response_data = APIResponse(status=api_response.status, code=api_response.code,
                                                data=api_response.data, headers=api_response.headers,
                                                errors=api_response.errors)
                    resp = make_api_response(data=response_data, http_code=api_response.code)
                return resp
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
