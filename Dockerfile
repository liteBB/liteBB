FROM python:alpine

WORKDIR /usr/src/liteBB
COPY . .

RUN pip install -r requirements.txt
RUN apk add py-gunicorn

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "-w", "1", "wsgi:application"]