FROM python:3.9-slim

WORKDIR /
COPY . /

# RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

RUN pip install -r /setup/requirements_latest.txt

EXPOSE 5000

ENV FLASK_APP=/app.py
ENV FLASK_ENV=production

CMD ["bash", "/run.sh"]