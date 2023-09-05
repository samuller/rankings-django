<script lang="ts">
	import type { ActivityPage } from './+page';
	import { AddButton, Card, DynamicData, Table, type RowDetail } from '$lib/components';
	import {
		currentActivityUrl,
		currentActivity,
		navTitle,
		activities,
		type Ranking,
		apiRankings,
	} from '../../store';

	export let data: ActivityPage;

	let rankingsTable: RowDetail[][] = [];
	currentActivityUrl.set(data.activity_url);

	$: if ($currentActivity) { navTitle.set($currentActivity.name); }
	$: rankings = apiRankings[data.activity_url];
	$: rankingsTable = $rankings
		.filter((ranking: Ranking) => ranking.skill > 0)
		.map((ranking: Ranking) => [
			{ text: ranking.player.name, url: `/${data.activity_url}/player/${ranking.player.id}` },
			{ text: ranking.skill.toFixed(0) }
		]);
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
		<span class="normal-case text-xl font-semibold">{$currentActivity.name}</span>
	</Card>

	<DynamicData data={rankings}></DynamicData>
	{#if rankingsTable.length > 0}
	<Table
		columnNames={['Name', 'Skill']}
		rows={rankingsTable.slice(0, 5)}
	></Table>
	{/if}

	<AddButton></AddButton>
{/if}
