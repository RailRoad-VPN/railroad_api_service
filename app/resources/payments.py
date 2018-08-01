import base64
import datetime
import sys
import uuid
from http import HTTPStatus
from typing import List

from flask import request, Response

from app import PaymentAPIService, OrderAPIService
from app.exception import RailRoadAPIError
from app.model.order_status import OrderStatus

sys.path.insert(0, '../rest_api_library')
from response import make_api_response, make_error_request_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIResourceURL, APIException


class PaymentAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'PaymentAPI'
    __api_url__ = 'payments'

    _config = None
    _payment_api_service = None
    _order_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{PaymentAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['POST']),
        ]
        return api_urls

    def __init__(self, payment_api_service: PaymentAPIService, order_api_service: OrderAPIService, config: dict):
        super().__init__()
        self._config = config
        self._payment_api_service = payment_api_service
        self._order_api_service = order_api_service

    def post(self) -> Response:
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        apn = request_json.get('apn', None)

        if apn is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.PAYMENT_BAD_DATA_ERROR)

        t = '{0:%Y_%m_%d_%H%M%S}'.format(datetime.datetime.now())
        tt = f"{t}_{uuid.uuid4()}"

        with open(self._config['APN_PATH'] % tt, 'w') as file:
            file.write(apn)
            file.close()

        apn_str = base64.b64decode(apn).decode("utf-8")
        apn_dict = {}
        for row in apn_str.split('\r\n'):
            if row == '':
                continue
            kv = row.split('=')
            print(kv)
            k = kv[0]
            if len(kv) > 2:
                v = kv[1]
                for val in kv[2:]:
                    v += f"={val}"
            elif len(kv) == 1:
                continue
            else:
                v = kv[1]
            apn_dict[k] = v

        # ORDER_CUSTOM_FIELDS = x - ordercode = 52
        order_custom_fields = apn_dict['ORDER_CUSTOM_FIELDS']
        splitted = order_custom_fields.split("=")
        order_code = splitted[-1]

        api_response = self._payment_api_service.create_ppg_payment(apn_dict=apn_dict, order_id=order_code)
        ppg_payment = api_response.data
        payment_uuid = ppg_payment['uuid']

        try:
            api_response = self._order_api_service.get_order(code=order_code)
            order = api_response.data
        except APIException:
            return make_error_request_response(HTTPStatus.BAD_REQUEST,
                                               err=RailRoadAPIError.PAYMENT_DOES_NOT_UPDATE_ORDER)

        order['payment_uuid'] = payment_uuid
        order['modify_reason'] = 'add payment uuid'
        self._order_api_service.update_order(order_json=order)

        response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        resp.headers['Location'] = f"{self._config['API_BASE_URI']}/{self.__api_url__}/{payment_uuid}"
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp
