import logging
from pprint import pprint

from flask import Flask

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load the default configuration
app.config.from_object('config.DevelopmentConfig')


pprint(app.url_map._rules_by_endpoint)
