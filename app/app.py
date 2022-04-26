import json

from flask import Flask, request
from PIL import Image
import io
import requests
import numpy as np
import align_face as af
import retina_face as rf
import s3_download as s3

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello'


# detect_faces()
@app.route('/api/v1/face/detect', methods=['POST'])
def detect_face_v1():
    img_byte = request.files['file_url'].read()
    data_io = io.BytesIO(img_byte)
    img = Image.open(data_io)
    image = np.array(img)

    detect = rf.detect_face(image)
    for k in detect:
        bbox = detect[k]['facial_area']
        left_eye = detect[k]['landmarks']['left_eye']
        right_eye = detect[k]['landmarks']['right_eye']

        angle = af.align_angle(left_eye, right_eye)

        face_img = img.crop(tuple(bbox)).rotate(angle)
        print(type(face_img))
        return "성공"


# 앨범ID와 이미지URL을 받아 얼굴 추출
@app.route('/api/v1/face/extract', methods=['POST'])
def extract_face_v1():
    if not request.is_json:
        print(request.get_json())
        return "json으로 이미지 url을 전달해 주세요"

    task_id_list = list()

    json_request = request.get_json()
    album_id = json_request['album_id']
    img_url_list = json_request['img_urls']

    # 앨범의 이미지수 만큼 extract_face()
    for img_url in img_url_list:
        req = {
            'album_id': album_id,
            'img_url': img_url,
            'file_url': ''
        }
        img = s3.read_s3_images(album_id, img_url)
        np_img = np.array(img)
        faces = rf.extract_face(np_img)
        print("얼굴 수:", len(faces))

        # 이미지의 얼굴 수만큼 siamese에 작업 요청
        for face in faces:
            req['file_url'] = face.tobytes()
            task_id_list.append(send_face_to_mq(req))

    return '작업 완료'


# extract_faces()
@app.route('/api/v3/face/extract', methods=['POST'])
def extract_face_v3():
    img_byte = request.files['file_url'].read()
    data_io = io.BytesIO(img_byte)
    img = Image.open(data_io)
    image = np.array(img)

    detects = rf.extract_face(image)
    faces = []
    for d in detects:
        img = Image.fromarray(d)
        faces.append(img.convert('RGB'))

    for f in faces:
        print(type(f))
    print(len(detects))
    return "성공"


# MQ에 작업 등록
def send_face_to_mq(req):
    print(req['album_id'], req['img_url'])
    url = 'localhost:5001/request/siamese'
    res = requests.post(url)
    print('siamese mq에 전송완료')
    return res


# siamese mq에 작업 확인
def check(task_id):
    url = 'localhost:5001/check/'
    res = requests.get(url + str(task_id))
    return res


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5999)
