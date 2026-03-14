const dbName = process.env.MONGO_INITDB_DATABASE || "appdb";
const adminDB = db.getSiblingDB("admin");
const appDB = db.getSiblingDB(dbName);

const addShardIfMissing = (shardName, connectionString) => {
  const shards = adminDB.runCommand({ listShards: 1 }).shards || [];
  const exists = shards.some((shard) => shard._id === shardName);
  if (exists) {
    print(`Shard ${shardName} already added`);
    return;
  }

  printjson(sh.addShard(connectionString));
};

addShardIfMissing("shard1RS", "shard1RS/shard1:27018");
addShardIfMissing("shard2RS", "shard2RS/shard2:27018");

printjson(sh.enableSharding(dbName));

appDB.grades.createIndex({ studentId: 1 });

const metadata = db.getSiblingDB("config").collections.findOne({ _id: `${dbName}.grades` });
const alreadySharded = Boolean(metadata && metadata.key);

if (!alreadySharded) {
  printjson(sh.shardCollection(`${dbName}.grades`, { studentId: 1 }));
} else {
  print(`${dbName}.grades is already sharded`);
}
