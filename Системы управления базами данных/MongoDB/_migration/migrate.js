// Миграция данных из PostgreSQL (экспортированные JSON) в MongoDB numismatics
const fs = require('fs');
const DIR = 'C:\\Users\\ppljc\\omstu-works-5\\Системы управления базами данных\\MongoDB\\_migration';
const dbx = db.getSiblingDB('numismatics');

function loadJson(name) {
  return JSON.parse(fs.readFileSync(DIR + '\\' + name + '.json', 'utf8'));
}

// --- Справочники и простые таблицы: перенос 1:1 ---
const simple = ['alloys', 'conditions', 'countries', 'professions', 'workplaces', 'collectors'];
for (const coll of simple) {
  const docs = loadJson(coll);
  dbx.getCollection(coll).deleteMany({});
  if (docs.length) dbx.getCollection(coll).insertMany(docs);
  print(coll + ': ' + dbx.getCollection(coll).countDocuments());
}

// --- Монеты: встраиваем feature_list (coin_features) и metadata (coin_metadata) ---
const features = {};
for (const row of loadJson('coin_features')) features[row.coin_id] = row.feature_list;
const metadata = {};
for (const row of loadJson('coin_metadata')) metadata[row.coin_id] = row.metadata;

const coins = loadJson('coins').map(c => {
  if (features[c.coin_id]) c.features = features[c.coin_id];
  if (metadata[c.coin_id]) c.metadata = metadata[c.coin_id];
  return c;
});
dbx.coins.deleteMany({});
if (coins.length) dbx.coins.insertMany(coins);
print('coins: ' + dbx.coins.countDocuments());

// --- Коллекции: дату приводим к типу Date ---
const collections = loadJson('collections').map(c => {
  if (c.collection_acquisition_date) c.collection_acquisition_date = new Date(c.collection_acquisition_date);
  return c;
});
dbx.collections.deleteMany({});
if (collections.length) dbx.collections.insertMany(collections);
print('collections: ' + dbx.collections.countDocuments());
