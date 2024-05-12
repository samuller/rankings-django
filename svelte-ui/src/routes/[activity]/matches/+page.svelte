<script lang="ts">
	import { page } from '$app/stores';
	import { DynamicData, PagingNav, PendingMatches, Table, type CellDetail } from '$lib/components';
	import { convertMatchesToTable } from '$lib/utils';
	import { apiMatches, apiPendingMatches } from '../../../store';

	$: pageNr = parseInt($page.url.searchParams.get('page') ?? '1');

	let matchesTable: CellDetail[][] = [];
	$: matches = apiMatches($page.params.activity, pageNr, 10);
	$: matchesTable = convertMatchesToTable($matches);

	$: pendingMatches = apiPendingMatches($page.params.activity);
	$: pendingMatchesTable = convertMatchesToTable($pendingMatches, true);
</script>

{#if pageNr == 1}
	<PendingMatches
		matches={pendingMatches}
		table={pendingMatchesTable}
		validationLink={`/admin/previous/gamesession/?activity__id__exact=${$page.params.activity}&validated__isnull=True`}
	/>
{/if}

<DynamicData data={matches} />
{#if matchesTable.length > 0}
	<div class="w-full md:w-1/2 text-gray-700">
		<h2 class="text-2xl font-bold text-left">Match history</h2>
		<p class="text-left">Reported matches which have been validated.</p>
	</div>
	<PagingNav {pageNr} pageable={matches} />
	<Table
		columnNames={['ID #', 'Date', 'Team 1', 'Team 2']}
		columnStyle={['text-center', 'text-center', 'text-center', 'text-center']}
		rows={matchesTable}
	/>
{:else}
	<div class="w-full md:w-1/2 text-gray-700">
		<h2 class="text-2xl font-bold text-left">Match history</h2>
		<p class="text-left">
			There are no matches that have been validated. Go to the
			<a href={`/${$page.params.activity}`} class="text-sky-500">summary page</a> to submit new matches.
		</p>
	</div>
{/if}
