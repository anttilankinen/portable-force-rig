FROM python:3.7-stretch

WORKDIR /usr/src/app

COPY . .

RUN apt update && apt install -y i2c-tools libatlas-base-dev
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python", "main.py"]
