<script lang="ts">
  import { page } from "$app/stores";
</script>

<div class="flex h-screen">
  <div class="m-auto text-center">
    <p class="text-4xl font-bold leading-loose tracking-wider">
      {$page.status}
      {$page.error?.message}
    </p>
  </div>
</div>
