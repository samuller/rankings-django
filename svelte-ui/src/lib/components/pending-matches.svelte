<script lang="ts">
	import { DynamicData, Table } from ".";
	import type { Matches, PageableAPIStore } from "../../store";
	import type { CellDetail } from "./table.svelte";

	export let matches: PageableAPIStore<Matches[]>;
	export let table: CellDetail[][];
</script>

<div class="w-1/2 text-gray-700">
	<h2 class="text-2xl font-bold text-left">Pending match results</h2>
	<p class="text-left">Reported matches which are still pending validation.</p>
</div>
<DynamicData data={matches}></DynamicData>
{#if table.length > 0}
	<Table
		columnNames={['Date', 'Team 1', 'Team 2', 'Submittor']}
		columnAlignments={['text-center', 'text-center', 'text-center', 'text-center']}
		rows={table}
	></Table>
{/if}
