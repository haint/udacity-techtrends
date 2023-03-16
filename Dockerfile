FROM python:3.8

LABEL maintainer="Ethan Nguyen"

COPY techtrends /app

WORKDIR /app

RUN pip install -U pip wheel setuptools && pip install -r requirements.txt
RUN python init_db.py

CMD [ "python", "app.py" ]