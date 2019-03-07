from typing import List

from app.exception import UserPolicyException, RailRoadAPIError
from app.model.vpn_conf_platform import VPNConfigurationPlatform
from app.model.vpn_type import VPNType
from app.service import *

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from api import ResourcePagination


class UserPolicy(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _rrn_user_api_service = None
    _rrn_user_tickets_api_service = None
    _rrn_user_device_api_service = None
    _rrn_user_rrnservice_api_service = None
    _rrn_order_api_service = None
    _rrn_vpn_servers_connections_api_service = None
    _rrn_vpn_mgmt_users_api_service = None
    _rrn_vpn_server_configurations_service = None

    def __init__(self,
                 rrn_user_rrnservice_api_service: UserRRNServiceAPIService,
                 rrn_user_api_service: UserAPIService,
                 rrn_user_tickets_api_service: UserTicketsAPIService,
                 rrn_order_api_service: OrderAPIService,
                 rrn_user_device_api_service: UserDeviceAPIService,
                 rrn_vpn_servers_connections_api_service: VPNServerConnectionsAPIService,
                 rrn_vpn_mgmt_users_api_service: VPNMGMTUsersAPIService,
                 rrn_vpn_server_configurations_api_service: UsersVPNServersConfigurationsAPIService):
        self._rrn_user_api_service = rrn_user_api_service
        self._rrn_user_tickets_api_service = rrn_user_tickets_api_service
        self._rrn_user_device_api_service = rrn_user_device_api_service
        self._rrn_user_rrnservice_api_service = rrn_user_rrnservice_api_service
        self._rrn_order_api_service = rrn_order_api_service
        self._rrn_vpn_servers_connections_api_service = rrn_vpn_servers_connections_api_service
        self._rrn_vpn_mgmt_users_api_service = rrn_vpn_mgmt_users_api_service
        self._rrn_vpn_server_configurations_service = rrn_vpn_server_configurations_api_service

    def create_user_ticket(self, user_uuid: str, contact_email: str, description: str, extra_info: dict,
                           zipfile: bytearray = None) -> APIResponse:
        extra_info_s = json.dumps(extra_info)
        api_response = self._rrn_user_tickets_api_service.create(user_uuid=user_uuid, contact_email=contact_email,
                                                                 extra_info=extra_info_s, description=description,
                                                                 zipfile=zipfile)
        return api_response

    def get_user_ticket_by_number(self, user_uuid: str, ticket_number: int) -> APIResponse:
        api_response = self._rrn_user_tickets_api_service.find(user_uuid=user_uuid, ticket_number=ticket_number)
        return api_response

    def get_user_ticket(self, user_uuid: str, ticket_uuid: str) -> APIResponse:
        api_response = self._rrn_user_tickets_api_service.find(user_uuid=user_uuid, suuid=ticket_uuid)
        return api_response

    def get_user_tickets(self, user_uuid: str) -> APIResponse:
        api_response = self._rrn_user_tickets_api_service.find(user_uuid=user_uuid)
        return api_response

    def create_user_service(self, user_uuid: str, service_id: str, order_uuid: str, status_id: int,
                            expire_date: datetime, is_trial: bool) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_user_service method with parameter user_uuid: {user_uuid}, "
                          f"service_id: {service_id}, is_trial: {is_trial}, expire_date: {expire_date},"
                          f"order_uuid: {order_uuid}, status_id: {status_id}")
        api_response = self._rrn_user_rrnservice_api_service.create(user_uuid=user_uuid, service_id=service_id,
                                                                    order_uuid=order_uuid, status_id=status_id,
                                                                    expire_date=expire_date, is_trial=is_trial)
        location = api_response.headers.get('Location', None)
        if location is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self._rrn_user_rrnservice_api_service.get_user_service_by_uuid(user_uuid=user_uuid, suuid=suuid)
        return api_response

    def update_user_sub(self, user_subscription: dict):
        self.logger.debug(
            f"{self.__class__}: update_user_sub method with parameter user_subscription: {user_subscription}")
        self._rrn_user_rrnservice_api_service.update(user_service=user_subscription)

    def get_user_service_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        api_response = self._rrn_user_rrnservice_api_service.get_user_service_by_uuid(user_uuid=user_uuid, suuid=suuid)
        return api_response

    def get_user_services(self, user_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_subs method with parameter user_uuid: {user_uuid}")
        self.logger.debug(f"{self.__class__}: Get user services by user uuid")
        api_response = self._rrn_user_rrnservice_api_service.get_user_services_by_user_uuid(user_uuid=user_uuid)
        return api_response

    def get_user(self, suuid: str = None, email: str = None, pin_code: str = None) -> APIResponse:
        self.logger.debug(
            f"{self.__class__}: get_user method with parameters suuid : {suuid}, email : {email}, pin_code: {pin_code}")
        api_response = self._rrn_user_api_service.get_user(suuid=suuid, email=email, pin_code=pin_code)
        return api_response

    def create_user(self, email: str, password: str, is_expired: bool = False, is_locked: bool = False,
                    is_password_expired: bool = False, enabled: bool = False, pin_code: str = None,
                    pin_code_expire_date: datetime = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_user method with parameters email: {email}, password: {password}, "
                          f"is_expired: {is_expired}, is_locked: {is_locked}, "
                          f"is_password_expired: {is_password_expired}, enabled: {enabled}, pin_code: {pin_code}, "
                          f"pin_code_expire_date: {pin_code_expire_date}")

        try:
            user_api_response = self._rrn_user_api_service.create_user(email=email,
                                                                       password=password,
                                                                       is_expired=is_expired,
                                                                       is_locked=is_locked,
                                                                       is_password_expired=is_password_expired,
                                                                       enabled=enabled,
                                                                       pin_code=pin_code,
                                                                       pin_code_expire_date=pin_code_expire_date)
        except APIException as e:
            self.logger.debug(e.serialize())
            raise UserPolicyException(error=RailRoadAPIError.UNKNOWN_ERROR_CODE.message,
                                      error_code=RailRoadAPIError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=RailRoadAPIError.UNKNOWN_ERROR_CODE.developer_message)

        location = user_api_response.headers.get('Location', None)
        if location is None:
            self.logger.error(f"No Location header")
            raise UserPolicyException(error=RailRoadAPIError.UNKNOWN_ERROR_CODE.message,
                                      error_code=RailRoadAPIError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=RailRoadAPIError.UNKNOWN_ERROR_CODE.developer_message)

        suuid = location.split('/')[-1]

        try:
            self.logger.debug(f"{self.__class__}: get user by uuid from Location HTTP header")
            user_api_response = self._rrn_user_api_service.get_user(suuid=suuid)
            user_json = user_api_response.data
            self.logger.debug(f"{self.__class__}: user: {user_json}")
        except APIException as e:
            self.logger.debug(e.serialize())
            raise UserPolicyException(error=RailRoadAPIError.UNKNOWN_ERROR_CODE.message,
                                      error_code=RailRoadAPIError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=RailRoadAPIError.UNKNOWN_ERROR_CODE.developer_message)

        user_uuid = user_json.get('uuid')
        user_email = user_json.get('email')

        try:
            self.logger.debug(f"{self.__class__}: call vpn mgmt users api service")
            api_response = self._rrn_vpn_mgmt_users_api_service.create_vpn_user(email=user_email)
            user_configurations = api_response.data
            self.logger.debug(f"{self.__class__}: user_configurations: {user_configurations}")
        except APIException as e:
            self.logger.debug(e.serialize())
            raise UserPolicyException(error=RailRoadAPIError.UNKNOWN_ERROR_CODE.message,
                                      error_code=RailRoadAPIError.UNKNOWN_ERROR_CODE.code,
                                      developer_message=RailRoadAPIError.UNKNOWN_ERROR_CODE.developer_message)

        self.logger.debug(f"{self.__class__}: get openvpn user configs")
        openvpn = user_configurations.get(VPNType.OPENVPN.text, None)

        self.logger.debug(f"{self.__class__}: get ikev2 user configs")
        ikev2 = user_configurations.get(VPNType.IKEV2.text, None)

        openvpn_win_config = None
        openvpn_android_config = None
        ikev2_ios_config = None

        if openvpn is not None:
            self.logger.debug(f"{self.__class__}: we have openvpn configs. check platforms")
            openvpn_win_config = openvpn.get(VPNConfigurationPlatform.WINDOWS.text)
            openvpn_android_config = openvpn.get(VPNConfigurationPlatform.ANDROID.text)
        else:
            self.logger.debug(f"{self.__class__}: we have NO openvpn configs")

        if ikev2 is not None:
            self.logger.debug(f"{self.__class__}: we have ikev2 configs. check platforms")
            ikev2_ios_config = ikev2.get(VPNConfigurationPlatform.IOS.text)
        else:
            self.logger.debug(f"{self.__class__}: we have NO ikev2 configs")

        if openvpn_win_config is not None:
            self.logger.debug(f"{self.__class__}: we have openvpn for windows configuration. save it")
            self._rrn_vpn_server_configurations_service.create(user_uuid=user_uuid,
                                                               configuration=openvpn_win_config,
                                                               vpn_device_platform_id=VPNConfigurationPlatform.WINDOWS.sid,
                                                               vpn_type_id=VPNType.OPENVPN.sid)
        if openvpn_android_config is not None:
            self.logger.debug(f"{self.__class__}: we have openvpn for android configuration. save it")
            self._rrn_vpn_server_configurations_service.create(user_uuid=user_uuid,
                                                               configuration=openvpn_win_config,
                                                               vpn_device_platform_id=VPNConfigurationPlatform.ANDROID.sid,
                                                               vpn_type_id=VPNType.OPENVPN.sid)

        if ikev2_ios_config is not None:
            self.logger.debug(f"{self.__class__}: we have ikev2 for ios configuration. save it")
            self._rrn_vpn_server_configurations_service.create(user_uuid=user_uuid,
                                                               configuration=ikev2_ios_config,
                                                               vpn_device_platform_id=VPNConfigurationPlatform.IOS.sid,
                                                               vpn_type_id=VPNType.IKEV2.sid)
        return user_api_response

    def update_user(self, user_dict: dict) -> None:
        self.logger.debug(f"{self.__class__}: update_user method with parameter user_dict: {user_dict}")
        self._rrn_user_api_service.update_user(user_dict=user_dict)

    def create_user_device(self, user_uuid: str, device_id: str, platform_id: int,
                           vpn_type_id: int, location: str, is_active: bool, device_ip: str = None) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_user_device method with parameters user_uuid: {user_uuid}, "
                          f"device_id: {device_id}, location: {location}, "
                          f"is_active: {is_active}, platform_id: {platform_id}, vpn_type_id: {vpn_type_id}")
        api_response = self._rrn_user_device_api_service.create(user_uuid=user_uuid, vpn_type_id=vpn_type_id,
                                                                device_id=device_id,
                                                                platform_id=platform_id, location=location,
                                                                is_active=is_active)
        self.logger.debug("Check X-Device-Token")
        x_device_token = api_response.headers.get('X-Device-Token', None)
        if x_device_token is None:
            self.logger.debug("Bad X-Device-Token")
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        self.logger.debug("Get Location HTTP Header from response")
        location = api_response.headers.get('Location', None)
        if location is None:
            self.logger.debug("Bad Location HTTP Header")
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        self.logger.debug("Get uuid of created user device from location HTTP header value")
        suuid = location.split('/')[-1]
        self.logger.debug(f"uuid: {suuid}")
        api_response = self._rrn_user_device_api_service.get_user_device_by_uuid(user_uuid=user_uuid, suuid=suuid)
        api_response.headers['X-Device-Token'] = x_device_token
        return api_response

    def update_user_device(self, user_device: dict):
        self.logger.debug(f"{self.__class__}: update_user_device method with parameters user_device: {user_device}")
        self._rrn_user_device_api_service.update(user_device=user_device)

    def delete_user_device(self, user_uuid: str, suuid: str):
        self.logger.debug(f"{self.__class__}: update_user_device method with parameters user_uuid: {user_uuid}, "
                          f"suuid: {suuid}")
        self._rrn_user_device_api_service.delete(user_uuid=user_uuid, suuid=suuid)

    def get_user_devices_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        """
            suuid is uuid or device_id
        """
        self.logger.debug(f"{self.__class__}: get_user_devices_by_uuid method with parameters "
                          f"user_uuid: {user_uuid}, suuid: {suuid}")
        api_response = self._rrn_user_device_api_service.get_user_device_by_uuid(user_uuid=user_uuid, suuid=suuid)
        self.logger.debug(f"{self.__class__}: got api response: {api_response.serialize()}")
        try:
            self.logger.debug(f"{self.__class__}: try to retrieve connections for "
                              f"user device with uuid: {api_response.data.get('uuid')}")
            user_device_list = self._get_user_device_connections(user_device=api_response.data)
            self.logger.debug(f"{self.__class__}: got user_device_connections_api_response: "
                              f"{user_device_list}")
            self.logger.debug(f"{self.__class__}: set user device connections to user device api response")
            conns_list = []
            for udc in user_device_list:
                conns_list.append(udc)
            api_response.data['connections'] = conns_list
        except APIException as e:
            self.logger.error(f"failed to retrieve connections for user device "
                              f"with uuid: {api_response.data.get('uuid')}")

        return api_response

    def get_user_devices(self, user_uuid: str) -> APIResponse:
        self.logger.debug(f"{self.__class__}: get_user_devices method with parameters user_uuid: {user_uuid}")
        api_response = self._rrn_user_device_api_service.get_user_devices(user_uuid=user_uuid)
        for user_device in api_response.data:
            bytes_i = 0
            bytes_o = 0
            try:
                self.logger.debug(f"get connection for user_device with uuid:{user_device['uuid']}")
                user_device_connection_list = self._get_user_device_connections(user_device=user_device)
                self.logger.debug(f"got connections. size:{len(user_device_connection_list)}")
                if user_device_connection_list:
                    user_device['_connections'] = user_device_connection_list
                    for user_device_connection in user_device_connection_list:
                        if 'is_connected' in user_device_connection and user_device_connection['is_connected']:
                            user_device['is_connected'] = True
                        if 'bytes_i' in user_device_connection:
                            bytes_i += int(user_device_connection['bytes_i'])
                        if 'bytes_o' in user_device_connection:
                            bytes_o += int(user_device_connection['bytes_o'])
                    user_device['bytes_i'] = bytes_i
                    user_device['bytes_o'] = bytes_o
            except APIException as e:
                self.logger.debug(f"APIException when get connections for user device")
        return api_response

    def _get_user_device_connections(self, user_device: dict):
        user_device_connection = self._rrn_vpn_servers_connections_api_service.get_all_by_user_device_uuid(
            user_device_uuid=user_device.get('uuid')).data
        return user_device_connection


class VPNServerPolicy(object):
    __version__ = 1

    logger = logging.getLogger(__name__)

    _rrn_vpn_servers_api_service = None
    _rrn_vpn_types_api_service = None
    _rrn_vpn_server_configurations_api_service = None
    _rrn_vpn_server_statuses_api_service = None
    _rrn_geo_position_api_service = None
    _rrn_geo_city_api_service = None
    _rrn_geo_country_api_service = None
    _rrn_geo_state_api_service = None

    def __init__(self,
                 rrn_vpn_servers_api_service: VPNServersAPIService,
                 rrn_vpn_types_api_service: VPNTypeAPIService,
                 rrn_vpn_server_configurations_api_service: UsersVPNServersConfigurationsAPIService,
                 rrn_vpn_server_statuses_api_service: VPNServerStatusAPIService,
                 rrn_geo_position_api_service: GeoPositionAPIService,
                 rrn_geo_city_api_service: GeoCityAPIService,
                 rrn_geo_country_api_service: GeoCountryAPIService,
                 rrn_geo_state_api_service: GeoStateAPIService):
        self._rrn_vpn_servers_api_service = rrn_vpn_servers_api_service
        self._rrn_vpn_types_api_service = rrn_vpn_types_api_service
        self._rrn_vpn_server_configurations_api_service = rrn_vpn_server_configurations_api_service
        self._rrn_vpn_server_statuses_api_service = rrn_vpn_server_statuses_api_service
        self._rrn_geo_position_api_service = rrn_geo_position_api_service
        self._rrn_geo_city_api_service = rrn_geo_city_api_service
        self._rrn_geo_country_api_service = rrn_geo_country_api_service
        self._rrn_geo_state_api_service = rrn_geo_state_api_service

    def create_vpn_server(self, vpnserver: dict) -> APIResponse:
        self.logger.debug(f"{self.__class__}: create_vpn_server method with parameters vpnserver: {vpnserver}")
        api_response = self._rrn_vpn_servers_api_service.create_vpnserver(vpnserver=vpnserver)

        location = api_response.headers.get('Location', None)
        if location is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self._rrn_vpn_servers_api_service.get_vpnserver_by_uuid(suuid=suuid)
        return api_response.data

    def update_vpn_server(self, vpnserver: dict) -> APIResponse:
        self.logger.debug(f"{self.__class__}: update_vpn_server method with parameter vpnserver: {vpnserver}")
        api_response = self._rrn_vpn_servers_api_service.update_vpnserver(vpnserver=vpnserver)
        return api_response

    def get_random_vpn_server(self, type_id: int = None) -> APIResponse:
        self.logger.debug(
            f"{self.__class__}: get_random_vpn_server method with parameters type_id: {type_id}")
        # TODO some logic to get random VPN server

        if type_id is not None:
            api_response = self._rrn_vpn_servers_api_service.get_vpnservers_by_type(type_id=type_id, pagination=None)
        else:
            api_response = self._rrn_vpn_servers_api_service.get_vpnservers()

        from random import randint
        rs = randint(0, len(api_response.data) - 1)
        server = api_response.data[rs]

        return server['uuid']

    def get_vpn_server_list(self, pagination: ResourcePagination = None) -> List[dict]:
        self.logger.debug(f"{self.__class__}: get_vpn_server_list method with parameters pagination: {pagination}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnservers(pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"get_vpn_server_list_by_type method with parameters type_id: {type_id}, pagination: {pagination}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_list_by_status method with parameters status_id: {status_id}, "
            f"pagination: {pagination}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnservers_by_status(status_id=status_id,
                                                                                  pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_condition_list(self, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_condition_list method with parameters pagination: {pagination}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnservers(pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_condition_list_by_type method with parameters type_id: {type_id}. "
            f"pagination: {pagination}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        self.logger.debug(
            f"{self.__class__}: get_vpn_server_condition_list_by_status method with parameters status_id: {status_id}, "
            f"pagination: {pagination}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnservers_by_status(status_id=status_id,
                                                                                  pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition(self, suuid: str):
        self.logger.debug(f"{self.__class__}: get_vpn_server_condition method with parameters suuid: {suuid}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnserver_by_uuid(suuid=suuid)

        server = api_response.data

        return self._get_vpn_server_condition(server=server)

    def _get_vpn_server_condition(self, server: dict) -> dict:
        self.logger.debug(f"{self.__class__}: _get_vpn_server_condition method with parameters server: {server}")
        server.pop("geo_position_id", None)
        server.pop("type_id", None)
        return server

    def get_vpn_server(self, suuid: str) -> dict:
        self.logger.debug(f"{self.__class__}: get_vpn_server method with parameters suuid: {suuid}")
        api_response = self._rrn_vpn_servers_api_service.get_vpnserver_by_uuid(suuid=suuid)
        return self._get_vpn_server(server=api_response.data)

    def _get_vpn_server(self, server: dict) -> dict:
        self.logger.debug(f"{self.__class__}: _get_vpn_server method with parameters server: {server}")
        geo_position_id = server.get("geo_position_id")

        try:
            self.logger.info(f"get geopos by id: {geo_position_id}")
            api_response = self._rrn_geo_position_api_service.get_geopos_by_id(sid=geo_position_id)
        except APIException as e:
            self.logger.error("Can not retrieve geo position by id")
            self.logger.error(e)
            return server

        geopos = api_response.data

        server['geo'] = geopos

        return server
