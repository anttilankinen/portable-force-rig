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
    const rows = await db.all('SELECT * FROM database');
    ctx.body = { rows: rows };
  } catch (err) {
    console.log(err);
  }
});

router.post('/data', bodyParser, async (ctx, next) => {
  let dataString = `[${ctx.request.body.data.join(', ')}]`;
  console.log(`Saving new readings to database: ${dataString}`);
  try {
    let now = new Date();
    const db = await dbPromise;
    db.run('INSERT INTO database (date_time, ant_size, readings) VALUES (?, ?, ?)', [now.toLocaleString(), 'Large', dataString]);
    ctx.body = `Readings successfully saved to the database: ${dataString}`;
  } catch (err) {
    console.log(err);
  }
});

api.use(router.routes());
api.use(router.allowedMethods());

const port = process.env.PORT || 80;
api.listen(port, () => {
  console.log(`Core API listening on port ${port}`);
});
