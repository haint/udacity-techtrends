FROM python:3.8

LABEL maintainer="Ethan Nguyen"

COPY techtrends /app

WORKDIR /app

RUN pip install -r requirements.txt

CMD [ "python", "app.py" ]