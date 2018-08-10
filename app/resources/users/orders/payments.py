import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.service import OrderAPIService
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from response import make_api_response, make_error_request_response, APIResponse, APIResponseStatus
from api import ResourceAPI
from rest import APIResourceURL, APIException, APINotFoundException

logger = logging.getLogger(__name__)


class OrderPaymentsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'OrderPaymentsAPI'
    __api_url__ = 'orders/<string:order_uuid>/payments'

    _config = None
    _order_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, OrderPaymentsAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET', 'PUT']),
        ]
        return api_urls

    def __init__(self, order_service: OrderAPIService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._order_service = order_service

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, order_uuid: str, suuid: str = None) -> Response:
        super(OrderPaymentsAPI, self).get(req=request)

        if suuid is not None:
            logger.debug(f"check order_payment uuid")
            is_valid = check_uuid(suuid)
            if not is_valid:
                return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.ORDERPAYMENT_IDENTIFIER)
            try:
                api_response = self._order_service.get_payment(order_uuid=order_uuid, suuid=suuid)
            except APINotFoundException as e:
                # order payment does not exist
                return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.ORDERPAYMENT_NOT_EXIST)
            except APIException as e:
                logging.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
        else:
            try:
                api_response = self._order_service.get_order_payments(order_uuid=order_uuid)
            except APIException as e:
                logging.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
