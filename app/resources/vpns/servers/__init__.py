import json
from enum import Enum
from http import HTTPStatus

from flask import Response, request

from app import *
from app.exception import RailRoadAPIError

sys.path.insert(0, '../rest_api_library')
from rest import APIException
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import check_uuid, make_api_response


class VPNServersRepr(Enum):
    list = 'list'
    map = 'map'


class VPNServersAPI(ResourceAPI):
    __version__ = 1

    __api_url__ = 'vpn/servers'

    _config = None

    vpnserver_service = None
    vpntype_service = None
    vpnserverconfiguration_service = None
    vpnserverstatus_service = None
    geoposition_service = None
    geocity_service = None
    geocountry_service = None
    geostate_service = None

    def __init__(self, vpnserver_service: VPNServerService, vpntype_service: VPNTypeService,
                 vpnserverconfiguration_service: VPNServerConfigurationService,
                 vpnserverstatus_service: VPNServerStatusService, geoposition_service: GeoPositionService,
                 geocity_service: GeoCityService, geocountry_service: GeoCountryService,
                 geostate_service: GeoStateService, config: dict) -> None:
        self.vpnserver_service = vpnserver_service
        self.vpntype_service = vpntype_service
        self.vpnserverconfiguration_service = vpnserverconfiguration_service
        self.vpnserverstatus_service = vpnserverstatus_service
        self.geoposition_service = geoposition_service
        self.geocity_service = geocity_service
        self.geocountry_service = geocountry_service
        self.geostate_service = geostate_service

        self._config = config

        super().__init__()

    def post(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self) -> Response:
        resp = make_api_response('', HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, suuid: str = None) -> Response:
        super(VPNServersAPI, self).get(req=request)
        if suuid is None:
            # list of all servers
            try:
                api_response = self.vpnserver_service.get_vpnservers(pagination=self.pagination)
            except APIException as e:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=e.http_code,
                                            error=e.message, error_code=e.code)
                resp = make_api_response(json.dumps(response_data.serialize()), e.http_code)
                return resp

            if api_response.status == APIResponseStatus.failed.value:
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=HTTPStatus.BAD_REQUEST.phrase,
                                            headers=api_response.headers, errors=api_response.errors)
                resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.BAD_REQUEST)
                return resp

            servers_repr_list = []
            for server in api_response.data:
                uuid = server['uuid']
                version = server['version']
                state_version = server['state_version']
                bandwidth = server['bandwidth']
                load = server['load']

                vpntype_id = server['type_id']
                vpnstatus_id = server['status_id']
                geo_position_id = server['geo_position_id']

                api_response = self.vpntype_service.get_vpntype_by_id(sid=vpntype_id)
                vpntype = api_response.data

                api_response = self.vpnserverstatus_service.get_vpnserverstatuse_by_id(sid=vpnstatus_id)
                vpnstatus = api_response.data

                api_response = self.geoposition_service.get_geopos_by_id(sid=geo_position_id)
                geopos = api_response.data
                city_id = geopos['city_id']
                country_code = geopos['country_code']
                state_code = geopos['state_code']

                server_repr = {
                    'uuid': uuid,
                    'version': version,
                    'state_version': state_version,
                    'status': vpnstatus,
                    'type': vpntype,
                    'load': load,
                    'bandwidth': bandwidth,
                    'geo': {
                        'id': geo_position_id,
                    }
                }

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

                servers_repr_list.append(server_repr)

            response_data = APIResponse(status=api_response.status, code=api_response.code, data=servers_repr_list,
                                        headers=api_response.headers, limit=self.pagination.limit,
                                        offset=self.pagination.offset)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
            return resp

        elif suuid is not None:
            # specific server by uuid TODO doit
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.value, code=code,
                                            error=RailRoadAPIError.BAD_USER_IDENTITY.phrase,
                                            error_code=RailRoadAPIError.BAD_USER_IDENTITY)
                resp = make_api_response(json.dumps(response_data.serialize()), code)
                return resp

            response_data = APIResponse(status=APIResponseStatus.success.value, data=data)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.OK)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.value)
            resp = make_api_response(json.dumps(response_data.serialize()), HTTPStatus.BAD_REQUEST)
        return resp
