import logging
from pprint import pprint

from flask import Flask

from app.resource.vpn import VPNServersAPI
from app.service import UserService
from app.resource.rrnuser import UserAPI

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load the default configuration
app.config.from_object('config.DevelopmentConfig')

# USER API
user_service = UserService(api_url=app.config['AUTH_SERVICE_URL'])

user_api_view_func = UserAPI.as_view('user_api', user_service, app.config)
app.add_url_rule('%s/%s' % (app.config['API_BASE_URI'], UserAPI.__api_url__), view_func=user_api_view_func,
                 methods=['GET', 'POST', ])
app.add_url_rule('%s/%s/uuid/<string:uuid>' % (app.config['API_BASE_URI'], UserAPI.__api_url__),
                 view_func=user_api_view_func, methods=['GET', 'PUT'])
app.add_url_rule('%s/%s/email/<string:email>' % (app.config['API_BASE_URI'], UserAPI.__api_url__),
                 view_func=user_api_view_func, methods=['GET'])

# VPNC API

vpnc_api_view_func = VPNServersAPI.as_view('vpnc_api', app.config)
app.add_url_rule('%s/%s' % (app.config['API_BASE_URI'], VPNServersAPI.__api_url__), view_func=vpnc_api_view_func,
                 methods=['GET'])
app.add_url_rule('%s/%s/<string:uuid>' % (app.config['API_BASE_URI'], VPNServersAPI.__api_url__),
                 view_func=vpnc_api_view_func, methods=['GET'])

pprint(app.url_map._rules_by_endpoint)
