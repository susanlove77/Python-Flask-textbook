from flask import (Flask, render_template, current_app, g, request, flash, 
                   url_for, redirect, make_response, session) 
from email_validator import validate_email, EmailNotValidError 
import logging 
import os
from flask_debugtoolbar import DebugToolbarExtension 
from flask_mail import Mail, Message

app = Flask(__name__) 
app.config["SECRET_KEY"] = "2AZSMss3p5QPbcY2hBsJ"
# 로그 레벨을 설정
app.logger.setLevel(logging.DEBUG) 
# 리다이렉트를 중단하지 않도록 한다
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]= False
# DebugToolbarExtension에 에플리케이션을 설정
app.debug = True
toolbar = DebugToolbarExtension(app) 

app.logger.critical("fatal error")
app.logger.error("error")
app.logger.warning("warning")
app.logger.info("info")
app.logger.debug("debug")

# Gmail SMTP 설정
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'jojeonghwa93@gmail.com'
app.config['MAIL_PASSWORD'] = 'vfwk nqvc kzcc fcro'  # 16자리 앱 비밀번호
app.config['MAIL_DEFAULT_SENDER'] = 'jojeonghwa93@gmail.com'

mail = Mail(app) 

# 1. 메인 페이지
@app.route("/", endpoint="endpoint-name")
def index():
    return "Hello, Flaskbook!"

# 2. 기본 안녕 페이지 (이름 없을 때)
@app.route("/hello", endpoint="hello-basic")
def hello_world(): 
    return "Hello, World!"

# 3. 이름을 받아서 처리하는 페이지 (GET/POST 모두 허용)
# 주소창에 /hello/AK 처럼 입력하면 작동합니다.
@app.route("/hello/<name>", methods=["GET", "POST"], endpoint="hello-endpoint")
def hello_with_name(name):
    return f"Hello, {name}!"

# 4. HTML 템플릿을 보여주는 페이지
# 주소창에 /name/정화 처럼 입력하면 templates/index.html을 보여줍니다.
@app.route("/name/<name>", endpoint="show-name-endpoint")
def show_name_template(name):
    return render_template("index.html", name=name) 

with app.test_request_context():
    print(url_for("endpoint-name"))
    print(url_for("hello-endpoint",name="world"))
    print(url_for("show-name-endpoint",name="AK",page="1")) 

@app.route("/contact")
def contact():
    # 1. 먼저 HTML 템플릿으로 응답 객체를 만듭니다.
    response = make_response(render_template("contact.html"))

    # 2. [취득] 브라우저에 이미 저장된 "username" 쿠키가 있는지 확인해봅니다.
    # (처음 접속할 때는 없겠지만, 두 번째 접속부터는 "AK"가 찍힐 거예요)
    username = request.cookies.get("username")
    print(f"현재 쿠키에 저장된 이름: {username}")

    # 3. [삭제] 만약 기존에 잘못된 쿠키가 있다면 삭제합니다. (실습용)
    # response.delete_cookie("username") 

    # 4. [설정] 쿠키와 세션에 값을 새로 저장합니다.
    response.set_cookie("username", "AK") # 쿠키 설정
    response.set_cookie("flashbook_key", "flashbook_value") # 추가 쿠키
    session["username"] = "AK" # 세션 설정

    # 5. 모든 설정이 담긴 응답 객체를 반환합니다.
    return response

@app.route("/contact/complete", methods=["GET", "POST"])
def contact_complete():
    if request.method == "POST":
        # 데이터 가져오기 (request.form.get 권장)
        username = request.form.get("username")
        email = request.form.get("email")
        description = request.form.get("description")

        is_valid = True

        # 유효성 검사
        if not username:
            flash("사용자명은 필수입니다")
            is_valid = False
        if not email:
            flash("메일 주소는 필수입니다")
            is_valid = False
        if not description:
            flash("문의 내용은 필수입니다")
            is_valid = False
        
        # 실패 시 다시 입력창으로
        if not is_valid:
            return redirect(url_for("contact"))

        # --- [여기가 핵심] 모든 검사 통과 시 ---
        flash("문의 내용은 메일로 송신했습니다. 문의해 주셔서 감사합니다.") # 메시지 주머니에 넣기

        send_email(email, "문의 감사합니다.","contact_mail", username=username,
                   description=description,)

        return redirect(url_for("contact_complete")) # POST 후에는 반드시 리다이렉트!
    
    # GET 요청 시 (즉, 위에서 리다이렉트되어 다시 들어올 때)
    return render_template("contact_complete.html")

def send_email(to, subject, template, **kwargs):
    """메일을 송신하는 함수"""
    msg = Message(subject, recipients=[to])
    msg.body = render_template(template + ".txt", **kwargs)
    msg.html = render_template(template + ".html", **kwargs)
    mail.send(msg) 

# 애플리케이션 컨텍스트를 취득하여 스택에 push한다 
ctx = app.app_context()
ctx.push()

# current_app에 접근할 수 있게 된다
print(current_app.name)

# 전역 임시 영역에 값을 설정한다
g.connection = "connection"
print(g.connection) 

with app.test_request_context("/users?updated=true"):
    print(request.args.get("updated")) 

@app.route("/contact/test_mail")
def test_mail():
    msg = Message(
        "Flaskbook 메일 테스트",
        recipients=["jojeonghwa93@gmail.com"] # 본인 메일로 해서 테스트해보세요!
    )
    msg.body = "구글 앱 비밀번호를 이용한 메일 발송에 성공했습니다!"
    
    try:
        mail.send(msg)
        return "메일 발송 성공! 메일함을 확인하세요."
    except Exception as e:
        return f"에러 발생: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True) # 여기서 True로 설정
