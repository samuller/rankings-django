<script lang="ts">
	import type { ActivityPage } from './+page';
	import Card from '$lib/card.svelte';
	import Table from '$lib/table.svelte';
	import TimePlot from '$lib/time-plot.svelte';
	import AddButton from '$lib/add-button.svelte';
	import DynamicData from '$lib/dynamic-data.svelte';
	import {
		currentActivityUrl,
		currentActivity,
		navTitle,
		activities,
		type Activity,
		players,
		type Player,
		rankingsAPIStore,
		type Ranking
	} from '../../store';

	export let data: ActivityPage;
	currentActivityUrl.set(data.url);

	let rankings = rankingsAPIStore(data.url);
	let rankingsTable: string[][] = [];

	$: navTitle.set($currentActivity?.name);
	$: rankingsTable = $rankings
		.filter((ranking: any) => ranking.skill > 0)
		.map((ranking: any) => [ranking.player.name, ranking.skill.toFixed(0)]);
</script>

<svelte:head>
{#if $currentActivity}
	<title>Rankings - {$navTitle}</title>
{:else}
	<title>Rankings</title>
{/if}
</svelte:head>

<DynamicData data={activities}></DynamicData>

{#if $currentActivity}
	<Card class="w-1/2 2xl:w-[calc(0.5*1536px)] flex justify-center" style="tight">
		<a class="normal-case text-xl font-semibold">{$currentActivity.name}</a>
	</Card>

	<Table
		columnNames={['Name', 'Skill']}
		rows={rankingsTable}
	></Table>

	<TimePlot></TimePlot>

	<AddButton></AddButton>
{/if}
