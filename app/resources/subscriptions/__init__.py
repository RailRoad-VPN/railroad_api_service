import sys
from http import HTTPStatus
from typing import List

import logging
from flask import request, Response

from app.exception import RailRoadAPIError
from app.service import SubscriptionAPIService

sys.path.insert(0, '../rest_api_library')
from utils import make_api_response, make_error_request_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIResourceURL, APIException


class SubscriptionAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'SubscriptionAPI'
    __api_url__ = 'subscriptions'

    _config = None
    _subscription_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, SubscriptionAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
        ]
        return api_urls

    def __init__(self, subscription_service: SubscriptionAPIService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._subscription_service = subscription_service

    def post(self) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def put(self, uuid: str = None) -> Response:
        resp = make_api_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self) -> Response:
        super(SubscriptionAPI, self).get(req=request)

        lang_code = request.headers.get('Accept-Language', None)

        if lang_code is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.BAD_ACCEPT_LANGUAGE_HEADER)

        try:
            api_response = self._subscription_service.get_subscriptions(lang_code=lang_code)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data,
                                    headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
