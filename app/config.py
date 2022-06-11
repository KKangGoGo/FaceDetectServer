import os

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET_REGION = os.getenv("AWS_S3_BUCKET_REGION")
AWS_S3_UP_BUCKET_NAME = os.getenv("AWS_S3_UP_BUCKET_NAME")
AWS_S3_DOWN_BUCKET_NAME = os.getenv("AWS_S3_DOWN_BUCKET_NAME")
MQ_DETECT_SIAMESE_SERVER = os.getenv("MQ_DETECT_SIAMESE_SERVER")