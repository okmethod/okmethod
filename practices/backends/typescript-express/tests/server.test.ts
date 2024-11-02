import request from "supertest";
import app from "../src/server";

describe("GET /api/heartbeat", () => {
  it("should return a heartbeat message", async () => {
    const res = await request(app).get("/api/heartbeat");
    expect(res.status).toBe(200);
    expect(res.body).toHaveProperty("alive");
    expect(typeof res.body.alive).toBe("string");
  });
});
