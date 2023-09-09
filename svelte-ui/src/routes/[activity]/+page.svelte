<script lang="ts">
	import type { ActivityPage } from './+page';
	import { AddButton, DynamicData, Table, type RowDetail } from '$lib/components';
	import {
		type Ranking,
		apiRankings,
	} from '../../store';

	export let data: ActivityPage;

	let rankingsTable: RowDetail[][] = [];

	$: rankings = apiRankings[data.activity_url];
	$: rankingsTable = $rankings
		.filter((ranking: Ranking) => ranking.skill > 0)
		.map((ranking: Ranking) => [
			{ text: ranking.player.name, url: `/${data.activity_url}/player/${ranking.player.id}` },
			{ text: ranking.skill.toFixed(0) }
		]);
</script>

<DynamicData data={rankings}></DynamicData>
{#if rankingsTable.length > 0}
<div class="w-full md:w-1/2 text-gray-700">
	<h2 class="text-2xl font-bold text-left">Top players</h2>
	<p class="text-left">The currently top ranked active players according to the validated match history.</p>
</div>
<Table
	columnNames={['Name', 'Skill']}
	columnAlignments={['text-left', 'text-right']}
	rows={rankingsTable.slice(0, 5)}
></Table>
{/if}
<a href={`/${data.activity_url}/matches`} class="text-gray-700 text-2xl font-bold underline">View all matches</a>

<AddButton></AddButton>
