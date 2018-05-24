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

    VPNC_SERVICE_VPNTYPE_RESOURCE_NAME = 'vpns/types'
    VPNC_SERVICE_VPNSERVER_RESOURCE_NAME = 'vpns/servers'
    VPNC_SERVICE_VPNSERVERSTATUS_RESOURCE_NAME = 'vpns/servers/statuses'
    VPNC_SERVICE_VPNSERVERSMETA_RESOURCE_NAME = 'vpns/servers/meta'
    VPNC_SERVICE_VPNSERVERCONFIGURATION_RESOURCE_NAME = 'vpns/servers/configurations'
    VPNC_SERVICE_GEOPOSITION_RESOURCE_NAME = 'geo_positions'
    VPNC_SERVICE_GEOCITY_RESOURCE_NAME = 'geo_positions/cities'
    VPNC_SERVICE_GEOCOUNTRY_RESOURCE_NAME = 'geo_positions/countries'
    VPNC_SERVICE_GEOSTATE_RESOURCE_NAME = 'geo_positions/states'


class ProductionConfig(Config):
    AUTH_SERVICE_URL = ''
    VNPC_SERVICE_URL = ''


class DevelopmentConfig(Config):
    DEBUG = True

    AUTH_SERVICE_URL = 'http://127.0.0.1:6000/api/v1'

    VPNC_SERVICE_URL = 'http://127.0.0.1:9000/api/v1'


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
