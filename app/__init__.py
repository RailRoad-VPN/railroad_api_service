import os
from http import HTTPStatus

from flask import Flask, request

from app.exception import RailRoadAPIError
from app.policy import *
from app.resources.payments import PaymentsAPI
from app.resources.services import RRNServicesAPI
from app.resources.users import UsersAPI
from app.resources.users.devices import UsersDevicesAPI
from app.resources.users.orders import UsersOrdersAPI
from app.resources.users.orders.payments import UsersOrdersPaymentsAPI
from app.resources.users.servers import UsersServersAPI
from app.resources.users.servers.conditions import UsersServersConditionsAPI
from app.resources.users.servers.configurations import UsersServersConfigurationsAPI
from app.resources.users.servers.connections import UsersServersConnectionsAPI
from app.resources.users.rrnservices import UsersServicesAPI
from app.resources.vpns.device_platforms import VPNSDevicePlatformsAPI
from app.resources.vpns.servers import VPNServersAPI
from app.resources.vpns.servers.connections import VPNSServersConnectionsAPI
from app.resources.vpns.servers.meta import VPNSServersMetaAPI
from app.resources.vpns.types import VPNSTypesAPI
from app.service import *

sys.path.insert(1, '../rest_api_library')
from api import register_api
from response import make_error_request_response

logging.basicConfig(
    level=logging.DEBUG,
    format='RAILROAD_API_SERVICE: %(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Load config based on env variable
ENVIRONMENT_CONFIG = os.environ.get("ENVIRONMENT_CONFIG", default='DevelopmentConfig')
logger.info("Got ENVIRONMENT_CONFIG variable: %s" % ENVIRONMENT_CONFIG)
config_name = "%s.%s" % ('config', ENVIRONMENT_CONFIG)
logger.info("Config name: %s" % config_name)
app.config.from_object(config_name)

app_config = app.config
api_base_uri = app_config['API_BASE_URI']

# SERVICES
rrn_vpn_server_api_service = VPNServersAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                  resource_name=app_config['VPNC_SERVICE_VPNSERVER_RESOURCE_NAME'])

rrn_vpn_servers_meta_api_service = VPNServersMetaAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                            resource_name=app_config[
                                                                'VPNC_SERVICE_VPNSERVERSMETA_RESOURCE_NAME'])

rrn_vpn_type_api_service = VPNTypeAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                             resource_name=app_config['VPNC_SERVICE_VPNTYPE_RESOURCE_NAME'])

rrn_vpn_server_connections_api_service = VPNServerConnectionsAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                                        resource_name=app_config[
                                                                            'VPNC_SERVICE_VPNSERVERCONNECTIONS_RESOURCE_NAME'])
rrn_vpn_server_status_api_service = VPNServerStatusAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                              resource_name=app_config[
                                                                  'VPNC_SERVICE_VPNSERVERSTATUS_RESOURCE_NAME'])

rrn_vpn_mgmt_users_api_service = VPNMGMTUsersAPIService(api_url=app_config['VPNMGMT_SERVICE_URL'],
                                                        auth=app_config['VPNMGMT_BASIC_AUTH'],
                                                        resource_name=app_config['VPNMGMT_USERS_RESOURCE_NAME'])

rrn_vpn_mgmt_server_conns_api_service = VPNMGMTServerConnectionsAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                                           auth=app_config['VPNMGMT_BASIC_AUTH'],
                                                                           resource_name=app_config[
                                                                               'VPNMGMT_SERVER_CONNECTIONS_RESOURCE_NAME'])

rrn_vpn_device_platforms_api_service = VPNDevicePlatformsAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                                    resource_name=app_config[
                                                                        'VPNC_SERVICE_DEVICE_PLATFORMS_RESOURCE_NAME'])

rrn_geo_position_api_service = GeoPositionAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                     resource_name=app_config['VPNC_SERVICE_GEOPOSITION_RESOURCE_NAME'])

rrn_geo_city_api_service = GeoCityAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                             resource_name=app_config['VPNC_SERVICE_GEOCITY_RESOURCE_NAME'])

rrn_geo_country_api_service = GeoCountryAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                   resource_name=app_config['VPNC_SERVICE_GEOCOUNTRY_RESOURCE_NAME'])

rrn_geo_state_api_service = GeoStateAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                               resource_name=app_config['VPNC_SERVICE_GEOSTATE_RESOURCE_NAME'])

rrn_user_api_service = UserAPIService(api_url=app_config['AUTH_SERVICE_URL'],
                                      resource_name=app_config['AUTH_SERVICE_USERS_RESOURCE_NAME'])

rrn_user_rrnservice_api_service = UserRRNServiceAPIService(api_url=app_config['BILLING_SERVICE_URL'],
                                                           resource_name=app_config[
                                                               'BILLING_SERVICE_USER_SUBSCRIPTION_RESOURCE_NAME'])

rrn_user_device_api_service = UserDeviceAPIService(api_url=app_config['AUTH_SERVICE_URL'],
                                                   resource_name=app_config['AUTH_SERVICE_USER_DEVICES_RESOURCE_NAME'])

rrn_vpn_server_configurations_api_service = UsersVPNServersConfigurationsAPIService(
    api_url=app_config['AUTH_SERVICE_URL'],
    resource_name=app_config['AUTH_SERVICE_USER_VPN_SERVER_CONFIGURATIONS_RESOURCE_NAME'])

rrn_rrnservices_api_service = RRNServiceAPIService(api_url=app_config['BILLING_SERVICE_URL'],
                                                   resource_name=app_config[
                                                       'BILLING_SERVICE_SUBSCRIPTIONS_RESOURCE_NAME'])

rrn_order_api_service = OrderAPIService(api_url=app_config['BILLING_SERVICE_URL'],
                                        resource_name=app_config['BILLING_SERVICE_ORDERS_RESOURCE_NAME'])

user_policy = UserPolicy(rrn_user_rrnservice_api_service=rrn_user_rrnservice_api_service,
                         rrn_order_api_service=rrn_order_api_service,
                         rrn_user_api_service=rrn_user_api_service,
                         rrn_user_device_api_service=rrn_user_device_api_service,
                         rrn_vpn_servers_connections_api_service=rrn_vpn_server_connections_api_service,
                         rrn_vpn_mgmt_users_api_service=rrn_vpn_mgmt_users_api_service,
                         rrn_vpn_server_configurations_api_service=rrn_vpn_server_configurations_api_service)

vpn_policy = VPNServerPolicy(rrn_vpn_servers_api_service=rrn_vpn_server_api_service,
                             rrn_vpn_types_api_service=rrn_vpn_type_api_service,
                             rrn_vpn_server_configurations_api_service=rrn_vpn_server_configurations_api_service,
                             rrn_vpn_server_statuses_api_service=rrn_vpn_server_status_api_service,
                             rrn_geo_position_api_service=rrn_geo_position_api_service,
                             rrn_geo_city_api_service=rrn_geo_city_api_service,
                             rrn_geo_country_api_service=rrn_geo_country_api_service,
                             rrn_geo_state_api_service=rrn_geo_state_api_service)

apis = [
    {'cls': UsersAPI, 'args': [user_policy, app_config, True]},
    {'cls': UsersOrdersAPI, 'args': [rrn_order_api_service, app_config, True]},
    {'cls': UsersOrdersPaymentsAPI, 'args': [rrn_order_api_service, app_config, True]},
    {'cls': UsersServicesAPI, 'args': [user_policy, app_config, True]},
    {'cls': UsersDevicesAPI, 'args': [user_policy, app_config, True]},
    {'cls': PaymentsAPI,
     'args': [rrn_order_api_service, rrn_user_rrnservice_api_service, rrn_vpn_mgmt_users_api_service, user_policy,
              rrn_vpn_server_configurations_api_service, app_config]},
    {'cls': RRNServicesAPI, 'args': [rrn_rrnservices_api_service, app_config, True]},
    {'cls': VPNServersAPI, 'args': [vpn_policy, app_config, True]},
    {'cls': VPNSServersMetaAPI, 'args': [rrn_vpn_servers_meta_api_service, app_config]},
    {'cls': UsersServersConditionsAPI, 'args': [vpn_policy, app_config, True]},
    {'cls': UsersServersAPI, 'args': [vpn_policy, app_config, True]},
    {'cls': UsersServersConfigurationsAPI,
     'args': [rrn_vpn_server_configurations_api_service, rrn_vpn_server_api_service, user_policy, app_config, True]},
    {'cls': UsersServersConnectionsAPI, 'args': [rrn_vpn_server_connections_api_service, app_config, True]},
    {'cls': VPNSDevicePlatformsAPI, 'args': [rrn_vpn_device_platforms_api_service, app_config, True]},
    {'cls': VPNSTypesAPI, 'args': [rrn_vpn_type_api_service, app_config, True]},
    {'cls': VPNSServersConnectionsAPI, 'args': [rrn_vpn_server_connections_api_service, user_policy, app_config, True]},
]

register_api(app, api_base_uri, apis)


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
           request.accept_mimetypes['text/html']


@app.errorhandler(400)
def not_found_error(error):
    return make_error_request_response(http_code=HTTPStatus.BAD_REQUEST, err=RailRoadAPIError.API_DOES_NOT_EXIST)


@app.errorhandler(404)
def not_found_error(error):
    return make_error_request_response(http_code=HTTPStatus.NOT_FOUND, err=RailRoadAPIError.BAD_IDENTITY_ERROR)


@app.errorhandler(500)
def internal_error(error):
    return make_error_request_response(http_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                                       err=RailRoadAPIError.UNKNOWN_ERROR_CODE)


@app.errorhandler(APIException)
def api_exception_error(error):
    return make_error_request_response(http_code=error.http_code)
