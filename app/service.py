import sys
from typing import List

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException
from response import APIResponse, APIResponseStatus
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


class UserSubscriptionAPIService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_by_user_uuid(self, user_uuid: str = None) -> APIResponse:
        url = '%s/%s' % (self._url, user_uuid)

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


class VPNService(object):
    __version__ = 1

    vpnserver_service = None
    vpntype_service = None
    vpnserverconfiguration_service = None
    vpnserverstatus_service = None
    geoposition_service = None
    geocity_service = None
    geocountry_service = None
    geostate_service = None

    def __init__(self, vpnserver_service: VPNServersAPIService, vpntype_service: VPNTypeAPIService,
                 vpnserverconfiguration_service: VPNServerConfigurationAPIService,
                 vpnserverstatus_service: VPNServerStatusAPIService, geoposition_service: GeoPositionAPIService,
                 geocity_service: GeoCityAPIService, geocountry_service: GeoCountryAPIService,
                 geostate_service: GeoStateAPIService):
        self.vpnserver_service = vpnserver_service
        self.vpntype_service = vpntype_service
        self.vpnserverconfiguration_service = vpnserverconfiguration_service
        self.vpnserverstatus_service = vpnserverstatus_service
        self.geoposition_service = geoposition_service
        self.geocity_service = geocity_service
        self.geocountry_service = geocountry_service
        self.geostate_service = geostate_service

    def create_vpn_server(self, vpnserver: dict) -> APIResponse:
        api_response = self.vpnserver_service.create_vpnserver(vpnserver=vpnserver)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        return api_response

    def update_vpn_server(self, vpnserver: dict) -> APIResponse:
        api_response = self.vpnserver_service.update_vpnserver(vpnserver=vpnserver)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors, data=api_response.data)
        return api_response

    def get_random_vpn_server(self, type_id: int = None, status_id: int = None) -> str:
        # TODO some logic to get random VPN server

        pagination = ResourcePagination(limit=1, offset=0)

        if type_id is not None:
            api_response = self.vpnserver_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)
        elif status_id is not None:
            api_response = self.vpnserver_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)
        else:
            api_response = self.vpnserver_service.get_vpnservers(pagination=pagination)

        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data[0]

        return server['uuid']

    def get_vpn_server_list(self, pagination: ResourcePagination = None) -> List[dict]:
        api_response = self.vpnserver_service.get_vpnservers(pagination=pagination)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_condition_list(self, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_service.get_vpnservers(pagination=pagination)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_type(self, type_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_service.get_vpnservers_by_type(type_id=type_id, pagination=pagination)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition_list_by_status(self, status_id: int, pagination: ResourcePagination) -> List[dict]:
        api_response = self.vpnserver_service.get_vpnservers_by_status(status_id=status_id, pagination=pagination)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition(self, suuid: str):
        api_response = self.vpnserver_service.get_vpnserver_by_uuid(suuid=suuid)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data

        return self._get_vpn_server_condition(server=server)

    def _get_vpn_server_condition(self, server: dict) -> dict:
        server.pop("geo_position_id", None)
        server.pop("type_id", None)
        return server

    def get_vpn_server(self, suuid: str) -> dict:
        api_response = self.vpnserver_service.get_vpnserver_by_uuid(suuid=suuid)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data

        return self._get_vpn_server(server=server)

    def get_vpn_server_configuration(self, server_uuid: str, user_uuid: str = None) -> dict:
        api_response = self.vpnserverconfiguration_service.get_vpnserverconfig(server_uuid=server_uuid,
                                                                               user_uuid=user_uuid)
        if api_response.status == APIResponseStatus.failed.status:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        return api_response.data

    def _get_vpn_server(self, server: dict) -> dict:
        geo_position_id = server.pop("geo_position_id")

        api_response = self.geoposition_service.get_geopos_by_id(sid=geo_position_id)
        if api_response.status == APIResponseStatus.failed.status:
            return server

        geopos = api_response.data
        geopos.pop("id", None)

        server['geo'] = geopos

        return server
