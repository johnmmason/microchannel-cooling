FROM python:3.9



# COPY api.py /app/
# COPY requirements.txt /app/
# COPY model /app/model

RUN ln -sf /usr/share/zoneinfo/America/Chicago /etc/localtime

COPY . /app
WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt

CMD ["python3", "-u", "/app/api.py"]
