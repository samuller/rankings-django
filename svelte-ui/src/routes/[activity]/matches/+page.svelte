<script lang="ts">
	import { page } from '$app/stores';
	import { AddButton, DynamicData, PagingNav, Table, type CellDetail } from '$lib/components';
	import {
		type Matches,
		apiMatches,
	} from '../../../store';

	$: pageNr = parseInt($page.url.searchParams.get('page') ?? '1');

	let matchesTable: CellDetail[][] = [];
	$: matches = apiMatches($page.params.activity, pageNr, 10);
	$: matchesTable = $matches
		.map((match: Matches) => [
			{ text: match.id },
			{ text: new Date(match.datetime*1000).toISOString().replace('T', ' ').split('.')[0]},
			{ text: match.teams[0].members.map((member) => member.player.name).join(" & ") },
			{ text: match.teams[1].members.map((member) => member.player.name).join(" & ") },
		]);
</script>

<PagingNav {pageNr} pageable={matches}></PagingNav>
<DynamicData data={matches}></DynamicData>
{#if matchesTable.length > 0}
	<Table
		columnNames={['ID #', 'Date', 'Team 1', 'Team 2']}
		columnAlignments={['text-center', 'text-center', 'text-center', 'text-center']}
		rows={matchesTable}
	></Table>
{/if}
