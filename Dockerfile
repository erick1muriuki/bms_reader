FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    bluetooth \
    bluez \
    dbus \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY bms_reader.py .

CMD ["python", "bms_reader.py"]
