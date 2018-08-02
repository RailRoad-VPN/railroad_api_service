from typing import List

from app.service import *

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from api import ResourcePagination

logger = logging.getLogger(__name__)


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

    def create_user_sub(self, user_uuid: str, subscription_id: str, order_uuid: str) -> APIResponse:
        logger.debug(f"create_user_sub method with parameter user_uuid: {user_uuid}, "
                     f"subscription_id: {subscription_id}, "
                     f"order_uuid: {order_uuid}")
        api_response = self._user_sub_api_service.create(user_uuid=user_uuid, subscription_id=subscription_id,
                                                         order_uuid=order_uuid)
        location = api_response.headers.get('Location', None)
        if location is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self._user_sub_api_service.get_user_sub_by_uuid(user_uuid=user_uuid, suuid=suuid)
        return api_response

    def update_user_sub(self, user_subscription: dict):
        logger.debug(f"update_user_sub method with parameter user_subscription: {user_subscription}")
        self._user_sub_api_service.update(user_subscription=user_subscription)

    def get_user_sub_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        api_response = self._user_sub_api_service.get_user_sub_by_uuid(user_uuid=user_uuid, suuid=suuid)
        enriched_user_sub = self.__enrich_user_sub(user_sub=api_response.data)
        api_response.data = enriched_user_sub
        return api_response

    def get_user_subs(self, user_uuid: str) -> APIResponse:
        logger.debug(f"get_user_subs method with parameter user_uuid: {user_uuid}")
        logger.debug(f"Get user subscriptions by user uuid")
        api_response = self._user_sub_api_service.get_user_subs_by_user_uuid(user_uuid=user_uuid)
        enriched_user_subs = []
        for user_sub in api_response.data:
            enriched_user_sub = self.__enrich_user_sub(user_sub=user_sub)
            enriched_user_subs.append(enriched_user_sub)
        api_response.data = enriched_user_subs
        return api_response

    def __enrich_user_sub(self, user_sub: dict) -> dict:
        logger.debug(f"__enrich_user_sub method with parameters user_sub: {user_sub}")
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

    def get_user(self, suuid: str = None, email: str = None, pin_code: str = None) -> APIResponse:
        logger.debug(f"get_user method with parameters suuid : {suuid}, email : {email}, pin_code: {pin_code}")
        api_response = self._user_api_service.get_user(suuid=suuid, email=email, pin_code=pin_code)
        return api_response

    def create_user(self, email: str, password: str, is_expired: bool = False, is_locked: bool = False,
                    is_password_expired: bool = False, enabled: bool = False, pin_code: str = None,
                    pin_code_expire_date: datetime = None) -> APIResponse:
        logger.debug(f"create_user method with parameters email: {email}, password: {password}, "
                     f"is_expired: {is_expired}, is_locked: {is_locked}, is_password_expired: {is_password_expired}, "
                     f"enabled: {enabled}, pin_code: {pin_code}, pin_code_expire_date: {pin_code_expire_date}")
        api_response = self._user_api_service.create_user(email=email, password=password, is_expired=is_expired,
                                                          is_locked=is_locked, is_password_expired=is_password_expired,
                                                          enabled=enabled, pin_code=pin_code,
                                                          pin_code_expire_date=pin_code_expire_date)
        location = api_response.headers.get('Location', None)
        if location is None:
            logger.error(f"no Location header. raise APIException")
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self._user_api_service.get_user(suuid=suuid)
        return api_response

    def update_user(self, user_dict: dict):
        logger.debug(f"update_user method with parameter user_dict: {user_dict}")
        self._user_api_service.update_user(user_dict=user_dict)

    def create_user_device(self, user_uuid: str, device_id: str, device_token: str = None, location: str = None,
                           is_active: bool = False) -> APIResponse:
        logger.debug(f"create_user_device method with parameters user_uuid: {user_uuid}, device_id: {device_id}, "
                     f"device_token: {device_token}, location: {location}, is_active: {is_active}")
        api_response = self._user_device_api_service.create(user_uuid=user_uuid, device_id=device_id,
                                                            device_token=device_token, location=location,
                                                            is_active=is_active)
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
        logger.debug(f"update_user_device method with parameters user_device: {user_device}")
        self._user_device_api_service.update(user_device=user_device)

    def get_user_device_by_uuid(self, user_uuid: str, suuid: str) -> APIResponse:
        logger.debug(f"get_user_device_by_uuid method with parameters user_uuid: {user_uuid}, suuid: {suuid}")
        api_response = self._user_device_api_service.get_user_device_by_uuid(user_uuid=user_uuid, suuid=suuid)
        return api_response

    def get_user_devices(self, user_uuid: str) -> APIResponse:
        logger.debug(f"get_user_devices method with parameters user_uuid: {user_uuid}")
        api_response = self._user_device_api_service.get_user_devices(user_uuid=user_uuid)
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
        logger.debug(f"create_vpn_server method with parameters vpnserver: {vpnserver}")
        api_response = self.vpnserver_api_service.create_vpnserver(vpnserver=vpnserver)

        location = api_response.headers.get('Location', None)
        if location is None:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        suuid = location.split('/')[-1]
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)
        return api_response.data

    def update_vpn_server(self, vpnserver: dict):
        logger.debug(f"update_vpn_server method with parameter vpnserver: {vpnserver}")
        self.vpnserver_api_service.update_vpnserver(vpnserver=vpnserver)

    def get_random_vpn_server(self, type_id: int = None, status_id: int = None) -> APIResponse:
        logger.debug(f"get_random_vpn_server method with parameters type_id: {type_id}, status_id: {status_id}")
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
        logger.debug(f"get_vpn_server_list method with parameters pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        logger.debug(f"get_vpn_server_list_by_type method with parameters type_id: {type_id}, pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        logger.debug(f"get_vpn_server_list_by_status method with parameters status_id: {status_id}, "
                     f"pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_condition_list(self, pagination: ResourcePagination) -> List[dict]:
        logger.debug(f"get_vpn_server_condition_list method with parameters pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers(pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        logger.debug(f"get_vpn_server_condition_list_by_type method with parameters type_id: {type_id}. "
                     f"pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        logger.debug(f"get_vpn_server_condition_list_by_status method with parameters status_id: {status_id}, "
                     f"pagination: {pagination}")
        api_response = self.vpnserver_api_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)

        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition(self, suuid: str):
        logger.debug(f"get_vpn_server_condition method with parameters suuid: {suuid}")
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)

        server = api_response.data

        return self._get_vpn_server_condition(server=server)

    def _get_vpn_server_condition(self, server: dict) -> dict:
        logger.debug(f"_get_vpn_server_condition method with parameters server: {server}")
        server.pop("geo_position_id", None)
        server.pop("type_id", None)
        return server

    def get_vpn_server(self, suuid: str) -> dict:
        logger.debug(f"get_vpn_server method with parameters suuid: {suuid}")
        api_response = self.vpnserver_api_service.get_vpnserver_by_uuid(suuid=suuid)
        return self._get_vpn_server(server=api_response.data)

    def get_vpn_server_configuration(self, server_uuid: str, user_uuid: str = None) -> dict:
        logger.debug(f"get_vpn_server_configuration method with parameters get_vpn_server_configuration: {get_vpn_server_configuration}")
        api_response = self.vpnserverconf_api_service.get_vpnserverconfig(server_uuid=server_uuid, user_uuid=user_uuid)
        return api_response.data

    def _get_vpn_server(self, server: dict) -> dict:
        logger.debug(f"_get_vpn_server method with parameters server: {server}")
        geo_position_id = server.pop("geo_position_id")

        try:
            logger.info(f"get geopos by id: {geo_position_id}")
            api_response = self.geoposition_api_service.get_geopos_by_id(sid=geo_position_id)
        except APIException as e:
            logger.error("Can not retrieve geo position by id")
            logger.error(e)
            return server

        geopos = api_response.data
        geopos.pop("id", None)

        server['geo'] = geopos

        return server
