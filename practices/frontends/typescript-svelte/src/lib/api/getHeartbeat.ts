import { constructRequestInit, fetchApi } from "$lib/utils/request";
import type { ResponseHeartbeatJson } from "$lib/types/heartbeat";

export async function getFastapiHeartbeat(fetchFunction: typeof window.fetch): Promise<ResponseHeartbeatJson> {
  const url = "/fastapi/heartbeat";
  const requestInit = constructRequestInit();
  const requestConfig = {
    ...requestInit,
    method: "GET",
  };
  const response = await fetchApi(fetchFunction, url, requestConfig);
  return (await response.json()) as ResponseHeartbeatJson;
}

export async function getExpressHeartbeat(fetchFunction: typeof window.fetch): Promise<ResponseHeartbeatJson> {
  const url = "/express/heartbeat";
  const requestInit = constructRequestInit();
  const requestConfig = {
    ...requestInit,
    method: "GET",
  };
  const response = await fetchApi(fetchFunction, url, requestConfig);
  return (await response.json()) as ResponseHeartbeatJson;
}
