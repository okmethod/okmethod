import type { Request, Response } from "express";
import express from "express";

const app = express();
const port = 3000;

app.get("/", (req: Request, res: Response) => {
  console.log("req:", req);
  res.send("Hello World!");
});

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`);
});
