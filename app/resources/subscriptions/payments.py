import datetime
import sys
import uuid
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.exception import RailRoadAPIError

sys.path.insert(0, '../rest_api_library')
from utils import make_api_response, make_error_request_response
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
            APIResourceURL(base_url=url, resource_name='', methods=['POST']),
        ]
        return api_urls

    def __init__(self, config: dict) -> None:
        super().__init__()
        self._config = config

    def post(self) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        apn = request_json.get('apn', None)

        if apn is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.PAYMENT_BAD_DATA_ERROR)

        t = '{0:%Y_%m_%d_%H%M%S}'.format(datetime.datetime.now())
        tt = "%s_%s" % (t, uuid.uuid4())

        with open('/opt/apps/dfn/apn/%s.apn' % tt, 'w') as file:
            file.write(apn)

        response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp
