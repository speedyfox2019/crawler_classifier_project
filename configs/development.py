import os, sys
top_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if not top_path in sys.path:
    sys.path.insert(1, top_path)

class DevelopmentConfig(object):    

    _basedir = os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(
                            os.path.dirname(__file__)))))

    HOST = "0.0.0.0"
    PORT = 5001

    DEBUG = False
    TESTING = False

    SECRET_KEY = "your secret key"

    TEMPORARY_FOLDER = "./temp"

    IMAGE_COUNT_LIMIT = 5
    BROWSER_MODE = "headless" # values: for now, only "headless" works
    CHROMEDRIVER_PATH = "/opt/chromedriver/95.0.4638.54/chromedriver"

    # For testing this code, fill out the following with valid Twitter Account.
    # My recommendation is to use API (with api_key and api_secret) as much as possible.
    TW_USER_NAME = ""
    TW_EMAIL = ""
    TW_PASSWORD = ""
        
    BLUEPRINTS = {
        "api": {
            "URL_PREFIX": "/api",
            "MODULE": "api.views"
        },        
    }