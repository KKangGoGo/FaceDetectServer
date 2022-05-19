import boto3
import config as cf
from PIL import Image


def s3_client():
    return boto3.client('s3',
                        aws_access_key_id=cf.AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=cf.AWS_SECRET_ACCESS_KEY,
                        region_name=cf.AWS_S3_BUCKET_REGION)


def read_s3_images(album_id, img_url):
    url = f'album/{album_id}/{img_url}'
    print(url)
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(name=cf.AWS_S3_BUCKET_NAME)
    response = bucket.Object(url).get()
    file_stream = response['Body']
    img = Image.open(file_stream)
    return img


def upload_image(img, uuid, num):
    s3 = s3_client()
    s3.put_object(Key=str(uuid)+'/'+str(num)+'.png', Body=img, Bucket='tmp-face-bucket')


def delete_image(uuid, num):
    s3 = s3_client()
    s3.delete_object(Key=str(uuid)+'/'+str(num)+'.png', Bucket=cf.AWS_S3_BUCKET_NAME)