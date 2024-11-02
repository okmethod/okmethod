import "tsconfig-paths/register";
import express from "express";
import heartbeat from "src/routes/heartbeat";

const app = express();
const port = 3000;

app.get("/api/heartbeat", heartbeat);

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
