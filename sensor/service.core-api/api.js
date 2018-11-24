const Router = require('koa-router');
const Koa = require('koa');
const bodyParser = require('koa-body')();
const router = new Router();
const api = new Koa();

const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./data/readings.sqlite');

router.get('/data', (ctx, next) => {
  ctx.body = 'Welcome to the Portable Force Rig Core API!';
});

router.post('/data', bodyParser, async (ctx, next) => {
  let data = ctx.request.body.data;
  let dataString = data.join(', ');
  console.log(`Saving new readings to database: ${dataString}`);
  db.run('INSERT INTO data (ant_size, readings) VALUES (?, ?)', [1.76, `[${dataString}]`])
  ctx.body = `Readings successfully saved to the database: ${data}`;
});

api.use(router.routes());
api.use(router.allowedMethods());

const port = 80 || process.env.PORT;
api.listen(port, () => {
  console.log(`Core API listening on port ${port}`);
});
