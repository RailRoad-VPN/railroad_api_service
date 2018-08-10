class Config(object):
    DEBUG = False
    TESTING = False

    APP_SESSION_SK = 'tbvzCCk6BDYqWDhYTWC'
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = APP_SESSION_SK
    TEMPLATES_AUTO_RELOAD = True

    VERSION = 'v1'
    API_BASE_URI = '/api/%s' % VERSION

    AUTH_SERVICE_USERS_RESOURCE_NAME = 'users'
    AUTH_SERVICE_USER_DEVICES_RESOURCE_NAME = 'users/<string:user_uuid>/devices'

    BILLING_SERVICE_SUBSCRIPTIONS_RESOURCE_NAME = 'subscriptions'
    BILLING_SERVICE_USER_SUBSCRIPTION_RESOURCE_NAME = 'users/<string:user_uuid>/subscriptions'
    BILLING_SERVICE_ORDERS_RESOURCE_NAME = 'orders'
    BILLING_SERVICE_PAYMENTS_RESOURCE_NAME = 'orders/<string:order_uuid>/payments'

    VPNC_SERVICE_VPNTYPE_RESOURCE_NAME = 'vpns/types'
    VPNC_SERVICE_VPNSERVER_RESOURCE_NAME = 'vpns/servers'
    VPNC_SERVICE_VPNSERVERSTATUS_RESOURCE_NAME = 'vpns/servers/statuses'
    VPNC_SERVICE_VPNSERVERSMETA_RESOURCE_NAME = 'vpns/servers/meta'
    VPNC_SERVICE_VPNSERVERCONFIGURATIONS_RESOURCE_NAME = 'vpns/servers/<string:server_uuid>/configurations'
    VPNC_SERVICE_VPNSERVERCONNECTIONS_RESOURCE_NAME = 'vpns/servers/<string:server_uuid>/connections'

    VPNC_SERVICE_GEOPOSITION_RESOURCE_NAME = 'geo_positions'
    VPNC_SERVICE_GEOCITY_RESOURCE_NAME = 'geo_positions/cities'
    VPNC_SERVICE_GEOCOUNTRY_RESOURCE_NAME = 'geo_positions/countries'
    VPNC_SERVICE_GEOSTATE_RESOURCE_NAME = 'geo_positions/states'


class ProductionConfig(Config):
    ENV = 'production'

    AUTH_SERVICE_URL = ''
    VNPC_SERVICE_URL = ''
    BILLING_SERVICE_URL = ''


class DevelopmentConfig(Config):
    ENV = 'development'

    DEBUG = True

    AUTH_SERVICE_URL = 'http://127.0.0.1:6000/api/v1'
    VPNC_SERVICE_URL = 'http://127.0.0.1:9000/api/v1'
    BILLING_SERVICE_URL = 'http://127.0.0.1:7000/api/v1'

    APN_PATH = '/Users/dikkini/Developing/workspaces/my/DFN/railroad_api_service/%s.apn'


class TestingConfig(Config):
    ENV = 'testing'

    TESTING = True
    DEBUG = True

    AUTH_SERVICE_URL = 'http://127.0.0.1:6000/api/v1'
    VPNC_SERVICE_URL = 'http://127.0.0.1:9000/api/v1'
    BILLING_SERVICE_URL = 'http://127.0.0.1:7000/api/v1'

    APN_PATH = '/opt/apps/dfn/apn/%s.apn'
