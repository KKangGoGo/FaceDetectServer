from flask import Flask, request
import json
from retinaface import RetinaFace
import math
import numpy as np
from PIL import Image
import io

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


def detect_face():
    detect = RetinaFace.detect_faces('aespa.jpg')
    return detect


def euclidean_distance(a, b):
    x1 = a[0]
    y1 = a[1]
    x2 = b[0]
    y2 = b[1]
    return math.sqrt(((x2 - x1) * (x2 - x1)) + ((y2 - y1) * (y2 - y1)))


def align_angle(left_eye, right_eye):
    # 회전 방향 결정
    if left_eye[1] <= right_eye[1]:  # 오른쪽 눈이 높으면 시계방향
        direction = -1
        point_3rd = (right_eye[0], left_eye[1])
    else:  # 반시계방향
        direction = 1
        point_3rd = (left_eye[0], right_eye[1])

    a = euclidean_distance(left_eye, point_3rd)
    b = euclidean_distance(right_eye, left_eye)
    c = euclidean_distance(right_eye, point_3rd)

    cos_a = (b * b + c * c - a * a) / (2 * b * c)
    print("cos(a) = ", cos_a)

    angle = np.arccos(cos_a)
    print("angle: ", angle, " in radian")

    angle = (angle * 180) / math.pi
    print("angle: ", angle, " in degree")

    if direction == -1:
        angle = 90 - angle
    return angle * direction


@app.route('/detect/save')
def crop_rotate_img():
    img = Image.open("aespa.jpg")
    detect = detect_face()
    for k in detect:
        area = detect[k]['facial_area']
        print(k + ": " + str(area))

        left_eye = detect[k]['landmarks']['left_eye']
        right_eye = detect[k]['landmarks']['right_eye']
        angle = align_angle(left_eye, right_eye)
        print(angle)

        cropped_img = img.crop(tuple(area))
        cropped_img = cropped_img.rotate(angle)

        # 이걸 샴 서버에 전달 묶어서
        print(type(cropped_img.tobytes()))

    return '0'


# def get_image():
#     img_byte = request.files[Config.get_fine_key].read()
#     data_io = io.BytesIO(img_byte)
#     return data_io


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
