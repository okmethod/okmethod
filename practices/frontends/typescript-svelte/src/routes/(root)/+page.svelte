<script lang="ts">
  import { getFastapiHeartbeat, getExpressHeartbeat, getGinHeartbeat } from "$lib/api/getHeartbeat";
  import type { ResponseHeartbeatJson } from "$lib/types/heartbeat";

  let fastapiResponse: ResponseHeartbeatJson | null = null;
  async function handleFastapiHeartbeat(): Promise<void> {
    fastapiResponse = await getFastapiHeartbeat(window.fetch);
  }

  let expressResponse: ResponseHeartbeatJson | null = null;
  async function handleExpressHeartbeat(): Promise<void> {
    expressResponse = await getExpressHeartbeat(window.fetch);
  }

  let ginResponse: ResponseHeartbeatJson | null = null;
  async function handleGinHeartbeat(): Promise<void> {
    ginResponse = await getGinHeartbeat(window.fetch);
  }
</script>

<div class="h-full my-4 mx-auto flex justify-center">
  <div class="space-y-5">
    <h1 class="h1">Let's get cracking bones!</h1>
    <div class="w-[600px] flex flex-col space-y-4 mx-4">
      <div class="flex items-center space-x-4">
        <button type="button" class="btn variant-filled" on:click={handleFastapiHeartbeat}> Call FastAPI </button>
        <p>Response: {fastapiResponse ? fastapiResponse.alive : "Nothing"}</p>
      </div>
      <div class="flex items-center space-x-4">
        <button type="button" class="btn variant-filled" on:click={handleExpressHeartbeat}> Call Express </button>
        <p>Response: {expressResponse ? expressResponse.alive : "Nothing"}</p>
      </div>
      <div class="flex items-center space-x-4">
        <button type="button" class="btn variant-filled" on:click={handleGinHeartbeat}> Call Gin </button>
        <p>Response: {ginResponse ? ginResponse.alive : "Nothing"}</p>
      </div>
    </div>
  </div>
</div>
