import json

from flask import Flask, request
import requests
import polling
import numpy as np
import retina_face as rf
import s3_download as s3

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello'


# detect_faces()
# @app.route('/api/v1/face/detect', methods=['POST'])
# def detect_face_v1():
#     img_byte = request.files['file_url'].read()
#     data_io = io.BytesIO(img_byte)
#     img = Image.open(data_io)
#     image = np.array(img)
#
#     detect = rf.detect_face(image)
#     for k in detect:
#         bbox = detect[k]['facial_area']
#         left_eye = detect[k]['landmarks']['left_eye']
#         right_eye = detect[k]['landmarks']['right_eye']
#
#         angle = af.align_angle(left_eye, right_eye)
#
#         face_img = img.crop(tuple(bbox)).rotate(angle)
#         print(type(face_img))
#         return "성공"

# detect -> mq2
# {
#   album_id : "",
#   original_image_url : "",
#   file_image : ""
# }
# 앨범ID와 이미지URL을 받아 얼굴 추출
@app.route('/data', methods=['POST'])
def extract_face_v1():
    req_str = request.data.decode('utf8').replace("'", '"')
    req_json = json.loads(req_str)

    # if not req_json.is_json:
    #     print(req_json.get_json())
    #     return "json으로 이미지 url을 전달해 주세요"

    task_id_list = list()  # mq 작업 id

    album_id = req_json['album_id']
    img_url_list = req_json['img_urls']

    # 앨범의 이미지수 만큼 extract_face()
    for img_url in img_url_list:
        req = {
            'album_id': album_id,
            'original_image_url': img_url,
        }
        img = s3.read_s3_images(album_id, img_url)
        np_img = np.array(img)
        faces = rf.extract_face(np_img)
        print("얼굴 수:", len(faces))

        # 이미지의 얼굴 수만큼 siamese에 작업 요청
        for face in faces:
            # req['file_url'] = face.tobytes()
            task_id_list.append(send_face_to_mq(req, face))

    # 모든 작업이 완료될 때까지 폴링
    polling.poll(
        lambda: check_all(task_id_list)['pending'] is False,
        step=60,
        poll_forever=True
    )

    return '작업 완료'


# extract_faces()
# @app.route('/api/v3/face/extract', methods=['POST'])
# def extract_face_v3():
#     img_byte = request.files['file_url'].read()
#     data_io = io.BytesIO(img_byte)
#     img = Image.open(data_io)
#     image = np.array(img)
#
#     detects = rf.extract_face(image)
#     faces = []
#     for d in detects:
#         img = Image.fromarray(d)
#         faces.append(img.convert('RGB'))
#
#     for f in faces:
#         print(type(f))
#     print(len(detects))
#     return "성공"


# detect -> mq2
# {
#   album_id : "",
#   original_image_url : "",
#   file_image : ""
# }

# MQ에 작업 등록
def send_face_to_mq(req, face):
    print(req['album_id'], req['img_url'])
    print('-----mq2에 전송시작-----')
    url = 'http://localhost:5002/request/siamese'
    res = requests.post(url, files=face)
    print('-----mq2에 전송완료-----')
    return res


# siamese mq에 작업 확인
def check(task_id):
    url = 'http://host.docker.internal:5002/check/'
    res = requests.get(url + str(task_id))
    return res


# 모든 작업 check
def check_all(task_id_list):
    results = {
        'pending': False
    }
    for task_id in task_id_list:
        result = check(task_id)
        if result == 'pending':
            results['pending'] = True
            break
        else:
            results[task_id] = result
    return results


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5999)
