import "tsconfig-paths/register";
import express from "express";
import heartbeat from "src/routes/heartbeat";

const app = express();
const port = 3000;

app.get("/api/heartbeat", heartbeat);

const startServer = () => {
  app.listen(port, () => {
    console.log(`Example app listening on port ${port}`);
  });
};

if (process.env.NODE_ENV !== "test") {
  startServer(); // テスト環境ではサーバーを起動しない
}

export default app;
