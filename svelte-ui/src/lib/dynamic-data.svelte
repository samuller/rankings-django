<!--
  @component
  Component that shows spinner while loading (asyncReadable) data and handles showing errors on failure. 

  Usage:
  ```tsx
  <DynamicData data={reloadableData}></DynamicData>
  ```
-->
<script context="module" lang="ts">
    export interface Reloadable<T> {
        load(): Promise<T>;
        reload?(): Promise<T>;
    }
</script>

<script lang="ts">
	import Loader from "$lib/loader.svelte";
	import TextButton from '$lib/text-button.svelte';

    // Reloadable data, most likely a asyncReadable from @square/svelte-store.
    export let data: Reloadable<any>;
    export const retry = true;

	let dataLoadPromise = data.load();
	function reload() {
		if (data.reload) {
			dataLoadPromise = data.reload();
		}
	}
</script>

{#await dataLoadPromise}
	<Loader></Loader>
{:catch error}
    <div class="flex flex-col">
        <p class="text-red-500">{error.message}</p>
        {#if retry}
        <button class="btn btn-outline btn-error" on:click={reload}>Retry</button>
        {/if}
    </div>
{/await}
