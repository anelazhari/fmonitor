FROM python:3.6.8-slim-stretch

LABEL maintainer="an.elazhari@gmail.com"

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

RUN useradd --no-log-init monitor
RUN chown -R monitor:monitor /app

USER monitor

CMD ["python", "run.py"]