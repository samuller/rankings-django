<script lang="ts">
	import { page } from '$app/stores';
	import { AddButton, DynamicData, PagingNav, Table, type CellDetail } from '$lib/components';
	import {
		type Matches,
		apiMatches,
		apiPendingMatches,
	} from '../../../store';

	$: pageNr = parseInt($page.url.searchParams.get('page') ?? '1');

	let matchesTable: CellDetail[][] = [];
	$: matches = apiMatches($page.params.activity, pageNr, 10);
	$: matchesTable = convertMatchesToTable($matches);

	$: pendingMatches = apiPendingMatches($page.params.activity, pageNr, 10);
	$: pendingMatchesTable = convertMatchesToTable($pendingMatches, true);

	const convertMatchesToTable = function(matches: Matches[], pending=false) {
		const idCol = (match: Matches) => { return {
			text: match.id
		}};
		const dateCol = (match: Matches) => { return {
			text: new Date(match.datetime*1000).toISOString().replace('T', ' ').split('.')[0]
		}};
		const team1Col = (match: Matches) => { return {
			text: match.teams[0].members.map((member) => member.player.name).join(" & "),
			...((match.teams[0].id == match.games[0].winning_team) && { tooltip: "Winner!" }),
		}};
		const team2Col = (match: Matches) => { return {
			text: match.teams[1].members.map((member) => member.player.name).join(" & "),
			...((match.teams[1].id == match.games[0].winning_team) && { tooltip: "Winner!" }),
		}};
		const submittorCol = (match: Matches) => { return {
			text: match.submittor,
		}};
		return matches.map((match: Matches) => pending ? [
				dateCol(match),
				team1Col(match),
				team2Col(match),
				submittorCol(match),
			]: [
				idCol(match),
				dateCol(match),
				team1Col(match),
				team2Col(match),
		]);
	};

</script>

<div class="w-1/2 text-gray-700">
	<h2 class="text-2xl font-bold text-left">Pending match results</h2>
	<p class="text-left">Reported matches which are still pending validation.</p>
</div>
<DynamicData data={pendingMatches}></DynamicData>
{#if pendingMatchesTable.length > 0}
	<Table
		columnNames={['Date', 'Team 1', 'Team 2', 'Submittor']}
		columnAlignments={['text-center', 'text-center', 'text-center', 'text-center']}
		rows={pendingMatchesTable}
	></Table>
{/if}

<div class="w-1/2 text-gray-700">
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
