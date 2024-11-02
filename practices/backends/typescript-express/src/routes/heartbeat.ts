import type { Request, Response } from "express";
import type { HeartbeatResponse } from "src/types/heartbeat";

const heartbeat = async (req: Request, res: Response) => {
  console.log("req:", req.body);
  const now = new Date();
  const response: HeartbeatResponse = {
    alive: now.toISOString(),
  };
  res.json(response);
};

export default heartbeat;
