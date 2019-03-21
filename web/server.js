const path = require('path');
const express = require('express');
const mongoose = require('mongoose');
const app = express();

app.use('/', express.static(path.join(__dirname + '/landing')));
app.use('/dashboard', express.static(path.join(__dirname + '/dashboard/build')));

app.get('/api/data', (req, res) => {
  res.json({ response: 'Hello' });
});

app.get('*', (req, res) => {
  res.redirect('/');
});

const port = process.env.PORT || 3001;
app.listen(port, () => {
  console.log(`Server listening on port ${port}`);
});
