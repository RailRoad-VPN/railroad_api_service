import sys
from http import HTTPStatus
from typing import List

import logging
from flask import request, Response

from app.exception import RailRoadAPIError
from app.service import PaymentAPIService

sys.path.insert(0, '../rest_api_library')
from utils import check_uuid, make_api_response
from api import ResourceAPI
from response import APIResponseStatus, APIResponse
from rest import APIException, APIResourceURL


class PaymentAPI(ResourceAPI):
    __version__ = 1

    __endpoint_name__ = 'PaymentAPI'
    __api_url__ = 'orders/<string:uuid>/payments'

    _config = None
    _payment_service = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = "%s/%s" % (base_url, PaymentAPI.__api_url__)
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET']),
            APIResourceURL(base_url=url, resource_name='<string:suuid>', methods=['GET', 'POST']),
        ]
        return api_urls

    def __init__(self, payment_service: PaymentAPIService, config: dict) -> None:
        super().__init__()
        self._config = config
        self._payment_service = payment_service

    def post(self) -> Response:
        request_json = request.json

        payment_email = request_json['email']

        if api_response.code == HTTPStatus.OK:
            # payment exist
            code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=code, headers=api_response.headers,
                                        error=RailRoadAPIError.PAYMENT_EMAIL_BUSY.message,
                                        error_code=RailRoadAPIError.PAYMENT_EMAIL_BUSY.code)
            resp = make_api_response(data=response_data, http_code=code)
            return resp

        try:
            api_response = self._payment_service.create_payment(payment_json=request_json)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code == HTTPStatus.CREATED:
            payment_uuid = api_response.data['uuid']
            resp = make_api_response(http_code=HTTPStatus.CREATED)
            resp.headers['Location'] = '%s/%s/uuid/%s' % (self._config['API_BASE_URI'], self.__api_url__, payment_uuid)
        else:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=api_response.code,
                                        errors=api_response.errors, headers=api_response.headers)
            resp = make_api_response(data=response_data, http_code=api_response.code)
        return resp

    def put(self, uuid: str = None) -> Response:
        is_valid = check_uuid(suuid=uuid)
        if not is_valid:
            code = HTTPStatus.NOT_FOUND
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=code,
                                        error=RailRoadAPIError.BAD_PAYMENT_IDENTITY.message,
                                        error_code=RailRoadAPIError.BAD_PAYMENT_IDENTITY)

            resp = make_api_response(data=response_data, http_code=code)
            return resp

        request_json = request.json

        try:
            api_response = self._payment_service.get_payment(suuid=uuid)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if not api_response.is_ok:
            # payment does not exist
            code = HTTPStatus.BAD_REQUEST
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=code,
                                        error=RailRoadAPIError.PAYMENT_NOT_EXIST.message,
                                        error_code=RailRoadAPIError.PAYMENT_NOT_EXIST)
            resp = make_api_response(data=response_data, http_code=code)
            return resp

        try:
            api_response = self._payment_service.update_payment(payment_json=request_json)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if api_response.code in [HTTPStatus.OK, HTTPStatus.NO_CONTENT]:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        headers=api_response.headers)
            # 200 OK - means some content in body
            if api_response.code == HTTPStatus.OK:
                response_data.data = api_response.data
        else:
            response_data = APIResponse(status=api_response.status, code=api_response.code,
                                        error=api_response.error, error_code=api_response.error_code,
                                        headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=api_response.code)
        return resp

    def get(self, suuid: str = None, email: str = None) -> Response:
        super(PaymentAPI, self).get(req=request)
        if suuid is not None:
            is_valid = check_uuid(suuid=suuid)
            if not is_valid:
                code = HTTPStatus.NOT_FOUND
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=code,
                                            error=RailRoadAPIError.BAD_PAYMENT_IDENTITY.message,
                                            error_code=RailRoadAPIError.BAD_PAYMENT_IDENTITY.code)

                resp = make_api_response(data=response_data, http_code=code)
                return resp

        if suuid is None and email is None:
            # find all payments - no parameters set
            code = HTTPStatus.METHOD_NOT_ALLOWED
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=code,
                                        error=RailRoadAPIError.PRIVATE_METHOD.message,
                                        error_code=RailRoadAPIError.PRIVATE_METHOD.code, limit=self.pagination.limit,
                                        offset=self.pagination.offset)

            resp = make_api_response(data=response_data, http_code=code)
            return resp

        # uuid or email is not None, let's get payment
        try:
            api_response = self._payment_service.get_payment(suuid=suuid, email=email)
        except APIException as e:
            logging.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

        if not api_response.is_ok:
            response_data = APIResponse(status=api_response.status, code=HTTPStatus.BAD_REQUEST,
                                        headers=api_response.headers, errors=api_response.errors)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.BAD_REQUEST)
            return resp

        response_data = APIResponse(status=api_response.status, code=api_response.code, data=api_response.data,
                                    headers=api_response.headers)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
