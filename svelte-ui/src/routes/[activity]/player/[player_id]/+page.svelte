<script lang="ts">
	import type { PlayerPage } from './+page';
	import { Card, DynamicData, TimePlot, GaussianPlot } from '$lib/components';
	import {
		currentActivityUrl,
		currentActivity,
		navTitle,
		activities,
		type Player,
		readJSONAPI
	} from '../../../../store';

	export let data: PlayerPage;
	const playerInfo = readJSONAPI<Player | null>(null, `/api/players/${data.player_id}/`);
	const skillHistory = readJSONAPI<{ datetime: number; skill: number }[] | null>(
		null,
		`/api/skill-history/${data.activity_url}/${data.player_id}/?select=skill,datetime`
	);
	const currentSkill = readJSONAPI<
		[{ datetime: number; skill: number; mu: number; sigma: number }] | null
	>(
		null,
		`/api/skill-history/${data.activity_url}/${data.player_id}/` +
			'?select=skill,mu,sigma,datetime&ordering=-datetime&limit=1'
	);

	currentActivityUrl.set(data.activity_url);

	$: if ($currentActivity) {
		navTitle.set($currentActivity.name);
	}
	$: skillPlotData = {
		x: $skillHistory ? $skillHistory.map((obj, idx) => idx) : [],
		y: $skillHistory ? $skillHistory.map((obj) => obj.skill) : []
	};
</script>

<svelte:head>
	{#if $currentActivity}
		<title>Rankings - {$navTitle}</title>
	{:else}
		<title>Rankings</title>
	{/if}
</svelte:head>

<DynamicData data={activities} />

{#if $currentActivity && $playerInfo}
	<Card
		class="w-full md:w-1/2 2xl:w-[calc(0.5*1536px)] flex flex-col items-center justify-center"
		style="tight"
	>
		<div class="text-xl font-semibold">🙂 {$playerInfo.name}</div>
		<div class="text-l text-gray-400">
			(<a href={`mailto:${$playerInfo.email}`}>{$playerInfo.email}</a>)
		</div>
	</Card>

	{#if skillPlotData}
		<TimePlot
			title="Skill progress"
			xAxisTitle="Matches played"
			yAxisTitle="Skill level"
			data={skillPlotData}
			initRangeX={[Math.max(skillPlotData.x.length - 30, 0), skillPlotData.x.length]}
			yRangeMinMax={[-2, null]}
		/>
	{/if}
	{#if $currentSkill && $currentSkill.length == 1}
		<GaussianPlot
			title="Current skill estimate"
			xAxisTitle="Skill level"
			yAxisTitle="Likelihood of actual skill (%)"
			mu={$currentSkill[0].mu}
			sigma={$currentSkill[0].sigma}
			limits={[0, 50]}
			verticalIndicators={[{ xPos: $currentSkill[0].skill, title: 'Skill value' }]}
		/>
	{/if}
{/if}
