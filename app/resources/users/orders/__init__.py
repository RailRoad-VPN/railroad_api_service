import logging
import sys
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.exception import RailRoadAPIError
from app.service import OrderAPIService

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid
from response import make_api_response, make_error_request_response, check_required_api_fields
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIException, APIResourceURL, APINotFoundException

logger = logging.getLogger(__name__)


class UsersOrdersAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = __qualname__
    __api_url__ = 'orders'

    _config = None
    _order_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, UsersOrdersAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['PUT']),
            APIResourceURL(base_url=url, resource_name='uuid/<string:suuid>', methods=['GET', 'POST']),
            APIResourceURL(base_url=url, resource_name='code/<int:code>', methods=['GET', 'POST']),
        ]
        return api_urls

    def __init__(self, order_service: OrderAPIService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._order_api_service = order_service

    def post(self) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        status_id = request_json.get('status_id', None)
        payment_uuid = request_json.get('payment_uuid', None)

        error_fields = check_required_api_fields({'status_id': status_id})
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._order_api_service.create_order(status_id=status_id, payment_uuid=payment_uuid)
        except APIException as e:
            logger.error(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        order_uuid = api_response.data['uuid']
        response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code)
        resp = make_api_response(data=response_data, http_code=api_response.code)
        resp.headers['Location'] = f"{self._config['API_BASE_URI']}/{self.__api_url__}/uuid/{order_uuid}"
        return resp

    def put(self, suuid: str) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        order_uuid = request_json.get('uuid', None)

        is_valid_a = check_uuid(suuid=suuid)
        is_valid_b = check_uuid(suuid=order_uuid)
        if not is_valid_a or not is_valid_b or (suuid != order_uuid):
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.BAD_ORDER_IDENTITY)

        try:
            self._order_api_service.get_order(suuid=suuid)
        except APINotFoundException as e:
            # order does not exist
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.ORDER_NOT_EXIST)
        except APIException as e:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.BAD_ORDER_IDENTITY)

        code = request_json.get('code', None)
        status_id = request_json.get('status_id', None)
        payment_uuid = request_json.get('payment_uuid', None)
        modify_reason = request_json.get('modify_reason', None)

        req_fields = {
            'code': code,
            'status_id': status_id,
            'modify_reason': modify_reason,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        req_fields['uuid'] = suuid
        req_fields['payment_uuid'] = payment_uuid

        try:
            self._order_api_service.update_order(order_json=req_fields)
        except APIException as e:
            logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp

    def get(self, suuid: str = None, code: int = None) -> Response:
        super(UsersOrdersAPI, self).get(req=request)

        if (suuid is None and code is None) or (suuid is not None and code is not None):
            # find all orders - no parameters set
            return make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED,
                                               err=RailRoadAPIError.METHOD_NOT_ALLOWED)

        if suuid is not None:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                return make_error_request_response(http_code=HTTPStatus.NOT_FOUND,
                                                   err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if code is not None:
            try:
                code = int(code)
            except ValueError:
                return make_error_request_response(http_code=HTTPStatus.BAD_REQUEST,
                                                   err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        # uuid or code is not None, let's get order
        try:
            api_response = self._order_api_service.get_order(suuid=suuid, code=code)
        except APIException as e:
            logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp
        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
