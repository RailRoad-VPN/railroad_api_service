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


class UserSubscriptionAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'UserSubscriptionAPI'
    __api_url__ = 'users/<string:user_uuid>/subscriptions'

    _config = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, UserSubscriptionAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST', ]),
            APIResourceURL(base_url=url, resource_name='<string:user_subscription_uuid>', methods=['GET', 'PUT', ]),
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
        subscription_id = request_json.get('subscription_id', None)
        order_uuid = request_json.get('order_uuid', None)

        req_fields = {
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'order_uuid': order_uuid,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._user_policy.create_user_sub(user_uuid=user_uuid, subscription_id=subscription_id,
                                                             order_uuid=order_uuid)

            api_url = self.__api_url__.replace('<string:user_uuid>', user_uuid)

            response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code)
            resp = make_api_response(data=response_data, http_code=api_response.code)
            resp.headers['Location'] = f"{self._config['API_BASE_URI']}/{api_url}/{api_response.data['uuid']}"
            return resp
        except APIException as e:
            logging.debug(e.serialize())
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

        us_json = {
            'uuid': us_uuid,
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'expire_date': expire_date,
            'order_uuid': order_uuid,
            'modify_date': modify_date,
            'modify_reason': modify_reason,
        }

        error_fields = check_required_api_fields(us_json)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            self._user_policy.get_user_sub_by_uuid(user_uuid=user_uuid, suuid=user_subscription_uuid)
        except APIException:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.USER_SUBSCRIPTION_NOT_EXIST)

        try:
            self._user_policy.update_user_sub(user_subscription=us_json)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        except APIException as e:
            logging.debug(e.serialize())
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
            try:
                api_response = self._user_policy.get_user_sub_by_uuid(user_uuid=user_uuid, suuid=user_subscription_uuid)
            except APIException as e:
                return make_error_request_response(http_code=e.http_code, err=e.errors)
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                        data=api_response.data)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
            return resp
        else:
            # get all user subscriptions
            try:
                api_response = self._user_policy.get_user_subs(user_uuid=user_uuid)
                subs = api_response.data
                response_data = APIResponse(status=api_response.status, code=api_response.code, data=subs)
                resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
                return resp
            except APIException as e:
                logging.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
