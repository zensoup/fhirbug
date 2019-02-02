FROM python:3.6-alpine

RUN apk update && \
    apk upgrade && \
    apk add git
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN pip install git+https://github.com/zensoup/fhirbug
RUN mv settings_prod.py settings.py

CMD python tools/download_examples.py && \
    python generate_examples.py -w && \
    gunicorn --workers=4 --bind 0.0.0.0:5000  flask_app:app

# Uncomment this line to skip example generation
# CMD [ "python", "./flask_app.py" ]
