<script lang="ts">
	import { page } from '$app/stores';
	import { DynamicData, Table, type CellDetail } from '$lib/components';
	import { convertMatchesToTable } from '$lib/utils';
	import { apiSingleMatch } from '../../../../store';

	$: paramId = parseInt($page.params.id) ?? null;

	let matchesTable: CellDetail[][] = [];
	$: match = apiSingleMatch($page.params.activity, paramId ?? 0);
	$: matchesTable = convertMatchesToTable($match ? [$match] : []);
</script>

<DynamicData data={match} />
{#if paramId !== null && $match !== null}
	<div class="w-full md:w-1/2 text-gray-700">
		<h2 class="text-2xl font-bold text-left">Match history</h2>
		<p class="text-left">Reported matches which have been validated.</p>
	</div>
	<Table
		columnNames={['ID #', 'Date', 'Team 1', 'Team 2']}
		columnStyle={['text-center', 'text-center', 'text-center', 'text-center']}
		rows={matchesTable}
	/>
{/if}
