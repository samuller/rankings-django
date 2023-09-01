<script lang="ts">
	import { page_title, activities } from '../store';
	import Card from "$lib/card.svelte";
	import Loader from "$lib/loader.svelte";

	page_title.set("");

	let test_data = [
		{ title: '⚽ Foosball', url: 'foosball' },
		{ title: '🏓 Table tennis', url: 'table_tennis' },
		{ title: '🏆 Table Tennis Tournament 2022', url: 'table_tennis_tournament_2022' }
	];
</script>

{#await activities.load()}
	<Loader></Loader>
{/await}

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
