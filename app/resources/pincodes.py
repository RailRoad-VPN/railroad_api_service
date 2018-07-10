import logging
import random
import sys
import uuid
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.policy import UserPolicy
from rest import APIResourceURL, APIException

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import make_api_response, make_error_request_response, check_required_api_fields, check_uuid

logger = logging.getLogger(__name__)


class PinCodeAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'PinCodesAPI'
    __api_url__ = 'pincodes'

    _user_policy = None
    _config = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, PinCodeAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST', 'PUT']),
        ]
        return api_urls

    def __init__(self, user_policy: UserPolicy, config: dict) -> None:
        super().__init__()
        self._user_policy = user_policy

        self._config = config

    def post(self) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        pin_code = request_json.get('pin_code', None)
        device_id = request_json.get('device_id', None)
        location = request_json.get('location', None)

        req_fields = {
            'pin_code': pin_code,
            'device_id': device_id,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._user_policy.get_user_uuid_by_pincode(pin_code=pin_code)
            if api_response.is_ok:
                user_uuid = api_response.data
            else:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.PINCODE_NOT_EXIST)

            api_response = self._user_policy.exchange_pincode_for_user_device(user_uuid=user_uuid, pin_code=pin_code,
                                                                              device_id=device_id, location=location,
                                                                              is_active=True,
                                                                              device_token=uuid.uuid4().hex,
                                                                              modify_reason='client_exchange')
        except APIException as e:
            logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.is_ok:
            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.CREATED)
            return make_api_response(data=response_data, http_code=api_response.code)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                        errors=api_response.errors, headers=api_response.headers)
            return make_api_response(data=response_data, http_code=api_response.code)

    def put(self) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        try:
            pin_code = int(request_json.get('pin_code', None))
        except KeyError:
            pin_code = None

        user_uuid = request_json.get('user_uuid', None)
        device_token = request_json.get('device_token', None)
        device_id = request_json.get('device_id', None)
        location = request_json.get('location', None)
        is_active = request_json.get('is_active', None)
        modify_reason = request_json.get('modify_reason', None)

        req_fields = {
            'pin_code': pin_code,
            'device_id': device_id,
            'is_active': is_active,
        }

        if user_uuid is not None:
            req_fields['device_token'] = device_token
            req_fields['modify_reason'] = modify_reason
            req_fields['user_uuid'] = user_uuid
        else:
            modify_reason = 'exchange pincode'
            try:
                api_response = self._user_policy.get_user_uuid_by_pincode(pin_code=pin_code)
                if api_response.is_ok:
                    user_uuid = api_response.data
                else:
                    return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.PINCODE_NOT_EXIST)
            except APIException as e:
                logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                            errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._user_policy.update_user_device(user_uuid=user_uuid, pin_code=pin_code,
                                                                device_id=device_id, location=location, is_active=True,
                                                                device_token=uuid.uuid4().hex,
                                                                modify_reason=modify_reason)
            if api_response.is_ok:
                response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.CREATED)
                return make_api_response(data=response_data, http_code=api_response.code)
            else:
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                            errors=api_response.errors, headers=api_response.headers)
                return make_api_response(data=response_data, http_code=api_response.code)
        except APIException as e:
            logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def get(self) -> Response:
        super(PinCodeAPI, self).get(req=request)

        user_uuid = request.args.get('user_uuid', None)

        error_fields = check_required_api_fields({'user_uuid': user_uuid})
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        is_valid = check_uuid(suuid=user_uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        try:
            self._user_policy.get_user(suuid=user_uuid)
        except APIException as e:
            logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        # We create a set of digits: {0, 1, .... 9}
        digits = set(range(10))
        # We generate a random integer, 1 <= first <= 9
        first = random.randint(1, 9)
        # We remove it from our set, then take a sample of
        # 3 distinct elements from the remaining values
        last_3 = random.sample(digits - {first}, 3)
        pin_code = int(str(first) + ''.join(map(str, last_3)))

        try:
            api_response = self._user_policy.create_user_device(user_uuid=user_uuid, pin_code=pin_code)
            if not api_response.is_ok:
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                            errors=error_fields)
                resp = make_api_response(data=response_data, http_code=api_response.code)
                return resp
        except APIException as e:
            logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK, data=pin_code)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
