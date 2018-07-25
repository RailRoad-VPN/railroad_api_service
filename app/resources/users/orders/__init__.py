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
from rest import APIException, APIResourceURL

logger = logging.getLogger(__name__)


class OrderAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'OrderAPI'
    __api_url__ = 'orders'

    _config = None
    _order_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, OrderAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
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
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code == HTTPStatus.CREATED:
            order_uuid = api_response.headers['Location'].split('/')[-1]
            response_data = APIResponse(status=APIResponseStatus.success.status, code=api_response.code)
            resp = make_api_response(data=response_data, http_code=api_response.code)
            resp.headers['Location'] = '%s/%s/uuid/%s' % (self._config['API_BASE_URI'], self.__api_url__, order_uuid)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                        errors=api_response.errors, headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=api_response.code)
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
            api_response = self._order_api_service.get_order(suuid=suuid)
            if not api_response.is_ok:
                # order does not exist
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.ORDER_NOT_EXIST)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        code = request_json.get('code', None)
        status_id = request_json.get('status_id', None)
        payment_uuid = request_json.get('payment_uuid', None)
        modify_reason = request_json.get('modify_reason', None)

        req_fields = {
            'code': code,
            'status_id': status_id,
            'payment_uuid': payment_uuid,
            'modify_reason': modify_reason,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        order_json = {
            'uuid': suuid,
            'code': code,
            'status_id': status_id,
            'payment_uuid': payment_uuid,
            'modify_reason': modify_reason,
        }

        try:
            api_response = self._order_api_service.update_order(order_json=order_json)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code in [HTTPStatus.OK, HTTPStatus.NO_CONTENT]:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        headers=api_response.headers)
            if api_response.code == HTTPStatus.CREATED:
                response_data.data = api_response.data
            resp = make_api_response(data=response_data, http_code=api_response.code)
            return resp
        else:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=api_response.code)
            return resp

    def get(self, suuid: str = None, code: int = None) -> Response:
        super(OrderAPI, self).get(req=request)

        if (suuid is None and code is None) or (suuid is not None and code is not None):
            # find all orders - no parameters set
            return make_error_request_response(HTTPStatus.METHOD_NOT_ALLOWED, err=RailRoadAPIError.METHOD_NOT_ALLOWED)

        if suuid is not None:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if code is not None:
            try:
                code = int(code)
            except ValueError:
                return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        # uuid or code is not None, let's get order
        try:
            api_response = self._order_api_service.get_order(suuid=suuid, code=code)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if not api_response.is_ok:
            response_data = APIResponse(status=api_response.status, code=HTTPStatus.BAD_REQUEST,
                                        headers=api_response.headers, errors=api_response.errors)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.BAD_REQUEST)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data,
                                    headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
