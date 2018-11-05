const path = require('path');
const express = require('express');
const mongoose = require('mongoose');

const server = express();

server.use(express.static(path.join(__dirname, 'client/build')));

server.get('/api/data', (req, res) => {
  res.json({ response: "Hello" });
});

server.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'client/build/index.html'));
});

const port = process.env.PORT || 3001;

server.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
