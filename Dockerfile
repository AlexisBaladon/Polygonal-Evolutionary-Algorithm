FROM python:3.9-slim

WORKDIR /app
COPY . /

RUN pip install -r /app/setup/requirements_latest.txt

EXPOSE 5000

ENV FLASK_APP=/app/app.py
ENV FLASK_ENV=production

CMD ["/app/run.sh"]