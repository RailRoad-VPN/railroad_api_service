import datetime
import json
import logging
import sys

from app.model.payment_type import PaymentType

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException
from response import APIResponse
from api import ResourcePagination

logger = logging.getLogger(__name__)


class PaymentAPIService(RESTService):
    __version__ = 1

    def create_ppg_payment(self, order_id: int, apn_dict: dict):
        logger.debug(f"create_ppg_payment method with parameters order_id: {order_id}, apn_dict: {apn_dict}")
        data = {
            'order_id': order_id,
            'type_id': PaymentType.PPG.sid,
            'json_data': json.dumps(apn_dict)
        }

        logger.debug(f"Create PayProGlobal payment: {data}")
        api_response = self._post(data=data, headers=self._headers)
        #
        # if 'Location' in api_response.headers:
        #     api_response = self._get(url=api_response.headers.get('Location'))
        #     return api_response
        # else:
        #     logging.debug(api_response.serialize())
        #     raise APIException(http_code=api_response.code, errors=api_response.errors)

    # def get_payment(self, suuid: str) -> APIResponse:
    #     url = f"{self._url}/{suuid}"
    #     api_response = self._get(url=url)
    #     return api_response


class OrderAPIService(RESTService):
    __version__ = 1

    def create_order(self, status_id: int, payment_uuid: str = None) -> APIResponse:
        data = {
            'status_id': status_id,
            'payment_uuid': payment_uuid,
        }
        api_response = self._post(data=data, headers=self._headers)
        if 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            return api_response
        else:
            logging.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_order(self, order_json: dict):
        url = f"{self._url}/{order_json['uuid']}"
        self._put(url=url, data=order_json, headers=self._headers)

    def get_order(self, suuid: str = None, code: int = None) -> APIResponse:
        if suuid:
            url = f"{self._url}/uuid/{suuid}"
        elif code:
            url = f"{self._url}/code/{code}"
        else:
            raise KeyError
        api_response = self._get(url=url)

        return api_response


class UserDeviceAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, user_uuid: str, device_id: str, device_token: str = None, location: str = None,
               is_active: bool = False) -> APIResponse:
        us_json = {
            'user_uuid': user_uuid,
            'device_id': device_id,
            'device_token': device_token,
            'location': location,
            'is_active': is_active,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._post(data=us_json, url=url)
        return api_response

    def update(self, user_device: dict):
        url = self._url.replace('<string:user_uuid>', user_device['user_uuid'])
        url = f"{url}/{user_device['uuid']}"

        self._put(data=user_device, url=url)

    def get_user_device_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = f"{url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def get_user_devices(self, user_uuid: str) -> APIResponse:
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._get(url=url)
        return api_response


class UserSubscriptionAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, user_uuid: str, subscription_id: str, order_uuid: str) -> APIResponse:
        us_json = {
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'order_uuid': order_uuid,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._post(data=us_json, url=url)
        return api_response

    def update(self, user_subscription: dict):
        url = self._url.replace('<string:user_uuid>', user_subscription['user_uuid'])
        url = f"{url}/{user_subscription['uuid']}"
        self._put(data=user_subscription, url=url)

    def get_user_sub_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = f"{url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def get_user_subs_by_user_uuid(self, user_uuid: str) -> APIResponse:
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._get(url=url)
        return api_response


class SubscriptionAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_subscriptions(self, lang_code: str) -> APIResponse:
        headers = {
            'Accept-Language': lang_code
        }
        api_response = self._get(headers=headers)

        return api_response


class UserAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_user(self, email: str, password: str, is_expired: bool = False, is_locked: bool = False,
                    is_password_expired: bool = False, enabled: bool = False, pin_code: str = None,
                    pin_code_expire_date: datetime = None) -> APIResponse:
        user_json = {
            'email': email,
            'password': password,
            'is_expired': is_expired,
            'is_locked': is_locked,
            'is_password_expired': is_password_expired,
            'enabled': enabled,
            'pin_code': pin_code,
            'pin_code_expire_date': pin_code_expire_date,
        }

        api_response = self._post(data=user_json, headers=self._headers)
        return api_response

    def update_user(self, user_dict: dict):
        logger.debug(f"Updating user with dict: {user_dict}")

        url = f"{self._url}/{user_dict['uuid']}"
        self._put(url=url, data=user_dict, headers=self._headers)

    def get_user(self, suuid: str = None, email: str = None, pin_code: int = None) -> APIResponse:
        if suuid:
            url = f"{self._url}/uuid/{suuid}"
        elif email:
            url = f"{self._url}/email/{email}"
        elif pin_code:
            url = f"{self._url}/pincode/{pin_code}"
        else:
            raise KeyError
        api_response = self._get(url=url)
        return api_response


class VPNServersAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnservers(self, pagination: ResourcePagination = None) -> APIResponse:
        if pagination is not None and pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset)
            api_response = self._get(url=url)
        else:
            api_response = self._get()
        return api_response

    def get_vpnservers_by_type(self, type_id: int, pagination: ResourcePagination) -> APIResponse:
        url = f"{self._url}/type/{type_id}"

        if pagination is not None and pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset, url=url)

        api_response = self._get(url=url)
        return api_response

    def get_vpnservers_by_status(self, status_id: int, pagination: ResourcePagination) -> APIResponse:
        url = f"{self._url}/status/{status_id}"
        if pagination is not None and pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset, url=url)

        api_response = self._get(url=url)
        return api_response

    def get_vpnserver_by_uuid(self, suuid: str) -> APIResponse:
        url = f"{self._url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def update_vpnserver(self, vpnserver: dict):
        url = f"{self._url}/{vpnserver['uuid']}"
        self._put(url=url, data=vpnserver)

    def create_vpnserver(self, vpnserver: dict) -> APIResponse:
        api_response = self._post(data=vpnserver)
        return api_response


class VPNServersMetaAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_meta(self) -> APIResponse:
        api_response = self._get()
        return api_response


class VPNTypeAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpntypes(self) -> APIResponse:
        api_response = self._get()
        return api_response

    def get_vpntype_by_id(self, sid) -> APIResponse:
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class VPNServerConfigurationAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnserverconfig(self, server_uuid: str, user_uuid: str = None) -> APIResponse:
        url = f"{self._url}/{server_uuid}/configurations/user/{user_uuid}"
        api_response = self._get(url=url)
        return api_response

    def get_vpnserverconfig_by_uuid(self, suuid) -> APIResponse:
        url = f"{self._url}/{suuid}"
        api_response = self._get(url=url)
        return api_response


class VPNServerStatusAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnserverstatuses(self) -> APIResponse:
        api_response = self._get()
        return api_response

    def get_vpnserverstatuse_by_id(self, sid) -> APIResponse:
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class GeoPositionAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geoposes(self) -> APIResponse:
        api_response = self._get()
        return api_response

    def get_geopos_by_id(self, sid) -> APIResponse:
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class GeoCityAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geocities(self) -> APIResponse:
        api_response = self._get()
        return api_response

    def get_geocity_by_id(self, sid) -> APIResponse:
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class GeoCountryAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geocountries(self) -> APIResponse:
        api_response = self._get()
        return api_response

    def get_geocountry_by_code(self, code) -> APIResponse:
        url = f"{self._url}/{code}"
        api_response = self._get(url=url)
        return api_response


class GeoStateAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geostates(self) -> APIResponse:
        api_response = self._get()
        return api_response

    def get_geostate_by_code(self, code) -> APIResponse:
        url = f"{self._url}/{code}"
        api_response = self._get(url=url)
        return api_response
