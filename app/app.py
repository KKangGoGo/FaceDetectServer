import json

from flask import Flask, request, jsonify
import requests
import polling
import numpy as np
import retina_face as rf
import s3_download as s3
import config as cf
import uuid
from PIL import Image
import io
import pprint

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello'


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

    task_id_list = list()  # mq 작업 id

    album_id = req_json['album_id']
    img_url_list = req_json['img_urls']

    # 앨범의 이미지수 만큼 extract_face()
    for img_url in img_url_list:
        img = s3.read_s3_images(img_url)
        np_img = np.array(img)
        faces = rf.extract_face(np_img)
        print("얼굴 수:", len(faces))

        # 이미지의 얼굴 수만큼 siamese에 작업 요청
        index = 0
        image_id = uuid.uuid4()
        for face in faces:
            img = Image.fromarray(face).convert('RGB')
            out_img = io.BytesIO()
            img.save(out_img, format='png')
            out_img.seek(0)
            s3.upload_image(out_img, image_id, index)

            task_id_list.append(bytes.decode(send_face_to_mq(album_id, img_url, f'https://{cf.AWS_S3_UP_BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{image_id}/{index}.png')))
            index += 1

    print(task_id_list)

    # 모든 작업이 완료될 때까지 폴링
    response = {
        "album_id": album_id,
        "result": {

        }
    }
    polling.poll(
        lambda: check_all(task_id_list, response)['PENDING'] is False,
        step=3,
        poll_forever=True
    )

    # mq1에 리턴
    return jsonify(response)


# MQ2에 작업 등록
def send_face_to_mq(album_id, img_url, file_image):
    req = {
        "album_id": album_id,
        "original_image_url": f'https://{cf.AWS_S3_UP_BUCKET_NAME}.s3.ap-northeast-2.amazonaws.com/{img_url}',
        "file_image": file_image
    }
    print(req)
    print('-----mq2에 전송시작-----')

    url = 'http://' + cf.MQ_DETECT_SIAMESE_SERVER + '/request/siamese'
    headers = {"Content-Type": "application/json"}

    res = requests.post(url, data=json.dumps(req), headers=headers)

    print('-----mq2에 전송완료-----')
    return res.content


# mq2에 작업 확인
def check(task_id):
    url = 'http://' + cf.MQ_DETECT_SIAMESE_SERVER + '/check/'
    res = requests.get(url + str(task_id))
    print("check " + task_id, bytes.decode(res.content))
    return res.content


# 모든 작업 check
def check_all(task_id_list, response):
    results = {
        'PENDING': False
    }
    for task_id in task_id_list:
        result = bytes.decode(check(task_id))
        if result == 'PENDING':
            results['PENDING'] = True
            pprint.pprint(results)
            break
        else:
            task_id_list.remove(task_id)
            results[task_id] = result
            pprint.pprint(results)

            result = result.replace("'", '"')
            result = json.loads(str(result))
            if result['person_username'] in response:
                response.get(result['person_username']).append(result['original_image_url'])
            else:
                response['result'][result['person_username']] = [result['original_image_url']]

    return results


if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5999)
