<script lang="ts">
	import { page } from '$app/stores';
	import { Card, TimePlot, GaussianPlot, DynamicData } from '$lib/components';
	import { readJSONAPI, readJSONAPIList } from '$lib/api';
	import type { Player } from '../../../../store';

	const playerInfo = readJSONAPI<Player | null>(null, `/api/players/${$page.params.player_id}/`);
	const skillHistory = readJSONAPIList<{ datetime: number; skill: number }[] | null>(
		null,
		`/api/skill-history/${$page.params.activity}/${$page.params.player_id}/?select=skill,datetime`
	);
	const currentSkill = readJSONAPIList<
		[{ datetime: number; skill: number; mu: number; sigma: number }] | null
	>(
		null,
		`/api/skill-history/${$page.params.activity}/${$page.params.player_id}/` +
			'?select=skill,mu,sigma,datetime&ordering=-datetime&limit=1'
	);

	$: skillPlotData = {
		x: $skillHistory ? $skillHistory.map((obj, idx) => idx) : [],
		y: $skillHistory ? $skillHistory.map((obj) => obj.skill) : []
	};
</script>

<DynamicData data={playerInfo} />
{#if $playerInfo}
	<Card
		class="w-full md:w-1/2 2xl:w-[calc(0.5*1536px)] flex flex-col items-center justify-center"
		variant="tight"
	>
		<div class="text-xl font-semibold">🙂 {$playerInfo.name}</div>
		<div class="text-l text-gray-400">
			(<a href={`mailto:${$playerInfo.email}`}>{$playerInfo.email}</a>)
		</div>
	</Card>

	<div class="w-[110%] md:w-[90%]">
		{#if skillPlotData}
			<TimePlot
				title="Skill progress"
				xAxisTitle="Matches played"
				yAxisTitle="Skill level"
				data={skillPlotData}
				initRangeX={[Math.max(skillPlotData.x.length - 15, 0), skillPlotData.x.length]}
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
	</div>
{/if}
