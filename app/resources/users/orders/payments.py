import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.service import PaymentAPIService

sys.path.insert(0, '../rest_api_library')
from response import make_api_response
from api import ResourceAPI
from rest import APIResourceURL


class OrderPaymentsAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'PaymentAPI'
    __api_url__ = 'orders/<string:uuid>/payments'

    _config = None
    _payment_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, OrderPaymentsAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET', 'POST']),
        ]
        return api_urls

    def __init__(self, payment_service: PaymentAPIService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._payment_service = payment_service

    def post(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, order_uuid: str, suuid: str = None) -> Response:
        super(OrderPaymentsAPI, self).get(req=request)

        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp
