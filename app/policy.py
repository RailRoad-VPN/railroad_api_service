from typing import List

from app.service import *

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from api import ResourcePagination


class UserPolicy(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    user_api_service = None
    user_sub_api_service = None
    order_api_service = None
    payment_api_service = None

    def __init__(self, user_sub_api_service: UserSubscriptionAPIService, user_api_service: UserAPIService,
                 order_api_service: OrderAPIService, user_device_api_service: UserDeviceAPIService,
                 vpnserversconnections_service: VPNServerConnectionsAPIService):
        self._user_api_service = user_api_service
        self._user_device_api_service = user_device_api_service
        self._user_sub_api_service = user_sub_api_service
        self._order_api_service = order_api_service
        self._vpnserversconnections_service = vpnserversconnections_service

    def create_user_sub(self, user_uuid: str, subscription_id: str, order_uuid: str, status_id: int) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_user_sub method with parameter user_uuid: {user_uuid}, "
                          f"subscription_id: {subscription_id}, "
                          f"order_uuid: {order_uuid}, status_id: {status_id}")
        api_response = self._user_sub_api_service.create(user_uuid=user_uuid, subscription_id=subscription_id,
                                                         order_uuid=order_uuid, status_id=status_id)
        location = api_response.headers.get('Location', None)
        if location is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self._user_sub_api_service.get_user_sub_by_uuid(user_uuid=user_uuid, suuid=suuid)
        return api_response

    def update_user_sub(self, user_subscription: dict):
        self.logger.debug(
            f"{self.__class__}: update_user_sub method with parameter user_subscription: {user_subscription}")
        self._user_sub_api_service.update(user_subscription=user_subscription)

    def get_user_sub_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        api_response = self._user_sub_api_service.get_user_sub_by_uuid(user_uuid=user_uuid, suuid=suuid)
        return api_response

    def get_user_subs(self, user_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_subs method with parameter user_uuid: {user_uuid}")
        self.logger.debug(f"{self.__class__}: Get user subscriptions by user uuid")
        api_response = self._user_sub_api_service.get_user_subs_by_user_uuid(user_uuid=user_uuid)
        return api_response

    def get_user(self, suuid: str = None, email: str = None, pin_code: str = None) -> APIResponse:
        self.logger.debug(
            f"{self.__class__}: get_user method with parameters suuid : {suuid}, email : {email}, pin_code: {pin_code}")
        api_response = self._user_api_service.get_user(suuid=suuid, email=email, pin_code=pin_code)
        return api_response

    def create_user(self, email: str, password: str, is_expired: bool = False, is_locked: bool = False,
                    is_password_expired: bool = False, enabled: bool = False, pin_code: str = None,
                    pin_code_expire_date: datetime = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_user method with parameters email: {email}, password: {password}, "
                          f"is_expired: {is_expired}, is_locked: {is_locked}, is_password_expired: {is_password_expired}, "
                          f"enabled: {enabled}, pin_code: {pin_code}, pin_code_expire_date: {pin_code_expire_date}")
        api_response = self._user_api_service.create_user(email=email, password=password, is_expired=is_expired,
                                                          is_locked=is_locked, is_password_expired=is_password_expired,
                                                          enabled=enabled, pin_code=pin_code,
                                                          pin_code_expire_date=pin_code_expire_date)
        location = api_response.headers.get('Location', None)
        if location is None:
            self.logger.error(f"no Location header. raise APIException")
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self._user_api_service.get_user(suuid=suuid)
        return api_response

    def update_user(self, user_dict: dict):
        self.logger.debug(f"{self.__class__}: update_user method with parameter user_dict: {user_dict}")
        self._user_api_service.update_user(user_dict=user_dict)

    def create_user_device(self, user_uuid: str, device_token: str, virtual_ip: str, device_id: str, platform_id: int,
                           vpn_type_id: int, location: str, is_active: bool, connected_since: datetime = None,
                           device_ip: str = None) -> APIResponse:
        self.logger.debug(
            f"{self.__class__}: create_user_device method with parameters user_uuid: {user_uuid}, device_id: {device_id}, "
            f"device_token: {device_token}, location: {location}, is_active: {is_active}, "
            f"platform_id: {platform_id}, vpn_type_id: {vpn_type_id}, virtual_ip: {virtual_ip}, "
            f"device_ip: {device_ip}, connected_since: {connected_since}")
        api_response = self._user_device_api_service.create(user_uuid=user_uuid, device_token=device_token,
                                                            vpn_type_id=vpn_type_id, device_id=device_id,
                                                            virtual_ip=virtual_ip, device_ip=device_ip,
                                                            platform_id=platform_id, location=location,
                                                            is_active=is_active, connected_since=connected_since)
        x_device_token = api_response.headers.get('X-Device-Token', None)
        if x_device_token is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        location = api_response.headers.get('Location', None)
        if location is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self._user_device_api_service.get_user_device_by_uuid(user_uuid=user_uuid, suuid=suuid)
        api_response.headers['X-Device-Token'] = x_device_token
        return api_response

    def update_user_device(self, user_device: dict):
        self.logger.debug(f"{self.__class__}: update_user_device method with parameters user_device: {user_device}")
        self._user_device_api_service.update(user_device=user_device)

    def delete_user_device(self, user_uuid: str, suuid: str):
        self.logger.debug(f"{self.__class__}: update_user_device method with parameters user_uuid: {user_uuid}, "
                          f"suuid: {suuid}")
        self._user_device_api_service.delete(user_uuid=user_uuid, suuid=suuid)

    def get_user_device_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: {self.__class__}: get_user_device_by_uuid method with parameters " 
                          f"user_uuid: {user_uuid}, suuid: {suuid}")
        api_response = self._user_device_api_service.get_user_device_by_uuid(user_uuid=user_uuid, suuid=suuid)
        self.logger.debug(f"got api response: {api_response.serialize()}")
        try:
            self.logger.debug(f"try to retrieve connections for user device with uuid: {api_response.data.get('uuid')}")
            api_response.data['connections'] = self._get_user_device_connections(user_device=api_response.data)
        except APIException as e:
            self.logger.error(f"failed to retrieve connections for user device "
                              f"with uuid: {api_response.data.get('uuid')}")
            return api_response

    def get_user_devices(self, user_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_devices method with parameters user_uuid: {user_uuid}")
        api_response = self._user_device_api_service.get_user_devices(user_uuid=user_uuid)
        try:
            for ud in api_response.data:
                user_device_connection_list = self._get_user_device_connections(user_device=ud)
                if user_device_connection_list:
                    ud['_connections'] = user_device_connection_list
        except APIException as e:
            pass
        return api_response

    def _get_user_device_connections(self, user_device: dict):
        user_device_connection = self._vpnserversconnections_service.get_all_by_user_device_uuid(
            user_device_uuid=user_device.get('uuid')).data
        return user_device_connection


class VPNServerPolicy(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    vpnserver_api_service = None
    vpntype_api_service = None
    vpnserverconf_api_service = None
    vpnserverstatus_api_service = None
    geoposition_api_service = None
    geocity_api_service = None
    geocountry_api_service = None
    geostate_api_service = None

    def __init__(self, vpnserver_service: VPNServersAPIService, vpntype_service: VPNTypeAPIService,
                 vpnserverconfiguration_service: UsersVPNServersConfigurationsAPIService,
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

    def create_vpn_server_user_configuration(self, server_uuid: str, user_uuid: str, cert: str):
        self.logger.debug(
            f"{self.__class__}: create_vpn_server_user_configuration method with parameters server_uuid: {server_uuid}, "
            f"user_uuid: {user_uuid}, cert: {cert}")

        self.logger.debug(f"{self.__class__}: get vpn server by uuid: {server_uuid}")
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=server_uuid)
        server = api_response.data
        self.logger.debug(f"{self.__class__}: vpn server: {server}")

        self.logger.debug(f"{self.__class__}: create vpn Configuration")
        configuration = ''
        platform_id = 0

        self.vpnserverconf_api_service.create(user_uuid=user_uuid, server_uuid=server_uuid,
                                              configuration=configuration, platform_id=platform_id)

        # TODO

    def create_vpn_server(self, vpnserver: dict) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_vpn_server method with parameters vpnserver: {vpnserver}")
        api_response = self.vpnserver_api_service.create_vpnserver(vpnserver=vpnserver)

        location = api_response.headers.get('Location', None)
        if location is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)
        return api_response.data

    def update_vpn_server(self, vpnserver: dict) -> APIResponse:
        self.logger.debug(f"{self.__class__}: update_vpn_server method with parameter vpnserver: {vpnserver}")
        api_response = self.vpnserver_api_service.update_vpnserver(vpnserver=vpnserver)
        return api_response

    def get_random_vpn_server(self, type_id: int = None, status_id: int = None) -> APIResponse:
        self.logger.debug(
            f"{self.__class__}: get_random_vpn_server method with parameters type_id: {type_id}, status_id: {status_id}")
        # TODO some logic to get random VPN server

        pagination = ResourcePagination(limit=1, offset=0)

        if type_id is not None:
            api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)
        elif status_id is not None:
            api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id,
                                                                               pagination=pagination)
        else:
            api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)

        server = api_response.data[0]

        return server['uuid']

    def get_vpn_server_list(self, pagination: ResourcePagination = None) -> List[dict]:
        self.logger.debug(f"{self.__class__}: get_vpn_server_list method with parameters pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"get_vpn_server_list_by_type method with parameters type_id: {type_id}, pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_list_by_status method with parameters status_id: {status_id}, "
            f"pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_condition_list(self, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_condition_list method with parameters pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_condition_list_by_type method with parameters type_id: {type_id}. "
            f"pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_condition_list_by_status method with parameters status_id: {status_id}, "
            f"pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition(self, suuid: str):
        self.logger.debug(f"{self.__class__}: get_vpn_server_condition method with parameters suuid: {suuid}")
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)

        server = api_response.data

        return self._get_vpn_server_condition(server=server)

    def _get_vpn_server_condition(self, server: dict) -> dict:
        self.logger.debug(f"{self.__class__}: _get_vpn_server_condition method with parameters server: {server}")
        server.pop("geo_position_id", None)
        server.pop("type_id", None)
        return server

    def get_vpn_server(self, suuid: str) -> dict:
        self.logger.debug(f"{self.__class__}: get_vpn_server method with parameters suuid: {suuid}")
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)
        return self._get_vpn_server(server=api_response.data)

    def _get_vpn_server(self, server: dict) -> dict:
        self.logger.debug(f"{self.__class__}: _get_vpn_server method with parameters server: {server}")
        geo_position_id = server.get("geo_position_id")

        try:
            self.logger.info(f"get geopos by id: {geo_position_id}")
            api_response = self.geoposition_api_service.get_geopos_by_id(sid=geo_position_id)
        except APIException as e:
            self.logger.error("Can not retrieve geo position by id")
            self.logger.error(e)
            return server

        geopos = api_response.data

        server['geo'] = geopos

        return server
