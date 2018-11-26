import base64
import datetime
import logging
import sys
import uuid
from http import HTTPStatus
from typing import List

from flask import request, Response

from app import UserPolicy
from app.exception import RailRoadAPIError
from app.model.order_status import OrderStatus
from app.model.payment_status import PaymentStatus, PPGPaymentStatus
from app.model.payment_type import PaymentType
from app.model.user_subscription_status import UserSubscriptionStatus
from app.model.vpn_conf_platform import VPNConfigurationPlatform
from app.model.vpn_type import VPNType
from app.service import OrderAPIService, UserRRNServiceAPIService, VPNMGMTUsersAPIService, \
    UsersVPNServersConfigurationsAPIService

sys.path.insert(0, '../rest_api_library')
from response import make_api_response, make_error_request_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIResourceURL, APINotFoundException


class PaymentsAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'payments'

    _order_api_service = None
    _user_rrnservice_api_service = None
    _vpn_mgmt_users_api_service = None
    _vpn_server_confs_service = None
    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{PaymentsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['POST']),
        ]
        return api_urls

    def __init__(self, order_api_service: OrderAPIService, user_sub_api_service: UserRRNServiceAPIService,
                 vpn_mgmt_users_api_service: VPNMGMTUsersAPIService, user_policy: UserPolicy,
                 vpn_server_confs_service: UsersVPNServersConfigurationsAPIService, *args):
        super().__init__(*args)
        self._order_api_service = order_api_service
        self._user_rrnservice_api_service = user_sub_api_service
        self._vpn_mgmt_users_api_service = vpn_mgmt_users_api_service
        self._vpn_server_confs_service = vpn_server_confs_service
        self._user_policy = user_policy

    def post(self) -> Response:
        super(PaymentsAPI, self).post(req=request)

        self.logger.debug(f"{self.__class__}: PaymentAPI -> POST method with parameters")

        self.logger.debug(f"{self.__class__}: check request has json")
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        self.logger.debug(f"{self.__class__}: get apn base64 string from request_json")
        apn = request_json.get('apn', None)

        if apn is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.PAYMENT_BAD_DATA_ERROR)

        self.logger.debug(f"{self.__class__}: create apn file name")
        t = '{0:%Y_%m_%d_%H%M%S}'.format(datetime.datetime.now())
        tt = f"{t}_{uuid.uuid4()}"

        self.logger.debug(f"{self.__class__}: Create APN file name: {tt}")
        with open(self._config['APN_PATH'] % tt, 'w') as file:
            file.write(apn)
            file.close()

        self.logger.debug(f"{self.__class__}: decode APN base64 string to utf-8")
        apn_str = base64.b64decode(apn).decode("utf-8")
        json_data_dict = {}
        self.logger.debug(f"{self.__class__}: convert APN to dict")
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
        self.logger.debug(
            "get from json_data_dict ORDER_CUSTOM_FIELDS=x-ordercode=52,x-useruuid=kfegie-adkasf-aszx-ce2c2e-zxcxzq")
        order_custom_fields = json_data_dict.get('ORDER_CUSTOM_FIELDS')
        self.logger.debug(f"{self.__class__}: got: {order_custom_fields}")

        self.logger.debug(f"{self.__class__}: processing order_custom_fields. try to find x-ordercode and x-useruuid fields")
        order_code = None
        user_uuid = None
        for order_custom_field in order_custom_fields.split(','):
            self.logger.debug(f"{self.__class__}: processing custom field: {order_custom_field}")
            key_value = order_custom_field.split("=")
            key = key_value[0]
            value = key_value[1]
            self.logger.debug(f"{self.__class__}: key: {key}")
            self.logger.debug(f"{self.__class__}: value: {value}")

            if key == 'x-ordercode':
                order_code = value
            elif key == 'x-useruuid':
                user_uuid = value

        self.logger.debug(f"{self.__class__}: order_code: {order_code}")
        self.logger.debug(f"{self.__class__}: user_uuid: {user_uuid}")

        if order_code is None:
            self.logger.debug(f"{self.__class__}: failed to process APN {tt} because x-ordercode not in APN content")
            resp = make_error_request_response(http_code=HTTPStatus.BAD_REQUEST,
                                               err=RailRoadAPIError.PAYMENT_APN_DOES_NOT_CONTAIN_ORDER_CODE_CUSTOM_FIELD)
            return resp
        elif user_uuid is None:
            self.logger.debug(f"{self.__class__}: failed to process APN {tt} because x-useruuid not in APN content")
            resp = make_error_request_response(http_code=HTTPStatus.BAD_REQUEST,
                                               err=RailRoadAPIError.PAYMENT_APN_DOES_NOT_CONTAIN_USER_UUID_CUSTOM_FIELD)
            return resp

        try:
            self.logger.debug(f"{self.__class__}: get order by code")
            api_response = self._order_api_service.get_order(code=order_code)
        except APINotFoundException as e:
            self.logger.error(e)
            http_code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=http_code, errors=e.errors)
            return make_api_response(data=response_data, http_code=http_code)

        order = api_response.data
        self.logger.debug(f"{self.__class__}: got order: {order}")
        order_uuid = order.get('uuid')

        self.logger.debug(f"{self.__class__}: get order status id from apn")
        apn_order_status_id = int(json_data_dict.get('ORDER_STATUS_ID'))
        self.logger.debug(f"{self.__class__}: got apn_order_status_id: {apn_order_status_id}")
        if apn_order_status_id == PPGPaymentStatus.PROCESSED.sid:
            self.logger.debug(f"{self.__class__}: it is {PPGPaymentStatus.PROCESSED.text} status: {PPGPaymentStatus.PROCESSED.sid}")
            payment_status_id = PaymentStatus.SUCCESS.sid
            order_status_id = OrderStatus.SUCCESS.sid
            user_sub_status_id = UserSubscriptionStatus.ACTIVE.sid
        elif apn_order_status_id == PPGPaymentStatus.WAITING.sid:
            self.logger.debug(f"{self.__class__}: it is {PPGPaymentStatus.WAITING.text} status: {PPGPaymentStatus.WAITING.sid}")
            payment_status_id = PaymentStatus.PROCESSING.sid
            order_status_id = OrderStatus.PROCESSING.sid
            user_sub_status_id = UserSubscriptionStatus.INACTIVE.sid
        else:
            # TODO понять что делать со статусами Refunded и Chargeback
            self.logger.warning(f"strange PPG status in APN: {apn_order_status_id}")
            payment_status_id = PaymentStatus.FAILED.sid
            order_status_id = OrderStatus.FAILED.sid
            user_sub_status_id = UserSubscriptionStatus.INACTIVE.sid

        self.logger.debug(f"{self.__class__}: create ppg payment")
        api_response = self._order_api_service.create_payment(order_uuid=order_uuid, type_id=PaymentType.PPG.sid,
                                                              status_id=payment_status_id, json_data=json_data_dict)
        payment = api_response.data

        payment_uuid = payment.get('uuid')
        self.logger.debug(f"{self.__class__}: created payment uuid: {payment_uuid}")

        self.logger.debug(f"{self.__class__}: prepare updated order")
        order['status_id'] = order_status_id
        order['modify_reason'] = 'update status'
        self.logger.debug(f"{self.__class__}: updated order: {order}")

        self.logger.debug(f"{self.__class__}: update order")
        self._order_api_service.update_order(order_json=order)

        self.logger.debug(f"{self.__class__}: get all user services")
        api_response = self._user_rrnservice_api_service.get_user_services_by_user_uuid(user_uuid=user_uuid)
        user_subs = api_response.data
        self.logger.debug(f"{self.__class__}: got user subs: {user_subs}")

        self.logger.debug(f"{self.__class__}: find user subscription for which payment come by order_uuid")
        payment_user_sub = None
        for user_sub in user_subs:
            self.logger.debug(f"{self.__class__}: process user sub: {user_sub}")
            if user_sub['order_uuid'] == order_uuid:
                self.logger.debug(f"{self.__class__}: we found!")
                payment_user_sub = user_sub
                break

        if payment_user_sub is None:
            self.logger.error(f"we DID NOT find user sub for which payment come")
            http_code = HTTPStatus.BAD_REQUEST
            return make_error_request_response(http_code=http_code,
                                               err=RailRoadAPIError.PAYMENT_APN_DID_NOT_FIND_USER_SUB)

        self.logger.debug(f"{self.__class__}: prepare updated user subscription")
        payment_user_sub['status_id'] = user_sub_status_id
        payment_user_sub['modify_reason'] = 'update status'
        self.logger.debug(f"{self.__class__}: updated user subscription: {payment_user_sub}")

        self.logger.debug(f"{self.__class__}: update user subscription")
        self._user_rrnservice_api_service.update(user_service=payment_user_sub)

        self.logger.debug(f"{self.__class__}: Launch MANAGEMENT API")
        self.logger.debug(f"{self.__class__}: create VPN user")

        self.logger.debug(f"{self.__class__}: get user by user_uuid: {user_uuid}")
        api_response = self._user_policy.get_user(suuid=user_uuid)
        user = api_response.data
        self.logger.debug(f"{self.__class__}: got user: {user}")

        self.logger.debug(f"{self.__class__}: call vpn mgmt users api service")
        api_response = self._vpn_mgmt_users_api_service.create_vpn_user(email=user.get('email'))
        self.logger.debug(f"{self.__class__}: got user configurations response: {api_response.serialize()}")
        user_configurations = api_response.data

        self.logger.debug(f"{self.__class__}: get openvpn user configs")
        openvpn = user_configurations.get(VPNType.OPENVPN.text, None)

        self.logger.debug(f"{self.__class__}: get ikev2 user configs")
        ikev2 = user_configurations.get(VPNType.IKEV2.text, None)

        openvpn_win_config = None
        openvpn_android_config = None
        ikev2_ios_config = None
        ikev2_win_config = None

        if openvpn is not None:
            self.logger.debug(f"{self.__class__}: we have openvpn configs. check platforms")
            openvpn_win_config = openvpn.get(VPNConfigurationPlatform.WINDOWS.text)
            openvpn_android_config = openvpn.get(VPNConfigurationPlatform.ANDROID.text)
        else:
            self.logger.debug(f"{self.__class__}: we have NO openvpn configs")

        if ikev2 is not None:
            self.logger.debug(f"{self.__class__}: we have ikev2 configs. check platforms")
            ikev2_win_config = ikev2.get(VPNConfigurationPlatform.WINDOWS.text)
            ikev2_ios_config = ikev2.get(VPNConfigurationPlatform.IOS.text)
        else:
            self.logger.debug(f"{self.__class__}: we have NO ikev2 configs")

        if openvpn_win_config is not None:
            self.logger.debug(f"{self.__class__}: we have openvpn for windows configuration. save it")
            self._vpn_server_confs_service.create(user_uuid=user_uuid,
                                                  configuration=openvpn_win_config,
                                                  vpn_device_platform_id=VPNConfigurationPlatform.WINDOWS.sid,
                                                  vpn_type_id=VPNType.OPENVPN.sid)
        if openvpn_android_config is not None:
            self.logger.debug(f"{self.__class__}: we have openvpn for android configuration. save it")
            self._vpn_server_confs_service.create(user_uuid=user_uuid,
                                                  configuration=openvpn_win_config,
                                                  vpn_device_platform_id=VPNConfigurationPlatform.ANDROID.sid,
                                                  vpn_type_id=VPNType.OPENVPN.sid)

        if ikev2_ios_config is not None:
            self.logger.debug(f"{self.__class__}: we have ikev2 for ios configuration. save it")
            self._vpn_server_confs_service.create(user_uuid=user_uuid,
                                                  configuration=ikev2_ios_config,
                                                  vpn_device_platform_id=VPNConfigurationPlatform.IOS.sid,
                                                  vpn_type_id=VPNType.IKEV2.sid)

        if ikev2_win_config is not None:
            self.logger.debug(f"{self.__class__}: we have ikev2 for windows configuration. save it")
            self._vpn_server_confs_service.create(user_uuid=user_uuid,
                                                  configuration=ikev2_win_config,
                                                  vpn_device_platform_id=VPNConfigurationPlatform.WINDOWS.sid,
                                                  vpn_type_id=VPNType.IKEV2.sid)

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
