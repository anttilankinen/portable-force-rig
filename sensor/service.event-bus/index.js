const dotenv = require('dotenv').config();
const redis = require('redis');
const express = require('express');
const app = express();
const server = require('http').createServer(app);
const io = require('socket.io')(server);

const redisClient = redis.createClient({
  host: process.env.DOCKER_HOST,
  port: process.env.REDIS_PORT
});

redisClient.on('error', err => {
  console.error(`Redis client error: ${err}`);
});

redisClient.subscribe('sensor-data');

io.on('connection', socket => {
  console.log('React client connected to socket server!');
  io.emit('connected', 'React client connected to socket server!');
});

redisClient.on('message', (channel, data) => {
  io.emit('new data', { data: data });
});

const port = 80 || process.env.PORT;
server.listen(port, () => {
  console.log(`Event Bus listening on port ${port}`);
});
