import datetime
import sys

sys.path.insert(0, '../rest_api_library')
from rest import RESTService
from response import APIResponse
from api import ResourcePagination


class PaymentAPIService(RESTService):
    __version__ = 1

    def create_payment(self, payment_json: dict) -> APIResponse:
        api_response = self._post(data=payment_json, headers=self._headers)
        return api_response

    def get_payment(self, suuid: str) -> APIResponse:
        url = '%s/%s' % (self._url, suuid)
        api_response = self._get(url=url)

        return api_response


class OrderAPIService(RESTService):
    __version__ = 1

    def create_order(self, order_json: dict) -> APIResponse:
        api_response = self._post(data=order_json, headers=self._headers)
        return api_response

    def update_order(self, order_json: dict) -> APIResponse:
        url = '%s/%s' % (self._url, order_json['uuid'])
        api_response = self._put(url=url, data=order_json, headers=self._headers)
        return api_response

    def get_order(self, suuid: str = None, code: int = None) -> APIResponse:
        if suuid:
            url = '%s/uuid/%s' % (self._url, suuid)
        elif code:
            url = '%s/code/%s' % (self._url, code)
        else:
            raise KeyError
        api_response = self._get(url=url)

        return api_response


class UserDeviceAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, user_uuid: str, pin_code: str, device_token: str = None, device_name: str = None,
               location: str = None, is_active: str = None) -> APIResponse:
        us_json = {
            'user_uuid': user_uuid,
            'pin_code': pin_code,
            'device_token': device_token,
            'device_name': device_name,
            'location': location,
            'is_active': is_active,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._post(data=us_json, url=url)
        return api_response

    def update(self, user_uuid: str, suuid: str, pin_code: str, device_token: str, device_name: str, location: str,
               is_active: str, modify_reason: str) -> APIResponse:
        ud_json = {
            'uuid': suuid,
            'user_uuid': user_uuid,
            'pin_code': pin_code,
            'device_token': device_token,
            'device_name': device_name,
            'location': location,
            'is_active': is_active,
            'modify_reason': modify_reason,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = '%s/%s' % (url, suuid)
        api_response = self._put(data=ud_json, url=url)
        return api_response

    def get_user_device_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        url = '%s/%s' % (self._url.replace('<string:user_uuid>', user_uuid), suuid)
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

    def update(self, user_uuid: str, user_subscription_uuid: str, subscription_id: str, order_uuid: str,
               expire_date: datetime, modify_date: datetime, modify_reason: str) -> APIResponse:
        us_json = {
            'uuid': user_subscription_uuid,
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'expire_date': expire_date,
            'order_uuid': order_uuid,
            'modify_date': modify_date,
            'modify_reason': modify_reason,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = '%s/%s' % (url, user_subscription_uuid)
        api_response = self._put(data=us_json, url=url)
        return api_response

    def get_user_subs_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        url = '%s/%s' % (self._url.replace('<string:user_uuid>', user_uuid), suuid)
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

    def create_user(self, user_json: dict) -> APIResponse:
        api_response = self._post(data=user_json, headers=self._headers)
        return api_response

    def update_user(self, user_json: dict):
        url = '%s/uuid/%s' % (self._url, user_json['uuid'])
        api_response = self._put(url=url, data=user_json, headers=self._headers)
        return api_response

    def get_user(self, suuid: str = None, email: str = None) -> APIResponse:
        if suuid:
            url = '%s/uuid/%s' % (self._url, suuid)
        elif email:
            url = '%s/email/%s' % (self._url, email)
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
        url = "%s/type/%s" % (self._url, type_id)

        if pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset, url=url)

        api_response = self._get(url=url)
        return api_response

    def get_vpnservers_by_status(self, status_id: int, pagination: ResourcePagination) -> APIResponse:
        url = "%s/status/%s" % (self._url, status_id)

        if pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset, url=url)

        api_response = self._get(url=url)
        return api_response

    def get_vpnserver_by_uuid(self, suuid: str) -> APIResponse:
        url = '%s/%s' % (self._url, suuid)
        api_response = self._get(url=url)
        return api_response

    def update_vpnserver(self, vpnserver: dict) -> APIResponse:
        url = '%s/%s' % (self._url, vpnserver['uuid'])
        api_response = self._put(url=url, data=vpnserver)
        return api_response

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
        url = '%s/%s' % (self._url, sid)
        api_response = self._get(url=url)
        return api_response


class VPNServerConfigurationAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnserverconfig(self, server_uuid: str, user_uuid: str = None) -> APIResponse:
        url = '%s/%s/configurations/user/%s' % (self._url, server_uuid, user_uuid)
        api_response = self._get(url=url)
        return api_response

    def get_vpnserverconfig_by_uuid(self, suuid) -> APIResponse:
        url = '%s/%s' % (self._url, suuid)
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
        url = '%s/%s' % (self._url, sid)
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
        url = '%s/%s' % (self._url, sid)
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
        url = '%s/%s' % (self._url, sid)
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
        url = '%s/%s' % (self._url, code)
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
        url = '%s/%s' % (self._url, code)
        api_response = self._get(url=url)
        return api_response
