<script lang="ts">
	import { page } from '$app/stores'
	import { AddButton, DynamicData, Table, type CellDetail } from '$lib/components';
	import AddMatch from '$lib/components/add-match.svelte';
	import {
		type Ranking,
		apiRankings,
		players,
	} from '../../store';

	let rankingsTable: CellDetail[][] = [];
	let addMatchModal: HTMLDialogElement;

	$: rankings = apiRankings[$page.params.activity];
	$: rankingsTable = $rankings
		.filter((ranking: Ranking) => ranking.skill > 0)
		.map((ranking: Ranking) => [
			{ text: ranking.player.name, url: `/${$page.params.activity}/player/${ranking.player.id}` },
			{ text: ranking.skill.toFixed(0) }
		]);
	$: allPlayers = $players.map((player) => { return { id: player.id, name: player.name } });
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
<a href={`/${$page.params.activity}/players`} class="text-gray-700 text-2xl font-bold underline">View all players</a>
<a href={`/${$page.params.activity}/matches`} class="text-gray-700 text-2xl font-bold underline">View all matches</a>

<AddButton on:click={() => addMatchModal.showModal()}></AddButton>

<dialog bind:this={addMatchModal} class="modal">
  <div class="modal-box w-11/12 max-w-2xl">
    <form method="dialog">
		<button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
	</form>
	<AddMatch players={allPlayers}></AddMatch>
  </div>
  <form method="dialog" class="modal-backdrop">
    <button>close</button>
  </form>
</dialog>
