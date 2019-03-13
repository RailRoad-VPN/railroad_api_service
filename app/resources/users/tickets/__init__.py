import logging
import sys
from http import HTTPStatus
from typing import List

from flask import Response, request, Config

from app import RailRoadAPIError
from app.policy import UserPolicy
from utils import check_uuid

sys.path.insert(0, '../rest_api_library')
from api import ResourceAPI, APIResourceURL, APIException
from response import make_error_request_response, APIResponse, make_api_response, APIResponseStatus, \
    check_required_api_fields


class UserTicketsAPI(ResourceAPI):
    __version__ = 1

    logger = logging.getLogger(__name__)

    __endpoint_name__ = __qualname__
    __api_url__ = 'users/<string:user_uuid>/tickets'

    _user_policy = None

    @staticmethod
    def get_api_urls(base_url: str) -> List[APIResourceURL]:
        url = f"{base_url}/{UserTicketsAPI.__api_url__}"
        api_urls = [
            APIResourceURL(base_url=url, resource_name='', methods=['GET', 'POST']),
            APIResourceURL(base_url=url, resource_name='<string:suuid_or_number>', methods=['GET']),
        ]
        return api_urls

    def __init__(self, user_policy: UserPolicy, *args) -> None:
        super().__init__(*args)
        self._user_policy = user_policy

    def post(self, user_uuid: str) -> Response:
        super(UserTicketsAPI, self).post(req=request)

        request_json = request.json

        if request_json is None:
            return make_error_request_response(HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.REQUEST_NO_JSON)

        contact_email = request_json.get('contact_email', None)
        description = request_json.get('description', None)
        extra_info = request_json.get('extra_info', None)
        zipfile = request_json.get('zipfile', None)

        req_fields = {
            'contact_email': contact_email,
            'description': description,
        }

        error_fields = check_required_api_fields(req_fields)
        if len(error_fields) > 0:
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=HTTPStatus.BAD_REQUEST,
                                        errors=error_fields)
            resp = make_api_response(data=response_data, http_code=response_data.code)
            return resp

        try:
            api_response = self._user_policy.create_user_ticket(user_uuid=user_uuid, contact_email=contact_email,
                                                                extra_info=extra_info, description=description,
                                                                zipfile=zipfile)

            api_url = self.__api_url__.replace('<string:user_uuid>', user_uuid)

            response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.CREATED)
            resp = make_api_response(data=response_data, http_code=HTTPStatus.CREATED)
            resp.headers['Location'] = f"{self._config['API_BASE_URI']}/{api_url}/{api_response.data['number']}"
            return resp
        except APIException as e:
            self.logger.debug(e.serialize())
            response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
            resp = make_api_response(data=response_data, http_code=e.http_code)
            return resp

    def put(self, suuid: str) -> Response:
        resp = make_error_request_response(http_code=HTTPStatus.METHOD_NOT_ALLOWED)
        return resp

    def get(self, user_uuid: str, suuid_or_number: str = None) -> Response:
        super(UserTicketsAPI, self).get(req=request)

        is_valid = check_uuid(suuid=user_uuid)
        if not is_valid:
            return make_error_request_response(HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)

        if suuid_or_number is None:
            try:
                self.logger.debug("find all user tickets")
                api_response = self._user_policy.get_user_tickets(user_uuid=user_uuid)
            except APIException as e:
                self.logger.debug(e.serialize())
                response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code, errors=e.errors)
                resp = make_api_response(data=response_data, http_code=e.http_code)
                return resp
        else:
            self.logger.debug("find specific ticket. check is uuid or ticket number")
            is_valid = check_uuid(suuid=suuid_or_number)
            if not is_valid:
                self.logger.debug(f"find by ticket number: {suuid_or_number}")
                try:
                    self.logger.debug("try parse ticket_number")
                    ticket_number = int(suuid_or_number)
                except ValueError:
                    return make_error_request_response(HTTPStatus.NOT_FOUND,
                                                       err=RailRoadAPIError.BAD_IDENTITY_ERROR)

                try:
                    self.logger.debug("get user ticket by ticket number")
                    api_response = self._user_policy.get_user_ticket_by_number(user_uuid=user_uuid,
                                                                               ticket_number=ticket_number)
                except APIException as e:
                    self.logger.debug(e.serialize())
                    response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                                errors=e.errors)
                    resp = make_api_response(data=response_data, http_code=e.http_code)
                    return resp
            else:
                try:
                    self.logger.debug(f"get user ticket by uuid: {suuid_or_number}")
                    api_response = self._user_policy.get_user_ticket(user_uuid=user_uuid, ticket_uuid=suuid_or_number)
                except APIException as e:
                    self.logger.debug(e.serialize())
                    response_data = APIResponse(status=APIResponseStatus.failed.status, code=e.http_code,
                                                errors=e.errors)
                    resp = make_api_response(data=response_data, http_code=e.http_code)
                    return resp

        response_data = APIResponse(status=APIResponseStatus.success.status, code=HTTPStatus.OK,
                                    data=api_response.data)
        resp = make_api_response(data=response_data, http_code=HTTPStatus.OK)
        return resp
