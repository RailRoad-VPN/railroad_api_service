import base64
import datetime
import logging
import sys
import uuid
from http import HTTPStatus
from typing import List

from flask import request, Response

from app.service import OrderAPIService, UserSubscriptionAPIService
from app.exception import RailRoadAPIError
from app.model.order_status import OrderStatus
from app.model.payment_status import PaymentStatus, PPGPaymentStatus
from app.model.payment_type import PaymentType
from app.model.user_subscription_status import UserSubscriptionStatus

sys.path.insert(0, '../rest_api_library')
from response import make_api_response, make_error_request_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIResourceURL, APINotFoundException

logger = logging.getLogger(__name__)


class PaymentAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'PaymentAPI'
    __api_url__ = 'payments'

    _config = None
    _order_api_service = None
    _user_sub_api_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{PaymentAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['POST']),
        ]
        return api_urls

    def __init__(self, order_api_service: OrderAPIService, user_sub_api_service: UserSubscriptionAPIService,
                 config: dict):
        super().__init__()
        self._config = config
        self._order_api_service = order_api_service
        self._user_sub_api_service = user_sub_api_service

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
        json_data_dict = {}
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
            json_data_dict[k] = v

        # ORDER_CUSTOM_FIELDS=x-ordercode=52,x-useruuid=kfegie-adkasf-aszx-ce2c2e-zxcxzq
        logger.debug("get from json_data_dict ORDER_CUSTOM_FIELDS=x-ordercode=52,x-useruuid=kfegie-adkasf-aszx-ce2c2e-zxcxzq")
        order_custom_fields = json_data_dict.get('ORDER_CUSTOM_FIELDS')
        logger.debug(f"got: {order_custom_fields}")

        logger.debug(f"processing order_custom_fields. try to find x-ordercode and x-useruuid fields")
        order_code = None
        user_uuid = None
        for order_custom_field in order_custom_fields.split(','):
            logger.debug(f"processing custom field: {order_custom_field}")
            key_value = order_custom_field.split("=")
            key = key_value[0]
            value = key_value[1]
            logger.debug(f"key: {key}")
            logger.debug(f"value: {value}")

            if key == 'x-ordercode':
                order_code = value
            elif key == 'x-useruuid':
                user_uuid = value

        logger.debug(f"order_code: {order_code}")
        logger.debug(f"user_uuid: {user_uuid}")

        if order_code is None:
            logger.debug(f"failed to process APN {tt} because x-ordercode not in APN content")
            resp = make_error_request_response(http_code=HTTPStatus.BAD_REQUEST,
                                               err=RailRoadAPIError.PAYMENT_APN_DOES_NOT_CONTAIN_ORDER_CODE_CUSTOM_FIELD)
            return resp
        elif user_uuid is None:
            logger.debug(f"failed to process APN {tt} because x-useruuid not in APN content")
            resp = make_error_request_response(http_code=HTTPStatus.BAD_REQUEST,
                                               err=RailRoadAPIError.PAYMENT_APN_DOES_NOT_CONTAIN_USER_UUID_CUSTOM_FIELD)
            return resp

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

        logger.debug(f"get order status id from apn")
        apn_order_status_id = int(json_data_dict.get('ORDER_STATUS_ID'))
        logger.debug(f"got apn_order_status_id: {apn_order_status_id}")
        if apn_order_status_id == PPGPaymentStatus.PROCESSED.sid:
            logger.debug(f"it is {PPGPaymentStatus.PROCESSED.text} status: {PPGPaymentStatus.PROCESSED.sid}")
            payment_status_id = PaymentStatus.SUCCESS.sid
            order_status_id = OrderStatus.SUCCESS.sid
            user_sub_status_id = UserSubscriptionStatus.ACTIVE.sid
        elif apn_order_status_id == PPGPaymentStatus.WAITING.sid:
            logger.debug(f"it is {PPGPaymentStatus.WAITING.text} status: {PPGPaymentStatus.WAITING.sid}")
            payment_status_id = PaymentStatus.PROCESSING.sid
            order_status_id = OrderStatus.PROCESSING.sid
            user_sub_status_id = UserSubscriptionStatus.INACTIVE.sid
        else:
            # TODO понять что делать со статусами Refunded и Chargeback
            logger.warning(f"strange PPG status in APN: {apn_order_status_id}")
            payment_status_id = PaymentStatus.FAILED.sid
            order_status_id = OrderStatus.FAILED.sid
            user_sub_status_id = UserSubscriptionStatus.INACTIVE.sid

        logger.debug(f"create ppg payment")
        api_response = self._order_api_service.create_payment(order_uuid=order_uuid, type_id=PaymentType.PPG.sid,
                                                              status_id=payment_status_id, json_data=json_data_dict)
        payment = api_response.data

        payment_uuid = payment.get('uuid')
        logger.debug(f"created payment uuid: {payment_uuid}")

        logger.debug(f"prepare updated order")
        order['status_id'] = order_status_id
        order['modify_reason'] = 'update status'
        logger.debug(f"updated order: {order}")

        logger.debug(f"update order")
        self._order_api_service.update_order(order_json=order)

        logger.debug(f"get all user subscriptions")
        api_response = self._user_sub_api_service.get_user_subs_by_user_uuid(user_uuid=user_uuid)
        user_subs = api_response.data
        logger.debug(f"got user subs: {user_subs}")

        logger.debug(f"find user subscription for which payment come by order_uuid")
        payment_user_sub = None
        for user_sub in user_subs:
            logger.debug(f"process user sub: {user_sub}")
            if user_sub['order_uuid'] == order_uuid:
                logger.debug(f"we found!")
                payment_user_sub = user_sub
                break

        if payment_user_sub is None:
            logger.error(f"we DID NOT find user sub for which payment come")
            http_code = HTTPStatus.BAD_REQUEST
            return make_error_request_response(http_code=http_code,
                                               err=RailRoadAPIError.PAYMENT_APN_DID_NOT_FIND_USER_SUB)

        logger.debug(f"prepare updated user subscription")
        payment_user_sub['status_id'] = user_sub_status_id
        payment_user_sub['modify_reason'] = 'update status'
        logger.debug(f"updated user subscription: {payment_user_sub}")

        logger.debug(f"update user subscription")
        self._user_sub_api_service.update(user_subscription=payment_user_sub)

        response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        resp.headers['Location'] = f"{self._config['API_BASE_URI']}/{self.__api_url__}/{payment_uuid}"
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp
