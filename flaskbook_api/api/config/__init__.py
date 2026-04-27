from flaskbook_api.api.config import base, local 
config = {
    "base" : base.Config,
    "local" : local.LocalConfig,
} 

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    return app