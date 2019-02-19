const Router = require('koa-router');
const Koa = require('koa');
const bodyParser = require('koa-body')();
const router = new Router();
const api = new Koa();
const uuidv4 = require('uuid/v4');

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

router.get('/data/:id', async (ctx, next) => {
  try {
    const db = await dbPromise;
    const row = await db.all(`SELECT * FROM database WHERE id = "${ctx.params.id}"`);
    ctx.body = { row: row };
  } catch(err) {
    console.log(err);
  }
});

router.post('/data', bodyParser, async (ctx, next) => {
  const id = ctx.request.body.id;
  const fileName = `${id}.mp4`;
  const dataString = `[${ctx.request.body.data.join(', ')}]`;
  console.log(`Saving new readings to database: ${dataString}`);
  try {
    let now = new Date();
    const db = await dbPromise;
    db.run('INSERT INTO database (id, date_time, ant_size, readings, file_name) VALUES (?, ?, ?, ?, ?)', [id, now.toLocaleString(), 'Large', dataString, fileName]);
    ctx.body = `Readings successfully saved to the database: ${dataString}`;
  } catch (err) {
    console.log(err);
  }
});

router.del('/data/:id/delete', async (ctx, next) => {
  try {
    const db = await dbPromise;
    db.run('DELETE FROM database WHERE id = ?', ctx.params.id, (err) => {
      if (err) return console.error(err.message);
    });
    const rows = await db.all('SELECT * FROM database');
    ctx.body = { rows: rows };
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
