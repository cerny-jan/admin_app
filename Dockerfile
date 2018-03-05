FROM python:3.6

WORKDIR /app

ADD . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

ENV APP_SECRET="secret_key"
ENV FLASK_APP="app.py"
ENV FLASK_DEBUG=True

CMD ["flask", "run", "-h", "0.0.0.0", "-p", "5000"]
