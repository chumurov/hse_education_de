const dbName = process.env.MONGO_INITDB_DATABASE || "appdb";
const namespace = `${dbName}.grades`;
const appDB = db.getSiblingDB(dbName);

const total = appDB.grades.countDocuments({});
if (total < 2) {
  print("Not enough grade documents to rebalance chunks");
  quit(0);
}

const splitCandidate = appDB.grades
  .find({}, { studentId: 1, _id: 0 })
  .sort({ studentId: 1 })
  .skip(Math.floor(total / 2))
  .limit(1)
  .next();

if (!splitCandidate || !splitCandidate.studentId) {
  print("Could not determine a split point for grades");
  quit(0);
}

const middle = { studentId: splitCandidate.studentId };

try {
  printjson(sh.splitAt(namespace, middle));
} catch (error) {
  print(`splitAt skipped: ${error}`);
}

try {
  printjson(sh.moveChunk(namespace, middle, "shard2RS"));
} catch (error) {
  print(`moveChunk skipped: ${error}`);
}
