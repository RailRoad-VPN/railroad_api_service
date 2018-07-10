from typing import List, Optional

from app.service import *

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from response import APIResponse
from api import ResourcePagination


class UserPolicy(object):
    __version__ = 1

    user_api_service = None
    user_sub_api_service = None
    order_api_service = None
    payment_api_service = None

    def __init__(self, user_sub_api_service: UserSubscriptionAPIService, user_api_service: UserAPIService,
                 order_api_service: OrderAPIService, user_device_api_service: UserDeviceAPIService):
        self._user_api_service = user_api_service
        self._user_device_api_service = user_device_api_service
        self._user_sub_api_service = user_sub_api_service
        self._order_api_service = order_api_service

    def create_user_sub(self, user_uuid: str, subscription_id: str, order_uuid: str):
        return self._user_sub_api_service.create(user_uuid=user_uuid, subscription_id=subscription_id,
                                                 order_uuid=order_uuid)

    def update_user_sub(self, user_uuid: str, user_subscription_uuid: str, subscription_id: str, order_uuid: str,
                        expire_date: datetime, modify_date: datetime, modify_reason: str) -> APIResponse:
        api_response = self._user_sub_api_service.update(user_uuid=user_uuid,
                                                         user_subscription_uuid=user_subscription_uuid,
                                                         subscription_id=subscription_id, order_uuid=order_uuid,
                                                         expire_date=expire_date, modify_date=modify_date,
                                                         modify_reason=modify_reason)
        return api_response

    def get_user_sub_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        api_response = self._user_sub_api_service.get_user_subs_by_uuid(user_uuid=user_uuid, suuid=suuid)
        if api_response.is_ok:
            enriched_user_sub = self.__enrich_user_sub(user_sub=api_response.data)
            api_response.data = enriched_user_sub
        return api_response

    def get_user_subs(self, user_uuid: str) -> APIResponse:
        api_response = self._user_sub_api_service.get_user_subs_by_user_uuid(user_uuid=user_uuid)
        if api_response.is_ok:
            enriched_user_subs = []
            for user_sub in api_response.data:
                enriched_user_sub = self.__enrich_user_sub(user_sub=user_sub)
                enriched_user_subs.append(enriched_user_sub)
        return api_response

    def __enrich_user_sub(self, user_sub) -> Optional[dict]:
        # is expired
        expire_date = user_sub['expire_date']
        now = datetime.datetime.now()
        is_expired = False
        import dateutil.parser
        expire_date = dateutil.parser.parse(expire_date)
        if expire_date < now:
            is_expired = True
        user_sub['is_expired'] = is_expired
        return user_sub

    def get_user(self, suuid: str = None, email: str = None) -> APIResponse:
        api_response = self._user_api_service.get_user(suuid=suuid, email=email)
        return api_response

    def create_user(self, user_json) -> APIResponse:
        api_response = self._user_api_service.create_user(user_json=user_json)
        return api_response

    def update_user(self, user_json) -> APIResponse:
        api_response = self._user_api_service.update_user(user_json=user_json)
        return api_response

    def create_user_device(self, user_uuid: str, pin_code: int) -> APIResponse:
        api_response = self._user_device_api_service.create(user_uuid=user_uuid, pin_code=pin_code)
        return api_response

    def update_user_device(self, user_uuid: str, pin_code: int, device_token: str, device_id: str,
                           location: str, is_active: bool, modify_reason: str, suuid: str = None) -> APIResponse:
        api_response = self._user_device_api_service.update(suuid=suuid, user_uuid=user_uuid, pin_code=pin_code,
                                                            device_token=device_token, device_id=device_id,
                                                            location=location, is_active=is_active,
                                                            modify_reason=modify_reason)
        return api_response

    def get_user_device_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        api_response = self._user_device_api_service.get_user_device_by_uuid(user_uuid=user_uuid, suuid=suuid)
        return api_response

    def get_user_devices(self, user_uuid: str) -> APIResponse:
        api_response = self._user_device_api_service.get_user_devices(user_uuid=user_uuid)
        return api_response

    def get_user_uuid_by_pincode(self, pin_code: int):
        api_response = self._user_api_service.get_user(pin_code=pin_code)
        return api_response


class VPNServerPolicy(object):
    __version__ = 1

    vpnserver_api_service = None
    vpntype_api_service = None
    vpnserverconf_api_service = None
    vpnserverstatus_api_service = None
    geoposition_api_service = None
    geocity_api_service = None
    geocountry_api_service = None
    geostate_api_service = None

    def __init__(self, vpnserver_service: VPNServersAPIService, vpntype_service: VPNTypeAPIService,
                 vpnserverconfiguration_service: VPNServerConfigurationAPIService,
                 vpnserverstatus_service: VPNServerStatusAPIService, geoposition_service: GeoPositionAPIService,
                 geocity_service: GeoCityAPIService, geocountry_service: GeoCountryAPIService,
                 geostate_service: GeoStateAPIService):
        self.vpnserver_api_service = vpnserver_service
        self.vpntype_api_service = vpntype_service
        self.vpnserverconf_api_service = vpnserverconfiguration_service
        self.vpnserverstatus_api_service = vpnserverstatus_service
        self.geoposition_api_service = geoposition_service
        self.geocity_api_service = geocity_service
        self.geocountry_api_service = geocountry_service
        self.geostate_api_service = geostate_service

    def create_vpn_server(self, vpnserver: dict) -> APIResponse:
        api_response = self.vpnserver_api_service.create_vpnserver(vpnserver=vpnserver)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        return api_response

    def update_vpn_server(self, vpnserver: dict) -> APIResponse:
        api_response = self.vpnserver_api_service.update_vpnserver(vpnserver=vpnserver)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors, data=api_response.data)
        return api_response

    def get_random_vpn_server(self, type_id: int = None, status_id: int = None) -> str:
        # TODO some logic to get random VPN server

        pagination = ResourcePagination(limit=1, offset=0)

        if type_id is not None:
            api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)
        elif status_id is not None:
            api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id,
                                                                               pagination=pagination)
        else:
            api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)

        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data[0]

        return server['uuid']

    def get_vpn_server_list(self, pagination: ResourcePagination = None) -> List[dict]:
        api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_condition_list(self, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition(self, suuid: str):
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data

        return self._get_vpn_server_condition(server=server)

    def _get_vpn_server_condition(self, server: dict) -> dict:
        server.pop("geo_position_id", None)
        server.pop("type_id", None)
        return server

    def get_vpn_server(self, suuid: str) -> dict:
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data

        return self._get_vpn_server(server=server)

    def get_vpn_server_configuration(self, server_uuid: str, user_uuid: str = None) -> dict:
        api_response = self.vpnserverconf_api_service.get_vpnserverconfig(server_uuid=server_uuid,
                                                                          user_uuid=user_uuid)
        if not api_response.is_ok:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        return api_response.data

    def _get_vpn_server(self, server: dict) -> dict:
        geo_position_id = server.pop("geo_position_id")

        api_response = self.geoposition_api_service.get_geopos_by_id(sid=geo_position_id)
        if not api_response.is_ok:
            return server

        geopos = api_response.data
        geopos.pop("id", None)

        server['geo'] = geopos

        return server
