from flask import Flask, request
from PIL import Image
import io
import cv2
import numpy as np
import align_face as af
import detect_face as df

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/face/extract', methods=['POST'])
def extract_face():
    img_byte = request.files['file_url'].read()
    data_io = io.BytesIO(img_byte)
    img = Image.open(data_io)
    image = np.array(img)

    detect = df.detect_face(image)
    for k in detect:
        bbox = detect[k]['facial_area']
        left_eye = detect[k]['landmarks']['left_eye']
        right_eye = detect[k]['landmarks']['right_eye']

        angle = af.align_angle(left_eye, right_eye)

        face_img = img.crop(tuple(bbox)).rotate(angle)
        print(type(face_img))
        return "성공"


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
