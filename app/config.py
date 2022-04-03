import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_REGION = 'ap-northeast-2'
AWS_S3_BUCKET_NAME = 'ksb-bucket-test'
USERS_IMAGE_PREFIX = 'users'

GET_S3_IMAGE_URL = f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_S3_BUCKET_REGION}.amazonaws.com/"
