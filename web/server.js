const path = require('path');
const express = require('express');
const mongoose = require('mongoose');
const server = express();

var Pusher = require('pusher');

var pusher = new Pusher({
  appId: '692148',
  key: '638c36a2b0fb6d91b3e6',
  secret: 'e658584ff474cb2803a1',
  cluster: 'eu',
  encrypted: true
});

pusher.trigger('my-channel', 'my-event', {
  "message": "hello world"
});

server.use(express.static(path.join(__dirname, 'client/build')));

server.get('/api/data', (req, res) => {
  res.json({ response: "Hello" });
});

server.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'index.html'));
});

const port = process.env.PORT || 3001;
server.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
