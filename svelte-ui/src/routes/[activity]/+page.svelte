<script lang="ts">
	import type { ActivityPage } from "./+page";
	import Card from "$lib/card.svelte";
	import Table from "$lib/table.svelte";
	import TimePlot from "$lib/time-plot.svelte";
	import AddButton from "$lib/add-button.svelte";
	import { page_title, activities, type Activity } from '../../store';
	import DynamicData from "$lib/dynamic-data.svelte";

	export let data: ActivityPage;

	$: activity = $activities?.find((act: Activity) => act.url == data.url);
	$: if (activity) {
		page_title.set(activity.name);
	}
</script>

<svelte:head>
{#if activity}
	<title>Rankings - {activity.name}</title>
{:else}
	<title>Rankings</title>
{/if}
</svelte:head>

<DynamicData data={activities}></DynamicData>

{#if activity}
	<Card class="w-1/2 2xl:w-[calc(0.5*1536px)] flex justify-center" style="tight">
		<a class="normal-case text-xl font-semibold">{activity.name}</a>
	</Card>

	<Table></Table>

	<TimePlot></TimePlot>

	<AddButton></AddButton>
{/if}
