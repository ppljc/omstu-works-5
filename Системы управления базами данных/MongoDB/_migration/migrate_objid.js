// Перезаливка numismatics: без целочисленных id, связи — через ObjectId
const fs = require('fs');
const DIR = 'C:\\Users\\ppljc\\omstu-works-5\\Системы управления базами данных\\MongoDB\\_migration';
const dbx = db.getSiblingDB('numismatics');

function loadJson(name) {
  return JSON.parse(fs.readFileSync(DIR + '\\' + name + '.json', 'utf8'));
}

// Справочники: вставляем без своего целочисленного id, запоминаем маппинг oldId -> ObjectId
function insertRef(collName, idField) {
  const map = {};
  const docs = loadJson(collName).map(d => {
    const oldId = d[idField];
    delete d[idField];
    d._id = new ObjectId();
    map[oldId] = d._id;
    return d;
  });
  dbx.getCollection(collName).deleteMany({});
  if (docs.length) dbx.getCollection(collName).insertMany(docs);
  print(collName + ': ' + dbx.getCollection(collName).countDocuments());
  return map;
}

const alloyMap      = insertRef('alloys', 'alloy_id');
const conditionMap  = insertRef('conditions', 'condition_id');
const countryMap    = insertRef('countries', 'country_id');
const professionMap = insertRef('professions', 'profession_id');
const workplaceMap  = insertRef('workplaces', 'workplace_id');

// Коллекторы: ссылки на профессию и место работы -> ObjectId
const collectorMap = {};
const collectors = loadJson('collectors').map(d => {
  const oldId = d.collector_id;
  delete d.collector_id;
  d._id = new ObjectId();
  collectorMap[oldId] = d._id;
  if (d.collector_profession_id != null) d.collector_profession_id = professionMap[d.collector_profession_id] || null;
  if (d.collector_workplace_id != null) d.collector_workplace_id = workplaceMap[d.collector_workplace_id] || null;
  return d;
});
dbx.collectors.deleteMany({});
if (collectors.length) dbx.collectors.insertMany(collectors);
print('collectors: ' + dbx.collectors.countDocuments());

// Монеты: ссылки на страну и сплав -> ObjectId; встраиваем features и metadata
const features = {};
for (const row of loadJson('coin_features')) features[row.coin_id] = row.feature_list;
const metadata = {};
for (const row of loadJson('coin_metadata')) metadata[row.coin_id] = row.metadata;

const coinMap = {};
const coins = loadJson('coins').map(d => {
  const oldId = d.coin_id;
  coinMap[oldId] = new ObjectId();
  d._id = coinMap[oldId];
  delete d.coin_id;
  d.coin_country_id = countryMap[d.coin_country_id] || null;
  d.coin_alloy_id = alloyMap[d.coin_alloy_id] || null;
  if (features[oldId]) d.features = features[oldId];
  if (metadata[oldId]) d.metadata = metadata[oldId];
  return d;
});
dbx.coins.deleteMany({});
if (coins.length) dbx.coins.insertMany(coins);
print('coins: ' + dbx.coins.countDocuments());

// Коллекции: ссылки на коллекционера, монету и состояние -> ObjectId; дата -> Date
const collections = loadJson('collections').map(d => {
  d.collector_id = collectorMap[d.collector_id] || null;
  d.coin_id = coinMap[d.coin_id] || null;
  d.collection_condition_id = conditionMap[d.collection_condition_id] || null;
  if (d.collection_acquisition_date) d.collection_acquisition_date = new Date(d.collection_acquisition_date);
  return d;
});
dbx.collections.deleteMany({});
if (collections.length) dbx.collections.insertMany(collections);
print('collections: ' + dbx.collections.countDocuments());
