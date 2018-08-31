import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request

from app.exception import RailRoadAPIError
from app.policy import VPNServerPolicy

sys.path.insert(0, '../rest_api_library')
from rest import APIException, APIResourceURL
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from utils import check_uuid
from response import make_api_response, make_error_request_response

logger = logging.getLogger(__name__)


class VPNServersAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'VPNServersAPI'
    __api_url__ = 'vpns/servers'

    _vpn_policy = None
    _config = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, VPNServersAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['PUT']),
        ]
        return api_urls

    def __init__(self, vpn_service: VPNServerPolicy, config: dict) -> None:
        self._vpn_policy = vpn_service
        self._config = config

        super().__init__()

    def post(self) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self, suuid: str) -> Response:
        logger.debug('put method')
        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        vpnserver_uuid = request_json.get('uuid', None)

        is_valid_suuid = check_uuid(suuid)
        is_valid_vpnserver_uuid = check_uuid(vpnserver_uuid)
        if not is_valid_suuid or not is_valid_vpnserver_uuid:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR)

        if suuid != vpnserver_uuid:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.VPNSERVER_IDENTIFIER_ERROR)

        try:
            logger.debug('call vpn service')
            api_response = self._vpn_policy.update_vpn_server(vpnserver=request_json)
            logger.debug('response: %s' % api_response.serialize())
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code)
        logger.debug('response data: %s' % response_data.serialize())
        resp = make_api_response(data=response_data, http_code=api_response.code)
        logger.debug('make api response: %s' % resp.__str__())
        return resp

    def get(self, suuid: str = None, type_id: int = None, status_id: int = None) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp