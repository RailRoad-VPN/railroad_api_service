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

    def get_vpn_server_list(self, pagination):
        api_response = self.vpnserver_service.get_vpnservers(pagination=pagination)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, code=RailRoadAPIError.UNKNOWN_ERROR_CODE.value,
                               message=RailRoadAPIError.UNKNOWN_ERROR_CODE.phrase)
        servers_list = []
        for server in api_response.data:
            server_repr = self._get_vpn_server(server=server)
            servers_list.append(server_repr)

        return servers_list

    def get_vpn_server(self, suuid: str):
        api_response = self.vpnserver_service.get_vpnserver_by_uuid(suuid=suuid)
        if api_response.status == APIResponseStatus.failed.value:
            raise APIException(http_code=api_response.code, code=RailRoadAPIError.UNKNOWN_ERROR_CODE.value,
                               message=RailRoadAPIError.UNKNOWN_ERROR_CODE.phrase)

        server = api_response.data

        return self._get_vpn_server(server=server)

    def _get_vpn_server(self, server: dict):
        uuid = server['uuid']
        version = server['version']
        state_version = server['state_version']
        bandwidth = server['bandwidth']
        load = server['load']

        vpntype_id = server['type_id']
        vpnstatus_id = server['status_id']
        geo_position_id = server['geo_position_id']

        server_repr = {
            'uuid': uuid,
            'version': version,
            'state_version': state_version,
            'load': load,
            'bandwidth': bandwidth,
            'geo': {
                'id': geo_position_id,
            }
        }

        api_response = self.vpntype_service.get_vpntype_by_id(sid=vpntype_id)
        if api_response.status == APIResponseStatus.success.value:
            vpntype = api_response.data
            server_repr['type'] = vpntype,

        api_response = self.vpnserverstatus_service.get_vpnserverstatuse_by_id(sid=vpnstatus_id)
        if api_response.status == APIResponseStatus.success.value:
            vpnstatus = api_response.data
            server_repr['status'] = vpnstatus,

        api_response = self.geoposition_service.get_geopos_by_id(sid=geo_position_id)
        if api_response.status == APIResponseStatus.failed.value:
            return server_repr

        geopos = api_response.data
        city_id = geopos['city_id']
        country_code = geopos['country_code']
        state_code = geopos['state_code']

        if city_id is not None:
            api_response = self.geocity_service.get_geocity_by_id(sid=city_id)
            city = api_response.data
            server_repr['geo']['city'] = city

        if country_code is not None:
            api_response = self.geocountry_service.get_geocountry_by_code(code=country_code)
            country = api_response.data
            server_repr['geo']['country'] = country

        if state_code is not None:
            api_response = self.geostate_service.get_geostate_by_code(code=state_code)
            state = api_response.data
            server_repr['geo']['state'] = state

        return server_repr
