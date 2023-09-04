<script lang="ts">
	import type { ActivityPage } from "./+page";
	import Card from "$lib/card.svelte";
	import Table from "$lib/table.svelte";
	import TimePlot from "$lib/time-plot.svelte";
	import AddButton from "$lib/add-button.svelte";
	import { page_title, activities, type Activity, players, type Player, rankingsAPIStore, type Ranking } from '../../store';
	import DynamicData from "$lib/dynamic-data.svelte";

	export let data: ActivityPage;

	let rankings: any;
	let rankingsTable: string[][] = [];

	$: activity = $activities?.find((act: Activity) => act.url == data.url);
	$: if (activity) { page_title.set(activity.name); }
	$: if (activity) { rankings = rankingsAPIStore(activity.url); }
	$: if (rankings) { rankingsTable = $rankings
		.filter((ranking: any) => ranking.skill > 0)
		.map((ranking: any) => [ranking.player.name, ranking.skill.toFixed(0)]);
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

	<Table
		columnNames={['Name', 'Skill']}
		rows={rankingsTable}
	></Table>

	<TimePlot></TimePlot>

	<AddButton></AddButton>
{/if}
