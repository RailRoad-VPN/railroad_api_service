class Config(object):
    DEBUG = False
    TESTING = False

    APP_SESSION_SK = 'tbvzCCk6BDYqWDhYTWC'
    SESSION_TYPE = 'filesystem'
    SECRET_KEY = APP_SESSION_SK
    TEMPLATES_AUTO_RELOAD = True

    VERSION = 'v1'
    API_BASE_URI = '/api/%s' % VERSION


class ProductionConfig(Config):
    AUTH_SERVICE_URL = 'http://127.0.0.1:6000/api/v1/users'


class DevelopmentConfig(Config):
    DEBUG = True

    AUTH_SERVICE_URL = 'http://127.0.0.1:6000/api/v1/users'


class TestingConfig(Config):
    TESTING = True
