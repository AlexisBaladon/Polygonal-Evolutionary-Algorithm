FROM python:3.9-slim

WORKDIR /app
COPY . /app

RUN pip install -r /app/setup/requirements_latest.txt

EXPOSE 5000

ENV FLASK_APP=/app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "4", "app:app", "worker-class", "eventlet", "--timeout", "90", "--reload"]