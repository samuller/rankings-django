<script lang="ts">
	import { page } from '$app/stores';
	import { DynamicData, Table, type CellDetail } from '$lib/components';
	import { sortAsNumber } from '$lib/utils';
	import { type Ranking, apiRankings } from '../../../store';

	let rankingsTable: CellDetail[][] = [];
	let sortingColumnIdx: number | null = 0;

	const updateSorting = function (event) {
		const colIdx = event.detail;
		sortingColumnIdx = colIdx;
	};

	$: rankings = apiRankings[$page.params.activity];
	$: rankingsTable = $rankings
		.filter((ranking: Ranking) => ranking.skill > 0)
		.map((ranking: Ranking) => [
			{ text: ranking.player.name, url: `/${$page.params.activity}/player/${ranking.player.id}` },
			{ text: ranking.skill.toFixed(0) }
		]);
	$: {
		rankingsTable.sort((rowA: CellDetail[], rowB: CellDetail[]) => {
			// Return 0 if values are considered equal (don't change sorting order).
			if (sortingColumnIdx === null) return 0;
			const [valueA, valueB] = [rowA[sortingColumnIdx].text, rowB[sortingColumnIdx].text];
			const numOrder = sortAsNumber(valueA, valueB);
			if (numOrder !== null) {
				// Invert sort order to show high numbers (rankings) first.
				return -numOrder;
			}
			return valueA.localeCompare(valueB);
		});
		rankingsTable = rankingsTable;
	}
</script>

<DynamicData data={rankings} />
{#if rankingsTable.length > 0}
	<div class="w-full md:w-1/2 text-gray-700">
		<h2 class="text-2xl font-bold text-left">All players</h2>
		<p class="text-left">The current rankings according to the validated match history.</p>
	</div>
	<!-- We add 'underline' style to headers to indicate they are clickable for sorting. -->
	<Table
		columnNames={['Name', 'Skill']}
		columnStyle={['text-left', 'text-right']}
		columnHeaderStyle={['underline', 'underline']}
		rows={rankingsTable}
		on:click-column-header={(event) => updateSorting(event)}
	/>
{/if}
