# 베이스 이미지
FROM python:3.8-slim-buster

# image의 디렉토리로 이동
WORKDIR /app

# 의존성 설치
RUN apt-get update
RUN apt-get -y install libgl1-mesa-glx
RUN apt-get install -y libglib2.0-0 libsm6 libxrender1 libxext6

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# 파일을 모두 컨테이너로 복사
COPY /app .

ENV FLASK_APP app/app.py

EXPOSE 5000

CMD ["python", "-m" , "flask", "run", "--host=0.0.0.0"]