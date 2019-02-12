FROM python:3.7-stretch

RUN apt update && apt install -y i2c-tools

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

CMD ["python", "main.py"]
