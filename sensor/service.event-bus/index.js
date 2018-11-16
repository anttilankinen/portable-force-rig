const redis = require('redis');
const express = require('express');
const app = express();
const server = require('http').createServer(app);
const io = require('socket.io')(server);

const port = 80 || process.env.PORT;
server.listen(port, () => {
  console.log(`Event Bus listening on port ${port}`);
});
