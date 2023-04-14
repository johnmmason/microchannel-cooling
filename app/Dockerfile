FROM python:3.9

RUN ln -sf /usr/share/zoneinfo/America/Chicago /etc/localtime
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

WORKDIR /app

COPY requirements.txt /app/requirements.txt
RUN pip3 install -r requirements.txt  --no-cache-dir

COPY . /app

CMD ["python3", "-u", "/app/api.py"]
