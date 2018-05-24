import logging
from pprint import pprint

from flask import Flask

from app.resources.users import UserAPI
from app.resources.vpns.servers import VPNServersAPI
from app.resources.vpns.servers.meta import VPNServersMetaAPI
from app.service import *

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load the default configuration
app.config.from_object('config.DevelopmentConfig')

# USER API
user_service = UserService(api_url=app.config['AUTH_SERVICE_URL'],
                           resource_name=app.config['AUTH_SERVICE_USERS_RESOURCE_NAME'])

user_api_view_func = UserAPI.as_view('user_api', user_service, app.config)
app.add_url_rule('%s/%s' % (app.config['API_BASE_URI'], UserAPI.__api_url__), view_func=user_api_view_func,
                 methods=['GET', 'POST', ])
app.add_url_rule('%s/%s/uuid/<string:suuid>' % (app.config['API_BASE_URI'], UserAPI.__api_url__),
                 view_func=user_api_view_func, methods=['GET'])
app.add_url_rule('%s/%s/email/<string:email>' % (app.config['API_BASE_URI'], UserAPI.__api_url__),
                 view_func=user_api_view_func, methods=['GET'])

# VPNC META API
vpnserversmeta_service = VPNServersMetaService(api_url=app.config['VPNC_SERVICE_URL'],
                                               resource_name=app.config['VPNC_SERVICE_VPNSERVERSMETA_RESOURCE_NAME'])

vpnserversmeta_api_view_func = VPNServersMetaAPI.as_view('vpnserversmeta_api', vpnserversmeta_service, app.config)
app.add_url_rule('%s/%s' % (app.config['API_BASE_URI'], VPNServersMetaAPI.__api_url__),
                 view_func=vpnserversmeta_api_view_func, methods=['GET'])

# VPNC API
vpnserver_service = VPNServersService(api_url=app.config['VPNC_SERVICE_URL'],
                                      resource_name=app.config['VPNC_SERVICE_VPNSERVER_RESOURCE_NAME'])
vpntype_service = VPNTypeService(api_url=app.config['VPNC_SERVICE_URL'],
                                 resource_name=app.config['VPNC_SERVICE_VPNTYPE_RESOURCE_NAME'])
vpnserverconfiguration_service = VPNServerConfigurationService(api_url=app.config['VPNC_SERVICE_URL'],
                                                               resource_name=app.config[
                                                                   'VPNC_SERVICE_VPNSERVERCONFIGURATION_RESOURCE_NAME'])
vpnserverstatus_service = VPNServerStatusService(api_url=app.config['VPNC_SERVICE_URL'],
                                                 resource_name=app.config['VPNC_SERVICE_VPNSERVERSTATUS_RESOURCE_NAME'])
geoposition_service = GeoPositionService(api_url=app.config['VPNC_SERVICE_URL'],
                                         resource_name=app.config['VPNC_SERVICE_GEOPOSITION_RESOURCE_NAME'])
geocity_service = GeoCityService(api_url=app.config['VPNC_SERVICE_URL'],
                                 resource_name=app.config['VPNC_SERVICE_GEOCITY_RESOURCE_NAME'])
geocountry_service = GeoCountryService(api_url=app.config['VPNC_SERVICE_URL'],
                                       resource_name=app.config['VPNC_SERVICE_GEOCOUNTRY_RESOURCE_NAME'])
geostate_service = GeoStateService(api_url=app.config['VPNC_SERVICE_URL'],
                                   resource_name=app.config['VPNC_SERVICE_GEOSTATE_RESOURCE_NAME'])

vpn_service = VPNService(vpnserver_service=vpnserver_service, vpntype_service=vpntype_service,
                         vpnserverconfiguration_service=vpnserverconfiguration_service,
                         vpnserverstatus_service=vpnserverstatus_service, geoposition_service=geoposition_service,
                         geocity_service=geocity_service, geocountry_service=geocountry_service,
                         geostate_service=geostate_service)

vpnc_api_view_func = VPNServersAPI.as_view('vpnc_api', vpn_service, app.config)
app.add_url_rule('%s/%s' % (app.config['API_BASE_URI'], VPNServersAPI.__api_url__), view_func=vpnc_api_view_func,
                 methods=['GET'])
app.add_url_rule('%s/%s/status/<string:status>' % (app.config['API_BASE_URI'], VPNServersAPI.__api_url__),
                 view_func=vpnc_api_view_func, methods=['GET'])
app.add_url_rule('%s/%s/<string:suuid>' % (app.config['API_BASE_URI'], VPNServersAPI.__api_url__),
                 view_func=vpnc_api_view_func, methods=['GET'])

pprint(app.url_map._rules_by_endpoint)
