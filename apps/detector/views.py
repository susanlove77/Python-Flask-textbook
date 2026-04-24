# uuid를 import한다
import uuid 
import random
import cv2
import numpy as np
import torch
import torchvision 

from apps.app import db
from apps.crud.models import User
from apps.detector.models import UserImage, UserImageTag
from flask import (Blueprint, current_app, flash, redirect, render_template,  send_from_directory, 
                    url_for, request, )
from PIL import Image
from sqlalchemy.exc import SQLAlchemyError 
# Path를 import 한다
from pathlib import Path 
# UploadImageForm을 import한다
from apps.detector.forms import UploadImageForm, DetectorForm, DeleteForm 
# login_requried, current_user를 import 한다
from flask_login import current_user, login_required

# template_folder를 지정한다(static은 지정하지 않는다)
dt = Blueprint("detector", __name__, template_folder="templates")

# dt 애플리케이션을 사용하여 엔드포인트를 작성한다
@dt.route("/")
def index():
    # raise Exception() 
    # User와 UserImage를 join해서 이미지 일람을 취득한다
    user_images = (
        db.session.query(User, UserImage)
        .join(UserImage)
        .filter(User.id == UserImage.user_id)
        .all()
    )

    # 태그 일람을 가져온다
    user_image_tag_dict = {}
    for user_image in user_images:
        # 이미지에 연결할 태그 일람을 가져온다
        user_image_tags = (
            db.session.query(UserImageTag)
            .filter(UserImageTag.user_image_id ==
                user_image.UserImage.id)
            .all()
        )
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags
    # 물체 감지 폼을 인스턴스화한다
    detector_form = DetectorForm()
    # DeleteForm을 인스턴스화한다
    delete_form = DeleteForm() 

    return render_template("detector/index.html", 
                           user_images=user_images,
                           # 태그 일람을 템플릿에 전달한다
                           user_image_tag_dict=user_image_tag_dict,
                           # 물체 감지 폼을 템플릿에 전달한다
                           detector_form=detector_form,
                           # 이미지 삭제 폼을 템플릿에 건넨다 
                           delete_form=delete_form)

@dt.route("/images/<path:filename>")
def image_file(filename):
    return send_from_directory(current_app.config["UPLOAD_FOLDER"], filename)

@dt.route("/upload", methods=["GET", "POST"])
# 로그인 필수로 한다
@login_required
def upload_image():
    #UploadImageForm을 이용해서 검증한다
    form = UploadImageForm()
    if form.validate_on_submit():
        # 업로드된 이미지 파일을 취득한다
        file = form.image.data
        # 파일의 파일명과 확장자를 취득하고, 파일명을 uuid로 변환한다
        ext = Path(file.filename).suffix
        image_uuid_file_name = str(uuid.uuid4()) + ext
        # 이미지를 저장한다
        image_path = Path(
            current_app.config["UPLOAD_FOLDER"], image_uuid_file_name
        )
        file.save(image_path) 

        # DB에 저장한다
        user_image = UserImage(
            user_id=current_user.id, image_path=image_uuid_file_name
        )
        db.session.add(user_image)
        db.session.commit()
        
        return redirect(url_for("detector.index"))
    return render_template("detector/upload.html", form=form)

def make_color(labels):
    # 테두리 선의 색을 랜덤으로 결정
    colors = [[random.randint(0, 255) for _ in range(3)] for _ in labels]
    color = random.choice(colors)
    return color

def make_line(result_image):
    # 테두리 선을 작성
    line = round(0.002 * max(result_image.shape[0:2])) + 1
    return line 

def draw_lines(c1, c2, result_image, line, color):
    # 사각형의 테두리 선을 이미지에 덧붙여 씀
    cv2.rectangle(result_image, c1, c2, color, thickness=line)
    return cv2

def draw_texts(result_image, line, c1, cv2, color, labels, label):
    display_txt = f"{labels[label]}"
    font = max(line - 1, 1)
    t_size = cv2.getTextSize(display_txt, 0, fontScale=line / 3, thickness=font)[0]
    
    # 텍스트 박스의 끝 지점(c2)을 정확히 계산합니다.
    c2 = c1[0] + t_size[0], c1[1] - t_size[1] - 3
    
    # 그 다음 사각형을 그립니다.
    cv2.rectangle(result_image, c1, c2, color, -1)
    cv2.putText(
        result_image,
        display_txt,
        (c1[0], c1[1] - 2),
        0,
        line / 3,
        [255, 255, 255],
        thickness=font,
        lineType=cv2.LINE_AA,
    )
    return cv2

def exec_detect(target_image_path):
    # 1. 모델 설정 및 추론 (이 부분은 잘 작성하셨습니다!)
    image = Image.open(target_image_path)
    model = torch.hub.load('ultralytics/yolov5', 'custom', 
                           path=Path(current_app.root_path, "detector", "model.pt"))
    model = model.eval()
    output = model(target_image_path) 

    tags = []
    result_image = np.array(image.copy())
    
    # 2. 데이터 정리 (가장 중요한 부분!)
    df = output.pandas().xyxy[0] 
    boxes = df[['xmin', 'ymin', 'xmax', 'ymax']].values
    scores = df['confidence'].values
    # 여기서 'name'을 가져오면 'cat', 'dog' 같은 글자가 바로 들어옵니다.
    current_labels = df['name'].values 

    # 3. 반복문 실행
    # label 변수에는 이제 숫자가 아니라 'cat' 같은 문자열이 들어갑니다.
    for box, label, score in zip(boxes, current_labels, scores):
        # score가 0.5보다 크고, 아직 태그에 등록되지 않은 경우
        if score > 0.5 and label not in tags:
            # 테두리 선의 색 결정 (문자열 리스트를 넘겨줍니다)
            color = make_color(current_labels)
            # 테두리 선의 두께 결정
            line = make_line(result_image)
            
            c1 = (int(box[0]), int(box[1]))
            c2 = (int(box[2]), int(box[3])) 
            
            # 이미지에 테두리 선 그리기
            cv2_img = draw_lines(c1, c2, result_image, line, color)
            
            # --- 텍스트 그리기 (에러 방지 핵심) ---
            # draw_texts 함수가 labels[label] 형태를 기대하므로, 
            # 우리는 label(이미 문자열임)을 담은 리스트와 인덱스 0을 보냅니다.
            cv2_img = draw_texts(result_image, line, c1, cv2_img, color, [label], 0)
            
            tags.append(label)

    # 4. 이미지 저장 로직
    detected_image_file_name = str(uuid.uuid4()) + ".jpg"
    # (오타 수정: cuurent_app -> current_app)
    detected_image_file_path = str(
        Path(current_app.config["UPLOAD_FOLDER"], detected_image_file_name)
    )
    
    cv2.imwrite(detected_image_file_path, cv2_img.cvtColor(
        result_image, cv2_img.COLOR_RGB2BGR)
    )

    return tags, detected_image_file_name

def save_detected_image_tags(user_image, tags, detected_image_file_name):
    # 감지 후 이미지의 저장처 경로를 DB에 저장한다
    user_image.image_path = detected_image_file_name
    # 감지 플래그를 True로 한다
    user_image.is_detected = True
    db.session.add(user_image)

    # user_images_tags 레코드를 작성한다
    for tag in tags:
        user_image_tag = UserImageTag(
            user_image_id=user_image.id, tag_name=tag)
        db.session.add(user_image_tag)
    
    db.session.commit() 

@dt.route("/detect/<string:image_id>", methods=["POST"])
# login_required 데코레이터를 붙여서 로그인 필수로 한다
@login_required
def detect(image_id):
    # user_images 테이블로부터 레코드를 가져온다
    user_image = db.session.query(UserImage).filter(
            UserImage.id == image_id).first()
    if user_image is None:
        flash("물체 감지 대상의 이미지가 존재하지 않습니다.")
        return redirect(url_for("detector.index"))
    # 물체 감지 대상의 이미지 경로를 가져온다
    target_image_path = Path(
        current_app.config["UPLOAD_FOLDER"], user_image.image_path
    )

    # 물체 감지를 실행하여 태그와 변환 후의 이미지 경로를 가져온다
    tags, detected_image_file_name = exec_detect(target_image_path)

    try:
        # 데이터베이스에 태그와 변환 후의 이미지 경로 정보를 저장한다
        save_detected_image_tags(user_image, tags,
            detected_image_file_name)
    except SQLAlchemyError as e:
        flash("물체 감지 처리에서 오류가 발생했습니다.")
        # 롤백한다
        db.session.rollback()
        # 오류 로그 출력
        current_app.logger.error(e)
        return redirect(url_for("detector.index"))

    return redirect(url_for("detector.index"))

@dt.route("/images/delete/<string:image_id>", methods=["POST"])
@login_required
def delete_image(image_id):
    try:
        # user_image_tags 테이블로부터 레코드를 삭제한다
        db.session.query(UserImageTag).filter(
            UserImageTag.user_image_id == image_id
        ).delete()
        # user_images 테이블로부터 레코드를 삭제한다
        db.session.query(UserImage).filter(UserImage.id == image_id).delete()

        db.session.commit()
    except SQLAlchemyError as e:
        flash("이미지 삭제 처리에서 오류가 발생했습니다. ")
        # 오류 로그 출력
        current_app.logger.error(e)
        db.session.rollback()
    
    return redirect(url_for("detector.index")) 
    
@dt.route("/images/search", methods=["GET"])
def search():
    # 이미지 일람을 가져온다
    user_images = db.session.query(User, UserImage).join(
        UserImage, User.id == UserImage.user_id
    )

    # GET 파라미터로부터 검색 단어를 가져온다
    search_text = request.args.get("search")
    user_image_tag_dict = {}
    filtered_user_images = []

    # user_images를 반복하여 user_images에 연결된 정보를 검색한다
    for user_image in user_images:
        # 검색 단어가 빈 경우는 모든 태그를 가져온다
        if not search_text:
            # 태그 일람을 가져온다
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id ==
                        user_image.UserImage.id)
                        .all()            
            )
        else:
            # 검색 단어로 추출한 태그를 가져온다
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id ==
                        user_image.UserImage.id)
                .filter(UserImageTag.tag_name.like(
                    "%" + search_text + "%"))
                .all()
            )

            # 태그를 찾을 수 없었다면 이미지를 반환하지 않는다
            if not user_image_tags:
                continue 

            # 태그가 있는 경우는 태그 정보를 다시 가져온다
            user_image_tags = (
                db.session.query(UserImageTag)
                .filter(UserImageTag.user_image_id ==
                        user_image.UserImage.id)
                .all()
            )
        # user_image_id를 키로 하는 사전에 태그 정보를 설정한다
        user_image_tag_dict[user_image.UserImage.id] = user_image_tags 

        # 추출 결과의 user_image 정보를 배열 설정한다
        filtered_user_images.append(user_image) 
    
    delete_form = DeleteForm()
    detector_form = DetectorForm()

    return render_template(
        "detector/index.html",
        # 추출한 user_images 배열을 전달한다
        user_images=filtered_user_images,
        # 이미지에 연결된 태그 일람의 사전을 전달한다
        user_image_tag_dict=user_image_tag_dict,
        delete_form=delete_form,
        detector_form=detector_form,
    )
        
        
        

