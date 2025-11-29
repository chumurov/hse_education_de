// Initialization script for MongoDB to create an app user and optionally seed data
// This file is evaluated at container init time by the official MongoDB image

const dbName = process.env.MONGO_INITDB_DATABASE || 'appdb';
const appUser = process.env.MONGO_APP_USERNAME || 'appuser';
const appPass = process.env.MONGO_APP_PASSWORD || 'apppassword';

print(`Initializing database: ${dbName}`);

const adminDB = db.getSiblingDB(dbName);

try {
  adminDB.createUser({
    user: appUser,
    pwd: appPass,
    roles: [ { role: 'readWrite', db: dbName } ]
  });
  print(`Created user ${appUser} with readWrite on ${dbName}`);
} catch (e) {
  print('User creation failed (maybe user already exists): ' + e);
}

// Optionally add sample data
// const col = adminDB.getCollection('items');
// col.insertMany([{name: 'item1'}, {name: 'item2'}]);
