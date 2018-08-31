import datetime
import json
import logging
import sys

from app.model import VPNTypeEnum

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException
from response import APIResponse
from api import ResourcePagination


class OrderAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_order(self, status_id: int, payment_uuid: str = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_order method with parameters status_id: {status_id}, payment_uuid: {payment_uuid}")
        data = {
            'status_id': status_id,
            'payment_uuid': payment_uuid,
        }
        api_response = self._post(data=data, headers=self._headers)
        if 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            return api_response
        else:
            self.logger.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_order(self, order_json: dict):
        self.logger.debug(f"{self.__class__}: update_order method with parameters order_json: {order_json}")
        url = f"{self._url}/{order_json['uuid']}"
        self._put(url=url, data=order_json, headers=self._headers)

    def get_order(self, suuid: str = None, code: int = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_order method with parameters suuid: {suuid}, code: {code}")
        if suuid:
            url = f"{self._url}/uuid/{suuid}"
        elif code:
            url = f"{self._url}/code/{code}"
        else:
            raise KeyError
        api_response = self._get(url=url)

        return api_response

    def create_payment(self, order_uuid: str, type_id: int, status_id: int, json_data: dict):
        self.logger.debug(f"{self.__class__}: create_payment method with parameters order_uuid: {order_uuid}, type_id: {type_id}, "
                          f"status_id: {status_id}, json_data: {json_data}")

        url = f"{self._url}/{order_uuid}/payments"

        data = {
            'order_uuid': order_uuid,
            'type_id': type_id,
            'status_id': status_id,
            'json_data': json.dumps(json_data),
        }

        self.logger.debug(f"{self.__class__}: Create payment: {data}")
        api_response = self._post(url=url, data=data, headers=self._headers)

        if 'Location' in api_response.headers:
            api_response = self._get(url=api_response.headers.get('Location'))
            return api_response
        else:
            self.logger.debug(api_response.serialize())
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_payment(self, order_uuid: str, suuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_payment method with parameters order_uuid: {order_uuid}, suuid: {suuid}")
        url = f"{self._url}/{order_uuid}/payments/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def get_order_payments(self, order_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_order_payments method with parameters order_uuid: {order_uuid}")
        url = f"{self._url}/{order_uuid}/payments"
        api_response = self._get(url=url)
        return api_response


class UserDeviceAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, user_uuid: str, device_token: str, virtual_ip: str, device_id: str, platform_id: int,
               vpn_type_id: int, location: str, is_active: bool, device_ip: str = None,
               connected_since: datetime = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create method with parameters user_uuid: {user_uuid}, device_id: {device_id}, "
                          f"device_token: {device_token}, location: {location}, is_active: {is_active}, "
                          f"platform_id: {platform_id}, vpn_type_id: {vpn_type_id}, virtual_ip: {virtual_ip}, "
                          f"device_ip: {device_ip}, connected_since: {connected_since}")
        us_json = {
            'user_uuid': user_uuid,
            'device_id': device_id,
            'platform_id': platform_id,
            'vpn_type_id': vpn_type_id,
            'device_token': device_token,
            'location': location,
            'is_active': is_active,
            'virtual_ip': virtual_ip,
            'device_ip': device_ip,
            'connected_since': connected_since,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._post(data=us_json, url=url)
        return api_response

    def update(self, user_device: dict):
        self.logger.debug(f"{self.__class__}: update method with parameters user_device: {user_device}")
        url = self._url.replace('<string:user_uuid>', user_device['user_uuid'])
        url = f"{url}/{user_device['uuid']}"

        self._put(data=user_device, url=url)

    def delete(self, user_uuid: str, suuid: str):
        self.logger.debug(f"{self.__class__}: delete method with parameters user_uuid: {user_uuid}, suuid: {suuid}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = f"{url}/{suuid}"

        self._delete(url=url)

    def get_user_device_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_device_by_uuid method with parameters user_uuid: {user_uuid}, suuid: {suuid}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = f"{url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def get_user_devices(self, user_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_devices method with parameters user_uuid: {user_uuid}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._get(url=url)
        return api_response


class UserSubscriptionAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, user_uuid: str, subscription_id: str, order_uuid: str, status_id: int) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create method with parameters user_uuid: {user_uuid}, subscription_id: {subscription_id}, "
                          f"order_uuid: {order_uuid}, status_id: {status_id}")
        us_json = {
            'user_uuid': user_uuid,
            'subscription_id': subscription_id,
            'status_id': status_id,
            'order_uuid': order_uuid,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._post(data=us_json, url=url)
        return api_response

    def update(self, user_subscription: dict):
        self.logger.debug(f"{self.__class__}: update method with parameters user_subscription: {user_subscription}")
        url = self._url.replace('<string:user_uuid>', user_subscription['user_uuid'])
        url = f"{url}/{user_subscription['uuid']}"
        self._put(data=user_subscription, url=url)

    def get_user_sub_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_sub_by_uuid method with parameters user_uuid: {user_uuid}, suuid: {suuid}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = f"{url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def get_user_subs_by_user_uuid(self, user_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_subs_by_user_uuid method with parameters user_uuid: {user_uuid}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._get(url=url)
        return api_response


class UsersVPNServersConfigurationsAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def find(self, user_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: find method with parameters: user_uuid: {user_uuid}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._get(url=url)
        return api_response

    def find_by_platform_and_type(self, user_uuid: str, platform_id: int, vpn_type_id: int) -> APIResponse:
        self.logger.debug(f"{self.__class__}: find method with parameters: user_uuid: {user_uuid}, platform_id: {platform_id}, "
                          f"vpn_type_id: {vpn_type_id}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = f"{url}?platform_id={platform_id}&vpn_type_id={vpn_type_id}"
        api_response = self._get(url=url)
        return api_response

    def get_by_suuid(self, user_uuid: str, suuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_by_suuid method with parameters: user_uuid: {user_uuid}, suuid: {suuid}")
        url = self._url.replace('<string:user_uuid>', user_uuid)
        url = f"{url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def create(self, user_uuid: str, configuration: str, vpn_device_platform_id: int, vpn_type_id: int) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create method with parameters: user_uuid: {user_uuid},"
                          f"configuration: {configuration}, vpn_device_platform_id: {vpn_device_platform_id}, "
                          f"vpn_type_id: {vpn_type_id}")
        data = {
            'user_uuid': user_uuid,
            'configuration': configuration,
            'vpn_device_platform_id': vpn_device_platform_id,
            'vpn_type_id': vpn_type_id,
        }
        url = self._url.replace('<string:user_uuid>', user_uuid)
        api_response = self._post(data=data, url=url)
        return api_response


class SubscriptionAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_subscriptions(self, lang_code: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_subscriptions method with parameters lang_code: {lang_code}")
        headers = {
            'Accept-Language': lang_code
        }
        api_response = self._get(headers=headers)

        return api_response


class UserAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_user(self, email: str, password: str, is_expired: bool = False, is_locked: bool = False,
                    is_password_expired: bool = False, enabled: bool = False, pin_code: str = None,
                    pin_code_expire_date: datetime = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_user method with parameters email: {email}, password: {password}, "
                          f"is_expired: {is_expired}, "
                          f"is_locked: {is_locked}, is_password_expired: {is_password_expired}, enabled: {enabled}, "
                          f"pin_code: {pin_code}, pin_code_expire_date: {pin_code_expire_date}")
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
        self.logger.debug(f"{self.__class__}: update_user method with parameters user_dict: {user_dict}")

        url = f"{self._url}/{user_dict['uuid']}"
        self._put(url=url, data=user_dict, headers=self._headers)

    def get_user(self, suuid: str = None, email: str = None, pin_code: int = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user method with parameters suuid: {suuid}, email: {email}, pin_code: {pin_code}")
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

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnservers(self, pagination: ResourcePagination = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_vpnservers method with parameters pagination: {pagination}")
        if pagination is not None and pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset)
            api_response = self._get(url=url)
        else:
            api_response = self._get()
        return api_response

    def get_vpnservers_by_type(self, type_id: int, pagination: ResourcePagination) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_vpnservers_by_type method with parameters type_id: {type_id}, pagination: {pagination}")
        url = f"{self._url}/type/{type_id}"

        if pagination is not None and pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset, url=url)

        api_response = self._get(url=url)
        return api_response

    def get_vpnservers_by_status(self, status_id: int, pagination: ResourcePagination) -> APIResponse:
        self.logger.debug(
            f"get_vpnservers_by_status method with parameters status_id: {status_id}, pagination: {pagination}")
        url = f"{self._url}/status/{status_id}"
        if pagination is not None and pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset, url=url)

        api_response = self._get(url=url)
        return api_response

    def get_vpnserver_by_uuid(self, suuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_vpnserver_by_uuid method with parameters suuid: {suuid}")
        url = f"{self._url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def update_vpnserver(self, vpnserver: dict):
        self.logger.debug(f"{self.__class__}: update_vpnserver method with parameters vpnserver: {vpnserver}")
        url = f"{self._url}/{vpnserver['uuid']}"
        api_response = self._put(url=url, data=vpnserver)
        return api_response

    def create_vpnserver(self, vpnserver: dict) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_vpnserver method with parameters vpnserver: {vpnserver}")
        api_response = self._post(data=vpnserver)
        return api_response


class VPNServersMetaAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_meta(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_meta method")
        api_response = self._get()
        return api_response


class VPNTypeAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpntypes(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_vpntypes method")
        api_response = self._get()
        return api_response

    def get_vpntype_by_id(self, sid) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_vpntype_by_id method with parameters sid: {sid}")
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class VPNMGMTUsersAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create_vpn_user(self, email: str):
        self.logger.debug(f"{self.__class__}: create_vpn_user with parameters email: {email}")
        url = self._url.replace("<string:user_email>", email)
        api_response = self._post(data={}, url=url)
        return api_response

    def withdraw_vpn_user(self, email: str):
        self.logger.debug(f"{self.__class__}: withdraw_vpn_user with parameters email: {email}")
        url = self._url.replace("<string:user_email>", email)
        api_response = self._delete(url=url)
        return api_response


class VPNMGMTServerConnectionsAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def update_server_connections(self, ip_address: str, vpn_type: VPNTypeEnum):
        self.logger.debug(f"{self.__class__}: update_server_connections with parameters ip_address: {ip_address}, vpn_type: {vpn_type}")
        data = {
            'ip_list': [ip_address, ],
            'vpn_type_name': vpn_type.text
        }
        api_response = self._post(data=data)
        return api_response


class VPNServerConnectionsAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def create(self, server_uuid: str, user_uuid: str, user_device_uuid: str, device_ip: str, virtual_ip: str,
               bytes_i: str, bytes_o: str, is_connected: bool, connected_since: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create method with parameters server_uuid: {server_uuid}, user_uuid: {user_uuid},"
                          f"user_device_uuid: {user_device_uuid}, ip_device: {device_ip}, virtual_ip: {virtual_ip},"
                          f"bytes_i: {bytes_i}, bytes_o: {bytes_o}, is_connected: {is_connected}, "
                          f"connected_since: {connected_since}")
        data = {
            'server_uuid': server_uuid,
            'user_uuid': user_uuid,
            'user_device_uuid': user_device_uuid,
            'ip_device': device_ip,
            'virtual_ip': virtual_ip,
            'bytes_i': bytes_i,
            'bytes_o': bytes_o,
            'is_connected': is_connected,
            'connected_since': connected_since,
        }

        url = self._url.replace("<string:server_uuid>", server_uuid)
        api_response = self._post(data=data, url=url)
        return api_response

    def disconnect_by_server(self, server_uuid: str):
        self.logger.debug(f"{self.__class__}: disconnect_by_server method with parameters server_uuid: {server_uuid}")
        url = self._url.replace("<string:server_uuid>", server_uuid)
        self._delete(url=url)

    def update(self, server_connection_dict: dict):
        self.logger.debug(f"{self.__class__}: update method with parameters server_connection_dict: {server_connection_dict}")
        url = self._url.replace("<string:server_uuid>", server_connection_dict.get('server_uuid'))
        url = f"{url}/{server_connection_dict.get('uuid')}"
        api_response = self._put(url=url, data=server_connection_dict)
        return api_response

    def get_by_server_and_user(self, server_uuid: str, user_uuid: str = None) -> APIResponse:
        self.logger.debug(
            f"get_by_server_and_user method with parameters server_uuid: {server_uuid}, user_uuid: {user_uuid}")
        url = self._url.replace("<string:server_uuid>", server_uuid)
        url = f"{url}?user_uuid={user_uuid}"
        api_response = self._get(url=url)
        return api_response

    def get_by_server_and_suuid(self, server_uuid: str, suuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_by_server_and_suuid method with parameters server_uuid: {server_uuid}, suuid: {suuid}")
        url = self._url.replace("<string:server_uuid>", server_uuid)
        url = f"{url}/{suuid}"
        api_response = self._get(url=url)
        return api_response

    def get_current_by_server_and_user_device(self, server_uuid: str, user_device_uuid: str):
        self.logger.debug(f"{self.__class__}: get_current_by_server_and_user_device method with parameters server_uuid: {server_uuid}, "
                          f"user_device_uuid: {user_device_uuid}")
        url = self._url.replace("<string:server_uuid>", server_uuid)
        url = f"{url}?user_device_uuid={user_device_uuid}&is_connected=True"
        api_response = self._get(url=url)
        return api_response

    def get_current_by_server_and_user_and_vip(self, server_uuid: str, virtual_ip: str):
        self.logger.debug(f"{self.__class__}: get_current_by_user_device method with parameters server_uuid: {server_uuid}, "
                          f"virtual_ip: {virtual_ip}")
        url = self._url.replace("<string:server_uuid>", server_uuid)
        url = f"{url}?virtual_ip={virtual_ip}&is_connected=True"
        api_response = self._get(url=url)
        return api_response

    def get_all_by_user_device_uuid(self, user_device_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_all_by_user_device_uuid method with parameters user_device_uuid: {user_device_uuid}")
        url = self._url.replace("/<string:server_uuid>/", "/")
        url = f"{url}?user_device_uuid={user_device_uuid}"
        api_response = self._get(url=url)
        return api_response

    def get_current_by_user_device(self, user_device_uuid: str):
        self.logger.debug(f"{self.__class__}: get_current_by_server_and_user_device method with parameters "
                          f"user_device_uuid: {user_device_uuid}")
        url = self._url.replace("/<string:server_uuid>/", "/")
        url = f"{url}?user_device_uuid={user_device_uuid}&is_connected=True"
        api_response = self._get(url=url)
        return api_response


class VPNServerStatusAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnserverstatuses(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_vpnserverstatuses method with parameters ")
        api_response = self._get()
        return api_response

    def get_vpnserverstatuse_by_id(self, sid) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_vpnserverstatuse_by_id method with parameters sid: {sid}")
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class GeoPositionAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geoposes(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geoposes method with parameters ")
        api_response = self._get()
        return api_response

    def get_geopos_by_id(self, sid) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geopos_by_id method with parameters sid: {sid}")
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class GeoCityAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geocities(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geocities method ")
        api_response = self._get()
        return api_response

    def get_geocity_by_id(self, sid) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geocity_by_id method with parameters sid: {sid} ")
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response


class GeoCountryAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geocountries(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geocountries method")
        api_response = self._get()
        return api_response

    def get_geocountry_by_code(self, code) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geocountry_by_code method with parameters code: {code}")
        url = f"{self._url}/{code}"
        api_response = self._get(url=url)
        return api_response


class GeoStateAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geostates(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geostates method")
        api_response = self._get()
        return api_response

    def get_geostate_by_code(self, code) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_geostate_by_code method with parameters code: {code}")
        url = f"{self._url}/{code}"
        api_response = self._get(url=url)
        return api_response


class VPNDevicePlatformsAPIService(RESTService):
    __version__ = 1

    logger = logging.getLogger(__name__)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def find(self) -> APIResponse:
        self.logger.debug(f"{self.__class__}: find method with parameters ")
        api_response = self._get()
        return api_response

    def find_by_id(self, sid: int) -> APIResponse:
        self.logger.debug(f"{self.__class__}: find_by_id method with parameters ")
        url = f"{self._url}/{sid}"
        api_response = self._get(url=url)
        return api_response
