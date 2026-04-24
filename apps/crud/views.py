# apps/crud/views.py
from flask import Blueprint, render_template, redirect, url_for, request  # [추가] request가 꼭 있어야 합니다!
from flask_login import login_required
# db를 import한다 
from apps.app import db
# User 클래스를 import 한다 
from apps.crud.models import User
# 개수 세기 위해 필요
from sqlalchemy import func 
from apps.crud.forms import UserForm 
crud = Blueprint(
    "crud",
    __name__,
    template_folder="templates",
    static_folder="static",
)

@crud.route("/")
# 데코레이터를 추가한다
@login_required 
def index():
    return render_template("crud/index.html")
# ================================================================================
@crud.route("/sql")
@login_required 
def sql():
    db.session.query(User).all() 
    return "콘솔 로그를 확인해 주세요"
# ================================================================================
    #.all() 대신 .first() 사용
    # user = db.session.query(User).first() 

    # if user:
    #     # 리스트가 아니므로 user[0] 처럼 쓸 필요 없이 바로 접근!
    #     print(f"가져온 유저 이름: {user.username}")
    #     return f"첫 번째 가입자: {user.username} (이메일: {user.email})"
    
    # return "유저가 한 명도 없습니다."
#==================================================================================
    # # id가 2이면서 username이 "admin"인 사용자를 모두 가져오라는 뜻입니다.
    # users = db.session.query(User).filter_by(id=2, username="admin").all()
    
    # print("-" * 30)
    # print(f"검색 결과: {users}") # 결과가 리스트 형태로 출력됩니다.
    
    # if users:
    #     return f"찾았습니다! 이름: {users[0].username}"
    # else:
    #     return "조건에 맞는 유저가 DB에 없어요."
#===================================================================================

@crud.route("/sql_limit")
def sql_limit():
    # 딱 1건만 가져오되, '리스트'에 담아서 가져옵니다.
    users = db.session.query(User).limit(1).all()
    
    # [주의] all()을 썼기 때문에 데이터가 한 개라도 users[0]으로 접근해야 합니다.
    if users:
        return f"Limit으로 찾은 유저: {users[0].username}"
    
    return "유저가 없네요."

#===================================================================================

# offset : 앞에서 n명을 건너뛰다 | limit : n명만 가져와라

@crud.route("/sql_offset")
def sql_offset():
    # 2명을 건너뛰고(0번, 1번 제외), 3번째 사람부터 1명만 가져오기
    users = db.session.query(User).limit(1).offset(2).all()
    
    if users:
        return f"3번째 순서의 유저: {users[0].username}"
    
    return "해당 순서에 유저가 없네요."

#===================================================================================

@crud.route("/sql_order")
def sql_order():
    # username 컬럼을 기준으로 오름차순(A-Z, 가나다) 정렬
    users = db.session.query(User).order_by("username").all()
    
    # 만약 역순(Z-A)으로 하고 싶다면?
    # from sqlalchemy import desc
    # users = db.session.query(User).order_by(desc("username")).all()
    
    print("-" * 30)
    for user in users:
        print(f"이름: {user.username}")
        
    return "터미널에서 정렬된 이름을 확인하세요!"

#===================================================================================

@crud.route("/sql_group")
def sql_group():
    # 이름별로 그룹을 묶고, 각 이름이 몇 명인지 세어보기
    # (실제 서비스에선 아이디 중복이 안 되겠지만, 통계 낼 때 유용해요)
    results = db.session.query(User.username, func.count(User.id)).group_by("username").all()
    
    print("-" * 30)
    for name, count in results:
        print(f"이름: {name}, 해당 이름을 쓰는 사람 수: {count}")
        
    return "터미널에서 그룹화 결과를 확인하세요!"

#===================================================================================

@crud.route("/users/new", methods=["GET", "POST"])
@login_required 
def create_user():
     # UserForm을 인스턴스화한다
    form = UserForm()
    # 폼의 값을 검증
    if form.validate_on_submit():
        # 사용자를 작성
        user = User(
            username = form.username.data,
            email=form.email.data,
            password=form.password.data,
        )
        # 사용자를 추가하고 커밋
        db.session.add(user)
        db.session.commit()
        # 사용자의 알람 화면으로 리다이렉트한다
        return redirect(url_for("crud.users"))
    return render_template("crud/create.html", form=form)

@crud.route("/insert") # 혹은 기존의 create_user 함수 내부
def insert_test():
    # ✅ 반드시 함수 안에 있어야 Flask가 "아, 누가 이 주소로 들어왔구나" 하고 실행합니다.
    ### insert ### 
    # 사용자 모델 객체를 작성한다 
    user = User(
        username="사용자명",
        email="flaskbook@example.com",
        password="비밀번호"
    )
    # 사용자 추가
    db.session.add(user)
    # 커밋한다
    db.session.commit() 

    ### update하기 ###
    user = db.session.query(User).filter_by(id=1).first()
    user.username = "사용자명2"
    user.email = "flaskbook2@example.com"
    user.password = "비밀번호2"
    db.session.add(user)
    db.session.commit() 

    ### delete 하기 ###
    user = db.session.query(User).filter_by(id=1).delete()
    db.session.commit()

@crud.route("/users")
@login_required 
def users():
    """사용자의 알람을 취득한다"""
    users = User.query.all()
    return render_template("crud/index.html", users=users)

@crud.route("/users/<user_id>", methods=["GET", "POST"])
@login_required 
def edit_user(user_id):
    form = UserForm()

    # User 모델을 이용하여 사용자를 취득
    user = User.query.filter_by(id=user_id).first()

    # form으로부터 제출된 경우는 사용자를 갱신하여 사용자의 일람 화면으로 리다이렉트한다 
    if form.validate_on_submit():
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("crud.users"))
    
    # GET의 경우는 HTML을 반환한다
    return render_template("crud/edit.html", user=user, form=form)

@crud.route("/users/<user_id>/delete", methods=["POST"])
@login_required 
def delete_user(user_id):
    user=User.query.filter_by(id=user_id).first()
    db.session.delete(user)
    db.session.commit ()
    return redirect(url_for("crud.users"))