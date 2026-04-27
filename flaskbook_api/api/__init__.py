from flask import Flask, Blueprint, jsonify, request
# 1. config 딕셔너리를 명확하게 임포트합니다.
from flaskbook_api.api.config import config 
from flaskbook_api.api import calculation

api = Blueprint("api", __name__)

def create_app(config_name):
    app = Flask(__name__)
    
    # 2. 이제 위에서 가져온 config 딕셔너리에서 설정을 꺼내옵니다.
    app.config.from_object(config[config_name])

    # 블루프린트 등록 (필요하다면)
    app.register_blueprint(api)

    return app