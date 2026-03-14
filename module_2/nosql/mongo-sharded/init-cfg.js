try {
  rs.status();
  print("cfgRS is already initialized");
} catch (error) {
  rs.initiate({
    _id: "cfgRS",
    configsvr: true,
    members: [
      { _id: 0, host: "cfg1:27019" },
      { _id: 1, host: "cfg2:27019" },
      { _id: 2, host: "cfg3:27019" }
    ]
  });
  print("cfgRS initiated");
}
