<script lang="ts">
	import { page } from '$app/stores'
	import { DynamicData, Table, type RowDetail } from '$lib/components';
	import {
		type Ranking,
		apiRankings,
	} from '../../../store';

	let rankingsTable: RowDetail[][] = [];

	$: rankings = apiRankings[$page.params.activity];
	$: rankingsTable = $rankings
		.filter((ranking: Ranking) => ranking.skill > 0)
		.sort((rnkA: Ranking, rnkB: Ranking) => rnkA.player.name.localeCompare(rnkB.player.name))
		.map((ranking: Ranking) => [
			{ text: ranking.player.name, url: `/${$page.params.activity}/player/${ranking.player.id}` },
			{ text: ranking.skill.toFixed(0) }
		]);
</script>

<DynamicData data={rankings}></DynamicData>
{#if rankingsTable.length > 0}
<div class="w-full md:w-1/2 text-gray-700">
	<h2 class="text-2xl font-bold text-left">All players</h2>
	<p class="text-left">The current rankings according to the validated match history.</p>
</div>
<Table
	columnNames={['Name', 'Skill']}
	columnAlignments={['text-left', 'text-right']}
	rows={rankingsTable}
></Table>
{/if}
