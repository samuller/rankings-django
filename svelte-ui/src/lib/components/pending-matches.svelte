<script lang="ts">
	import { DynamicData, Table } from '.';
	import type { PageableAPIStore } from '$lib/api';
	import type { Matches } from '../../store';
	import type { CellDetail } from './table.svelte';

	export let matches: PageableAPIStore<Matches[]>;
	export let table: CellDetail[][];
	export let recent = false;
	export let validationLink: string = null;
</script>

<div class="w-full md:w-1/2 text-gray-700">
	<h2 class="text-2xl font-bold text-left">
		{recent ? 'Recent pending' : 'Pending'} match results
	</h2>
	{#if table.length > 0}
		<p class="text-left">
			{recent ? 'Recently reported' : 'Reported'} matches which are still pending
			{#if validationLink}
				<a data-sveltekit-reload href={validationLink}>validation</a>.
			{:else}
				validation.
			{/if}
		</p>
	{:else}
		<p class="text-left">There are no recent matches pending validation.</p>
	{/if}
</div>
<DynamicData data={matches} />
{#if table.length > 0}
	<Table
		columnNames={['Date', 'Team 1', 'Team 2', 'Submittor']}
		columnStyle={['text-center', 'text-center', 'text-center', 'text-center']}
		rows={table}
	/>
{/if}
