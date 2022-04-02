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
@app.route('/face/v1/extract', methods=['POST'])
def extract_face_v1():
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


# extract_faces()
@app.route('/face/v2/extract', methods=['POST'])
def extract_face_v2():
    if not request.is_json:
        return "json으로 이미지 url을 전달해 주세요"

    json_response = request.get_json()
    json_obj = json.loads(json_response)
    album_id = json_obj['album_id']
    img_url_list = json_obj['img_urls']
    for img_url in img_url_list:
        img = s3.read_s3_images(album_id, img_url)
        face = rf.extract_face(img)
        send_face_to_siamese(face)
    return "이미지 url 수신 완료"


def send_face_to_siamese(face):
    HOST = "http://"
    PATH = "/siamese"
    url = HOST + PATH
    header = {

    }
    body = {

    }

    requests.post(url,
                  files={}
                  )


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
