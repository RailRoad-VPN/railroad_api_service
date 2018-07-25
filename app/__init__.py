import logging
import os
from http import HTTPStatus

from flask import Flask, request

from app.policy import *
from app.service import *
from app.resources.subscriptions import SubscriptionAPI
from app.resources.users import UserAPI
from app.resources.users.orders import OrderAPI
from app.resources.users.subscriptions import UserSubscriptionAPI
from app.resources.vpns.servers import VPNServersAPI
from app.resources.vpns.servers.conditions import VPNServerConditionsAPI
from app.resources.vpns.servers.configurations import VPNServersConfigurationsAPI
from app.resources.vpns.servers.meta import VPNServersMetaAPI
from app.resources.users.devices import UserDeviceAPI
from app.resources.payments import PaymentAPI

sys.path.insert(1, '../rest_api_library')
from api import register_api
from response import make_error_request_response

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load config based on env variable
ENVIRONMENT_CONFIG = os.environ.get("ENVIRONMENT_CONFIG", default='DevelopmentConfig')
logging.info("Got ENVIRONMENT_CONFIG variable: %s" % ENVIRONMENT_CONFIG)
config_name = "%s.%s" % ('config', ENVIRONMENT_CONFIG)
logging.info("Config name: %s" % config_name)
app.config.from_object(config_name)

app_config = app.config
api_base_uri = app_config['API_BASE_URI']

# SERVICES
vpnserver_api_service = VPNServersAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                             resource_name=app_config['VPNC_SERVICE_VPNSERVER_RESOURCE_NAME'])

vpnserversmeta_api_service = VPNServersMetaAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                      resource_name=app_config[
                                                          'VPNC_SERVICE_VPNSERVERSMETA_RESOURCE_NAME'])

vpntype_api_service = VPNTypeAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                        resource_name=app_config['VPNC_SERVICE_VPNTYPE_RESOURCE_NAME'])

vpnserverconf_api_service = VPNServerConfigurationAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                             resource_name=app_config[
                                                                 'VPNC_SERVICE_VPNSERVERCONFIGURATION_RESOURCE_NAME'])
vpnserverstatus_api_service = VPNServerStatusAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                        resource_name=app_config[
                                                            'VPNC_SERVICE_VPNSERVERSTATUS_RESOURCE_NAME'])

geoposition_api_service = GeoPositionAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                                resource_name=app_config['VPNC_SERVICE_GEOPOSITION_RESOURCE_NAME'])

geocity_api_service = GeoCityAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                        resource_name=app_config['VPNC_SERVICE_GEOCITY_RESOURCE_NAME'])

geocountry_api_service = GeoCountryAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                              resource_name=app_config['VPNC_SERVICE_GEOCOUNTRY_RESOURCE_NAME'])

geostate_api_service = GeoStateAPIService(api_url=app_config['VPNC_SERVICE_URL'],
                                          resource_name=app_config['VPNC_SERVICE_GEOSTATE_RESOURCE_NAME'])

user_api_service = UserAPIService(api_url=app_config['AUTH_SERVICE_URL'],
                                  resource_name=app_config['AUTH_SERVICE_USERS_RESOURCE_NAME'])

user_sub_api_service = UserSubscriptionAPIService(api_url=app_config['BILLING_SERVICE_URL'],
                                                  resource_name=app_config[
                                                      'BILLING_SERVICE_USER_SUBSCRIPTION_RESOURCE_NAME'])

user_device_api_service = UserDeviceAPIService(api_url=app_config['AUTH_SERVICE_URL'],
                                               resource_name=app_config['AUTH_SERVICE_USER_DEVICES_RESOURCE_NAME'])

subscription_api_service = SubscriptionAPIService(api_url=app_config['BILLING_SERVICE_URL'],
                                                  resource_name=app_config[
                                                      'BILLING_SERVICE_SUBSCRIPTIONS_RESOURCE_NAME'])

order_api_service = OrderAPIService(api_url=app_config['BILLING_SERVICE_URL'],
                                    resource_name=app_config['BILLING_SERVICE_ORDERS_RESOURCE_NAME'])

payment_api_service = PaymentAPIService(api_url=app_config['BILLING_SERVICE_URL'],
                                        resource_name=app_config['BILLING_SERVICE_PAYMENTS_RESOURCE_NAME'])

user_policy = UserPolicy(user_sub_api_service=user_sub_api_service, order_api_service=order_api_service,
                         user_api_service=user_api_service, user_device_api_service=user_device_api_service)

vpn_policy = VPNServerPolicy(vpnserver_service=vpnserver_api_service, vpntype_service=vpntype_api_service,
                             vpnserverconfiguration_service=vpnserverconf_api_service,
                             vpnserverstatus_service=vpnserverstatus_api_service,
                             geoposition_service=geoposition_api_service, geocity_service=geocity_api_service,
                             geocountry_service=geocountry_api_service, geostate_service=geostate_api_service)

apis = [
    {'cls': UserAPI, 'args': [user_policy, app_config]},
    {'cls': OrderAPI, 'args': [order_api_service, app_config]},
    {'cls': UserSubscriptionAPI, 'args': [user_policy, app_config]},
    {'cls': UserDeviceAPI, 'args': [user_policy, app_config]},
    {'cls': PaymentAPI, 'args': [payment_api_service, order_api_service, app_config]},
    {'cls': SubscriptionAPI, 'args': [subscription_api_service, app_config]},
    {'cls': VPNServersMetaAPI, 'args': [vpnserversmeta_api_service, app_config]},
    {'cls': VPNServerConditionsAPI, 'args': [vpn_policy, app_config]},
    {'cls': VPNServersAPI, 'args': [vpn_policy, app_config]},
    {'cls': VPNServersConfigurationsAPI, 'args': [vpnserverconf_api_service, app_config]},
]

register_api(app, api_base_uri, apis)


def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
           request.accept_mimetypes['text/html']


@app.errorhandler(400)
def not_found_error(error):
    return make_error_request_response(HTTPStatus.BAD_REQUEST)


@app.errorhandler(404)
def not_found_error(error):
    return make_error_request_response(HTTPStatus.NOT_FOUND)


@app.errorhandler(500)
def internal_error(error):
    return make_error_request_response(HTTPStatus.INTERNAL_SERVER_ERROR)
