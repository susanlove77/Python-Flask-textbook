import cv2
import base64
import os
from flask import Flask, render_template
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy 
from flask_wtf.csrf import CSRFProtect 
from flask_socketio import SocketIO
from apps.config import config

from ultralytics import YOLO  # 상단 import에 추가

# 1. 모델 로드 (create_app 밖에서 최초 1회 실행)
# 가장 가벼운 n(nano) 모델을 써야 2개 카메라를 동시에 돌릴 때 속도가 나와.
model = YOLO('yolov8n.pt') 

# --- [수정된 실시간 스트리밍 & AI 탐지 로직] ---
def run_rtsp_stream(cam_id, rtsp_url):
    # 1. 카메라 연결
    cap = cv2.VideoCapture(rtsp_url)
    print(f"[DEBUG] {cam_id} 분석 시작: {rtsp_url}") 
    
    if not cap.isOpened():
        print(f"[ERROR] {cam_id} 연결 실패!")
        return

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
        
        # 2. YOLO 탐지 실행 (conf를 0.25로 낮춰서 더 잘 잡히게 설정)
        results = model(frame, conf=0.25, verbose=False)
        
        # 3. 박스가 그려진 이미지 생성 (이게 빠지면 박스 안 보임!)
        annotated_frame = results[0].plot()
        
        # 4. 전송용 리사이징 및 인코딩
        # 원본 frame이 아니라 'annotated_frame'을 인코딩해야 함!
        annotated_frame = cv2.resize(annotated_frame, (640, 480))
        _, buffer = cv2.imencode('.jpg', annotated_frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')

        # 5. 소켓 전송
        socketio.emit(f'video_frame_{cam_id}', {'image': frame_base64})
        socketio.sleep(0.01) 
    
    cap.release()

# --- [1] 전역 객체 선언 ---
db = SQLAlchemy() 
csrf = CSRFProtect() 
login_manager = LoginManager()
login_manager.login_view = "auth.signup"
login_manager.login_message = ""

# async_mode='threading' (또는 'eventlet') 설정
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading', logger=False, engineio_logger=False)

# --- [2] RTSP 및 카메라 설정 ---
CAM_USER = "admin"
CAM_PW = "Mbc320!!" 
CAM_IPS = [ "192.168.0.43", "192.168.0.38"] # "192.168.0.48" # ipCam 3개면 안돌아감 2개가 MAX 

RTSP_SOURCES = {
    f"cam{i+1}": f"rtsp://{CAM_USER}:{CAM_PW}@{ip}:554/stream1"
    for i, ip in enumerate(CAM_IPS)
}
# 1. 에러 핸들러 함수를 먼저 정의합니다. (위치 이동)
def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404

def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"), 500

def create_app(config_key="local"):
    app = Flask(__name__)
    app.config.from_object(config[config_key])
    
    db.init_app(app)
    Migrate(app, db)
    csrf.init_app(app)
    login_manager.init_app(app)
    socketio.init_app(app)

    # 커스텀 오류 화면을 등록한다
    app.register_error_handler(404, page_not_found)
    app.register_error_handler(500, internal_server_error)

    with app.app_context():
        from apps.crud import views as crud_views 
        app.register_blueprint(crud_views.crud, url_prefix="/crud")
        from apps.auth import views as auth_views
        app.register_blueprint(auth_views.auth, url_prefix="/auth")
        from apps.detector import views as dt_views
        app.register_blueprint(dt_views.dt)

 

    @app.route('/ai_detect/aistream')
    def ai_stream_page():
        return render_template('ai_detect/ai_stream.html')

    return app


@socketio.on('connect')
def handle_connect():
    print(f"\n[SYSTEM] 새 연결 감지! 카메라 개수: {len(RTSP_SOURCES)}")
    for cam_id, url in RTSP_SOURCES.items():
        print(f"[SYSTEM] {cam_id} 백그라운드 태스크 시작 시도 중...")
        socketio.start_background_task(run_rtsp_stream, cam_id, url)

# --- [4] 서버 실행부 ---
app = create_app("local")

if __name__ == '__main__':
    # 생성된 주소 확인용 로그
    print("\n" + "="*50)
    print("서버를 시작합니다. 접속 주소: http://127.0.0.1:5000/ai_detect/aistream")
    for cam, url in RTSP_SOURCES.items():
        print(f" - {cam} 주소: {url}")
    print("="*50 + "\n")

    # socketio.run을 사용해야 실시간 통신이 끊기지 않습니다.
    # debug=False, use_reloader=False를 권장합니다 (SSH 환경 안정성)
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# 등록한 엔드포인트명의 함수를 작성하고, 404 오류나 500 오류가 발생했을 때에 지정한 HTML을 반환한다
def page_not_found(e):
    """404 Not Found"""
    return render_template("404.html"), 404

def internal_server_error(e):
    """500 Internal Server Error"""
    return render_template("500.html"), 500