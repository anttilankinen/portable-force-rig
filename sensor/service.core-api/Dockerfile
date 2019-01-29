FROM node:stretch

WORKDIR /usr/src/app

COPY . .

RUN apt-get install libsqlite3-dev && npm install sqlite3 --build-from-source --sqlite=/usr
RUN npm install

EXPOSE 80

CMD ["npm", "start"]
