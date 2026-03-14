try {
  rs.status();
  print("shard2RS is already initialized");
} catch (error) {
  rs.initiate({
    _id: "shard2RS",
    members: [{ _id: 0, host: "shard2:27018" }]
  });
  print("shard2RS initiated");
}
