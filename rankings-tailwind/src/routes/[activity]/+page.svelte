<script lang="ts">
	import type { ActivityPage } from "./+page";
	import Card from "$lib/card.svelte";
	import Table from "$lib/table.svelte";
	import TimePlot from "$lib/time-plot.svelte";
	import AddButton from "$lib/add-button.svelte";
	import { page_title, activities } from '../../store';
	import Loader from "$lib/loader.svelte";

	export let data: ActivityPage;

	$: activity = $activities?.find((act) => act.url == data.url);
	$: if (activity) {
		page_title.set(activity.name);
	}
</script>


{#await activities.load()}
	<Loader></Loader>
{:then value}
	<Card class="w-1/2 2xl:w-[calc(0.5*1536px)] flex justify-center" style="tight">
		<a class="normal-case text-xl font-semibold">{activity?.name}</a>
	</Card>

	<Table></Table>

	<TimePlot></TimePlot>

	<AddButton></AddButton>
{/await}
