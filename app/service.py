import sys

from app.exception import RailRoadAPIError

sys.path.insert(0, '../rest_api_library')
from rest import RESTService, APIException
from response import APIResponse, APIResponseStatus
from api import ResourcePagination


class UserService(RESTService):
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


class VPNServersService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnservers(self, pagination: ResourcePagination):
        if pagination.is_paginated:
            url = self._build_url_pagination(limit=pagination.limit, offset=pagination.offset)
            api_response = self._get(url=url)
        else:
            api_response = self._get()
        return api_response

    def get_vpnserver_by_uuid(self, suuid: str):
        url = '%s/%s' % (self._url, suuid)
        api_response = self._get(url=url)
        return api_response

    def update_vpnserver(self, vpnserver: dict):
        url = '%s/%s' % (self._url, vpnserver['uuid'])
        api_response = self._put(url=url, data=vpnserver)
        return api_response

    def create_vpnserver(self, vpnserver: dict):
        api_response = self._post(data=vpnserver)
        return api_response


class VPNServersMetaService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_meta(self):
        api_response = self._get()
        return api_response


class VPNTypeService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpntypes(self):
        api_response = self._get()
        return api_response

    def get_vpntype_by_id(self, sid):
        url = '%s/%s' % (self._url, sid)
        api_response = self._get(url=url)
        return api_response


class VPNServerConfigurationService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnserverconfig(self):
        api_response = self._get()
        return api_response

    def get_vpnserverconfig_by_uuid(self, suuid):
        url = '%s/%s' % (self._url, suuid)
        api_response = self._get(url=url)
        return api_response


class VPNServerStatusService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_vpnserverstatuses(self):
        api_response = self._get()
        return api_response

    def get_vpnserverstatuse_by_id(self, sid):
        url = '%s/%s' % (self._url, sid)
        api_response = self._get(url=url)
        return api_response


class GeoPositionService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geoposes(self):
        api_response = self._get()
        return api_response

    def get_geopos_by_id(self, sid):
        url = '%s/%s' % (self._url, sid)
        api_response = self._get(url=url)
        return api_response


class GeoCityService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geocities(self):
        api_response = self._get()
        return api_response

    def get_geocity_by_id(self, sid):
        url = '%s/%s' % (self._url, sid)
        api_response = self._get(url=url)
        return api_response


class GeoCountryService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geocountries(self):
        api_response = self._get()
        return api_response

    def get_geocountry_by_code(self, code):
        url = '%s/%s' % (self._url, code)
        api_response = self._get(url=url)
        return api_response


class GeoStateService(RESTService):
    __version__ = 1

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def get_geostates(self):
        api_response = self._get()
        return api_response

    def get_geostate_by_code(self, code):
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

    def __init__(self, vpnserver_service: VPNServersService, vpntype_service: VPNTypeService,
                 vpnserverconfiguration_service: VPNServerConfigurationService,
                 vpnserverstatus_service: VPNServerStatusService, geoposition_service: GeoPositionService,
                 geocity_service: GeoCityService, geocountry_service: GeoCountryService,
                 geostate_service: GeoStateService):
        self.vpnserver_service = vpnserver_service
        self.vpntype_service = vpntype_service
        self.vpnserverconfiguration_service = vpnserverconfiguration_service
        self.vpnserverstatus_service = vpnserverstatus_service
        self.geoposition_service = geoposition_service
        self.geocity_service = geocity_service
        self.geocountry_service = geocountry_service
        self.geostate_service = geostate_service

    def create_vpn_server(self, vpnserver: dict):
        api_response = self.vpnserver_service.create_vpnserver(vpnserver=vpnserver)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def update_vpn_server(self, vpnserver: dict):
        api_response = self.vpnserver_service.update_vpnserver(vpnserver=vpnserver)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

    def get_vpn_server_list(self, pagination: ResourcePagination):
        api_response = self.vpnserver_service.get_vpnservers(pagination=pagination)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server_condition_list(self, pagination: ResourcePagination):
        api_response = self.vpnserver_service.get_vpnservers(pagination=pagination)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, errors=api_response.errors)
        servers_list = []
        for server in api_response.data:
            server = self._get_vpn_server_condition(server=server)
            servers_list.append(server)

        return servers_list

    def get_vpn_server_condition(self, suuid: str):
        api_response = self.vpnserver_service.get_vpnserver_by_uuid(suuid=suuid)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data

        return self._get_vpn_server_condition(server=server)

    def _get_vpn_server_condition(self, server: dict):
        server.pop("geo_position_id", None)
        server.pop("type_id", None)
        return server

    def get_vpn_server(self, suuid: str):
        api_response = self.vpnserver_service.get_vpnserver_by_uuid(suuid=suuid)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, errors=api_response.errors)

        server = api_response.data

        return self._get_vpn_server(server=server)

    def _get_vpn_server(self, server: dict):
        geo_position_id = server.pop("geo_position_id")

        api_response = self.geoposition_service.get_geopos_by_id(sid=geo_position_id)
        if api_response.status == APIResponseStatus.failed.value:
            return server

        geopos = api_response.data
        geopos.pop("id", None)

        server['geo'] = geopos

        return server
