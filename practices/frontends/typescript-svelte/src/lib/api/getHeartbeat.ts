import { constructRequestInit, fetchApi } from "$lib/utils/request";
import type { ResponseHeartbeatJson } from "$lib/types/heartbeat";

type supportedPrefix = "fastapi" | "express";

async function getHeartbeat(
  fetchFunction: typeof window.fetch,
  prefix: supportedPrefix,
): Promise<ResponseHeartbeatJson> {
  const url = `/${prefix}/heartbeat`;
  const requestInit = constructRequestInit();
  const requestConfig = {
    ...requestInit,
    method: "GET",
  };
  const response = await fetchApi(fetchFunction, url, requestConfig);
  return (await response.json()) as ResponseHeartbeatJson;
}

export const getFastapiHeartbeat = (fetchFunction: typeof window.fetch) => getHeartbeat(fetchFunction, "fastapi");
export const getExpressHeartbeat = (fetchFunction: typeof window.fetch) => getHeartbeat(fetchFunction, "express");
