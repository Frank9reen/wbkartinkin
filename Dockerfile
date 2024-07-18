FROM python:3.8-alpine


MAINTAINER Vasilii Zhdanov 'vasilii.zhdanov@gmail.com'

RUN mkdir -p /usr/src/app/wbkartinkin
WORKDIR /usr/src/app/wbkartinkin

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY wbkartinkin .

EXPOSE 8080


CMD ["python", "wsgi.py"]