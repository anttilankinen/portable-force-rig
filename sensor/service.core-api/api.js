const Router = require('koa-router');
const Koa = require('koa');
const bodyParser = require('koa-body')();
const router = new Router();
const api = new Koa();

const sqlite = require('sqlite');
const dbPromise = sqlite.open('./data/readings.sqlite');

router.get('/data', async (ctx, next) => {
  try {
    const db = await dbPromise;
    const rows = await db.all('SELECT * FROM data');
    ctx.body = { rows: rows };
  } catch (err) {
    console.log(err);
  }
});

router.post('/data', bodyParser, async (ctx, next) => {
  let data = ctx.request.body.data;
  let dataString = `[${data.join(', ')}]`;
  console.log(`Saving new readings to database: ${dataString}`);
  try {
    const db = await dbPromise;
    db.run('INSERT INTO data (ant_size, readings) VALUES (?, ?)', [1.76, dataString]);
    ctx.body = `Readings successfully saved to the database: ${dataString}`;
  } catch (err) {
    console.log(err);
  }
});

api.use(router.routes());
api.use(router.allowedMethods());

const port = 80 || process.env.PORT;
api.listen(port, () => {
  console.log(`Core API listening on port ${port}`);
});
