import datetime
import sys
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.exception import RailRoadAPIError

sys.path.insert(0, '../rest_api_library')
from utils import make_api_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIResourceURL


class PaymentAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'PaymentAPI'
    __api_url__ = 'payments'

    _config = None
    _subscription_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, PaymentAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
        ]
        return api_urls

    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config

    def post(self) -> Response:
        request_json = request.json

        if request_json is None:
            error = RailRoadAPIError.REQUEST_NO_JSON.message
            error_code = RailRoadAPIError.REQUEST_NO_JSON.code
            developer_message = RailRoadAPIError.REQUEST_NO_JSON.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            return make_api_response(data=response_data, http_code=http_code)

        apn = request_json.get('apn', None)

        if apn is None:
            error = RailRoadAPIError.PAYMENT_BAD_DATA_ERROR.message
            error_code = RailRoadAPIError.PAYMENT_BAD_DATA_ERROR.code
            developer_message = RailRoadAPIError.PAYMENT_BAD_DATA_ERROR.developer_message
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.value, code=http_code, error=error,
                                        developer_message=developer_message, error_code=error_code)
            return make_api_response(data=response_data, http_code=http_code)

        t = '{0:%Y_%m_%d_%H%M%S}'.format(datetime.datetime.now())

        with open('/opt/apps/dfn/apn/%s.apn' % t, 'w') as file:
            file.write(apn)

        response_data = APIResponse(status=APIResponseStatus.success.value, code=HTTPStatus.OK)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp
