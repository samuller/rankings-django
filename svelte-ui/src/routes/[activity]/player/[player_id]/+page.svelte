<script lang="ts">
	import type { PlayerPage } from './+page';
	import { Card, DynamicData, TimePlot } from '$lib/components';
	import {
		currentActivityUrl,
		currentActivity,
		navTitle,
		activities,
		type Player,
		readJSONAPI,
	} from '../../../../store';

	export let data: PlayerPage;
	const playerInfo = readJSONAPI<Player | null>(null, `/api/players/${data.player_id}/`);
	const skillHistory = readJSONAPI<{ datetime: number, skill: number }[] | null>(null,
		`/api/skill-history/${data.activity_url}/${data.player_id}/?select=skill,datetime`
	);

	currentActivityUrl.set(data.activity_url);

	$: if ($currentActivity) { navTitle.set($currentActivity.name); }
	$: plotData = {
		x: $skillHistory ? $skillHistory.map((obj, idx) => idx) : [],
		y: $skillHistory ? $skillHistory.map((obj) => obj.skill) : [],
	};
</script>

<svelte:head>
{#if $currentActivity}
	<title>Rankings - {$navTitle}</title>
{:else}
	<title>Rankings</title>
{/if}
</svelte:head>

<DynamicData data={activities}></DynamicData>

{#if $currentActivity && $playerInfo}
	<Card class="w-1/2 2xl:w-[calc(0.5*1536px)] flex flex-col items-center justify-center" style="tight">
		<div class="text-xl font-semibold">🙂 {$playerInfo.name}</div>
		<div class="text-l text-gray-400">
			(<a href={`mailto:${$playerInfo.email}`}>{$playerInfo.email}</a>)
		</div>
	</Card>

	<TimePlot
		title="Skill progress"
		xAxisTitle="Matches played"
		yAxisTitle="Skill level"
		data={plotData}
	></TimePlot>
	<!-- <GaussianPlot
		title="Current skill estimate"
		xAxisTitle="Skill level"
		yAxisTitle="Likelihood of actual skill (%)"
	></GaussianPlot> -->
{/if}
