<script lang="ts">
	import { page } from '$app/stores';
	import { SvelteToast, toast } from '@zerodevx/svelte-toast';
	import { AddButton, DynamicData, Table, type CellDetail, PendingMatches } from '$lib/components';
	import { convertMatchesToTable } from '$lib/utils';
	import AddMatch from '$lib/components/add-match.svelte';
	import {
		type Ranking,
		apiRankings,
		players,
		currentActivityUrl,
		apiPendingMatches
	} from '../../store';
	import TextButton from '$lib/components/text-button.svelte';

	const dialogToastStyle = {
		reversed: true,
		intro: { y: 192 },
		duration: 10000,
		pausable: true
	};

	let rankingsTable: CellDetail[][] = [];
	let addMatchModal: HTMLDialogElement;

	$: rankings = apiRankings[$page.params.activity];
	$: rankingsTable = $rankings
		.filter((ranking: Ranking) => ranking.skill > 0)
		.map((ranking: Ranking) => [
			{ text: ranking.player.name, url: `/${$page.params.activity}/player/${ranking.player.id}` },
			{ text: ranking.skill.toFixed(0) }
		]);
	$: allPlayers = $players.map((player) => {
		return { id: player.id, name: player.name };
	});

	const onSubmitNewMatch = function (event) {
		const data: { gameCount: number } = event.detail;
		addMatchModal.close();
		// Refresh data that's now changed.
		apiPendingMatches($page.params.activity).reload();
		let msg = 'Matches submitted!';
		if (data.gameCount) {
			msg = data.gameCount == 1 ? 'Match submitted!' : `${data.gameCount} matches submitted!`;
		}
		toast.push(msg, { classes: ['toast-as-success'] });
	};
	const onSubmitNewMatchError = function (err: any) {
		const errorMsg = `${err.statusText} (${err.status})`;
		toast.push(`Failed to submit match. <strong>Error:</strong> ${errorMsg}`, {
			classes: ['toast-as-error'],
			initial: 0
		});
	};

	$: pendingMatches = apiPendingMatches($page.params.activity);
	$: pendingMatchesTable = convertMatchesToTable($pendingMatches, true).slice(0, 5);
</script>

<DynamicData data={rankings} />
{#if rankingsTable.length > 0}
	<div class="w-full md:w-1/2 text-gray-700">
		<h2 class="text-2xl font-bold text-left">Top players</h2>
		<p class="text-left">
			The currently top ranked active players according to the validated match history.
		</p>
	</div>
	<Table
		columnNames={['Name', 'Skill']}
		columnStyle={['text-left', 'text-right']}
		rows={rankingsTable.slice(0, 5)}
	/>
	<a href={`/${$page.params.activity}/players`} class="text-gray-700 text-2xl font-bold underline"
		>View all players</a
	>
{:else}
	<div class="w-full md:w-1/2 text-gray-700">
		<h2 class="text-2xl font-bold text-left">Top players</h2>
		<p class="text-left">
			No ranked active players have been found - submit and validate some
			<TextButton on:click={() => addMatchModal.showModal()}><span>new matches</span></TextButton>.
		</p>
	</div>
{/if}

<PendingMatches recent={true} matches={pendingMatches} table={pendingMatchesTable} />
<a href={`/${$page.params.activity}/matches`} class="text-gray-700 text-2xl font-bold underline"
	>View all matches</a
>

<AddButton on:click={() => addMatchModal.showModal()} />

<dialog bind:this={addMatchModal} class="modal">
	<div class="modal-box w-11/12 max-w-2xl">
		<form method="dialog">
			<button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
		</form>
		{#if $currentActivityUrl != null}
			<AddMatch
				currentActivity={$currentActivityUrl}
				players={allPlayers}
				on:submit={onSubmitNewMatch}
				on:error={onSubmitNewMatchError}
			/>
		{/if}
	</div>
	<form method="dialog" class="modal-backdrop">
		<button>close</button>
	</form>
	<!--
	In addition to the global toast display, we add another one here (in <dialog>) so that it'll be
	included in the "top layer" and will display over the dialog modal.
	See: https://stackoverflow.com/questions/77099074/layering-toast-alerts-above-dialog-modal
  -->
	<SvelteToast options={dialogToastStyle} />
</dialog>
