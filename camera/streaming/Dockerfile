FROM python:3.7-stretch

RUN usermod -aG video root

WORKDIR /usr/src/app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "streamer.py"]
