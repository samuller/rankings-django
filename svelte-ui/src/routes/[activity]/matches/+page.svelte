<script lang="ts">
	import { page } from '$app/stores';
	import { DynamicData, PagingNav, PendingMatches, Table, type CellDetail } from '$lib/components';
	import { convertMatchesToTable } from '$lib/utils';
	import {
		apiMatches,
		apiPendingMatches,
	} from '../../../store';

	$: pageNr = parseInt($page.url.searchParams.get('page') ?? '1');

	let matchesTable: CellDetail[][] = [];
	$: matches = apiMatches($page.params.activity, pageNr, 10);
	$: matchesTable = convertMatchesToTable($matches);

	$: pendingMatches = apiPendingMatches($page.params.activity);
	$: pendingMatchesTable = convertMatchesToTable($pendingMatches, true);
</script>

{#if pageNr == 1}
<PendingMatches matches={pendingMatches} table={pendingMatchesTable}></PendingMatches>
{/if}

<div class="w-full md:w-1/2 text-gray-700">
	<h2 class="text-2xl font-bold text-left">Match history</h2>
	<p class="text-left">Reported matches which have been validated.</p>
</div>
<PagingNav {pageNr} pageable={matches}></PagingNav>
<DynamicData data={matches}></DynamicData>
{#if matchesTable.length > 0}
	<Table
		columnNames={['ID #', 'Date', 'Team 1', 'Team 2']}
		columnAlignments={['text-center', 'text-center', 'text-center', 'text-center']}
		rows={matchesTable}
	></Table>
{/if}
