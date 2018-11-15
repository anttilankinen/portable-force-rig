const express = require('express');
const controller = express();

controller.get('/', (req, res) => {
  res.send("Controller GET");
});

controller.post('/', (req, res) => {
  res.send("Controller POST");
});

const port = 80 || process.env.PORT;
controller.listen(port, () => {
  console.log(`Controller listening on port ${port}`);
});
