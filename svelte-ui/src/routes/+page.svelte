<script lang="ts">
	import { navTitle, activities } from '../store';
	import { Card, DynamicData } from "$lib/components";

	navTitle.set("");
</script>

<!-- We don't put this in +layout as it shouldn't be inherited. -->
<svelte:head>
    <title>Rankings</title> 
</svelte:head>

<DynamicData data={activities} let:data={loaded}>
	{#if loaded.length == 0}
	<div class="text-black text-center">
		<h4>Currently there are no activities.</h4>
		<p>You can go to <a data-sveltekit-reload href="/admin/">admin tools</a> to add some.</p>
	</div>
	{/if}
</DynamicData>

{#each $activities ?? [] as activity}
	<a href="/{activity.url}">
		<Card class="w-96 md:w-[600px] hover:bg-sky-500 hover:ring-sky-500 flex justify-center" style="tight">
				<span class="text-white group-hover:[text-shadow:_0_0_3px_blue] text-2xl">{activity.name}</span>
		</Card>
	</a>
{/each}

<style lang="postcss">
	:global(html) {
		/* background-color: theme(colors.gray.100); */
	}
</style>
