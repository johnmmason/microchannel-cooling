FROM python:3.9

RUN ln -sf /usr/share/zoneinfo/America/Chicago /etc/localtime

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

CMD ["python3", "-u", "/app/api.py"]
