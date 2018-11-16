const Router = require('koa-router');
const Koa = require('koa');
const router = new Router();
const api = new Koa();

const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('./data/readings.sqlite');

router.get('/api/data', (ctx, next) => {
 ctx.body = 'Welcome to the Portable Force Rig Core API!';
});

router.post('/api/data', (ctx, next) => {
 ctx.body = 'Saving to the SQLite store..';
});

api.use(router.routes());
api.use(router.allowedMethods());

const port = 80 || process.env.PORT;
api.listen(port, () => {
  console.log(`Core API listening on port ${port}`);
});
