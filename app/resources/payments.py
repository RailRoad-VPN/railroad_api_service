import base64
import datetime
import logging
import sys
import uuid
from http import HTTPStatus
from typing import List

from flask import request, Response

from app import OrderAPIService
from app.exception import RailRoadAPIError
from app.model.order_status import OrderStatus

sys.path.insert(0, '../rest_api_library')
from response import make_api_response, make_error_request_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIResourceURL, APIException, APINotFoundException

logger = logging.getLogger(__name__)


class PaymentAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'PaymentAPI'
    __api_url__ = 'payments'

    _config = None
    _order_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{PaymentAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['POST']),
        ]
        return api_urls

    def __init__(self, order_api_service: OrderAPIService, config: dict):
        super().__init__()
        self._config = config
        self._order_api_service = order_api_service

    def post(self) -> Response:
        logger.debug(f"PaymentAPI -> POST method with parameters")

        logger.debug("check request has json")
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        logger.debug("get apn base64 string from request_json")
        apn = request_json.get('apn', None)

        if apn is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.PAYMENT_BAD_DATA_ERROR)

        logger.debug("create apn file name")
        t = '{0:%Y_%m_%d_%H%M%S}'.format(datetime.datetime.now())
        tt = f"{t}_{uuid.uuid4()}"

        logger.debug(f"Create APN file name: {tt}")
        with open(self._config['APN_PATH'] % tt, 'w') as file:
            file.write(apn)
            file.close()

        logger.debug(f"decode APN base64 string to utf-8")
        apn_str = base64.b64decode(apn).decode("utf-8")
        apn_dict = {}
        logger.debug(f"convert APN to dict")
        for row in apn_str.split('\r\n'):
            if row == '':
                continue
            kv = row.split('=')
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
        logger.debug("get from apn_dict ORDER_CUSTOM_FIELDS, we expect value like x - ordercode = 52")
        order_custom_fields = apn_dict['ORDER_CUSTOM_FIELDS']
        logger.debug(f"got: {order_custom_fields}")

        logger.debug(f"retrieve order code")
        splitted = order_custom_fields.split("=")
        order_code = splitted[-1]
        logger.debug(f"order code: {order_code}")

        try:
            logger.debug(f"get order by code")
            api_response = self._order_api_service.get_order(code=order_code)
        except APINotFoundException as e:
            logger.error(e)
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, errors=e.errors)
            return make_api_response(data=response_data, http_code=http_code)

        order = api_response.data
        logger.debug(f"got order: {order}")
        order_uuid = order.get('uuid')

        logger.debug(f"try to create ppg payment")
        api_response = self._order_api_service.create_ppg_payment(order_uuid=order_uuid, apn_dict=apn_dict,
                                                                  order_id=order_code)
        ppg_payment = api_response.data

        payment_uuid = ppg_payment.get('payment_uuid')
        logger.debug(f"created payment uuid: {payment_uuid}")

        logger.debug(f"prepare updated order")
        order['status_id'] = OrderStatus.SUCCESS.sid
        order['modify_reason'] = 'add payment uuid'
        logger.debug(f"updated order: {order}")

        logger.debug(f"try to update order")
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
