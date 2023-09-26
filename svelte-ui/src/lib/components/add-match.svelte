<script lang="ts">
	import { createEventDispatcher } from 'svelte';
	import Tabs from './tabs.svelte';

	interface Player {
		name: string;
		id: number;
	}

	const dispatch = createEventDispatcher();
	const teamNames = ['Team 1', 'Team 2'];
	const defaultNames = [
		['Player 1', 'Player 2'],
		['Player 3', 'Player 4']
	];

	export let currentActivity: string;
	// Full list of all known possible players.
	export let players: Player[] = [];

	let selectedMemberIds = [
		[0, 0],
		[0, 0]
	];
	$: selectedPlayers = selectedMemberIds
		.flat()
		.filter((id) => id != 0)
		.map((id) => {
			return players.find((player) => player.id == id);
		}) as Player[];
	$: validMemberSelection = selectedMemberIds[0][0] != 0 && selectedMemberIds[1][0] != 0;

	/**
	 * State and functions for multiple match selection.
	 */
	let multiMatchList: HTMLSelectElement;
	let multiMatchWins: number[] = [];

	const isSelected = function (playerId: number) {
		if (playerId == 0) return false;
		return selectedMemberIds.flat().includes(playerId);
	};

	const addMultiMatchResult = function (teamNr: number) {
		multiMatchWins = [...multiMatchWins, teamNr];
	};

	const removeSelectedMultiMatches = function () {
		// Loop backwards so that indexes aren't changed after each remove.
		for (let idx = multiMatchList.selectedOptions.length - 1; idx >= 0; idx--) {
			const selected = multiMatchList.selectedOptions[idx];
			multiMatchWins.splice(parseInt(selected.value), 1);
		}
		// Indicate variable has changed to trigger updates.
		multiMatchWins = multiMatchWins;
	};

	/**
	 * State and functions for round-robin selection.
	 */
	let roundRobinWinPlayer = 0;
	let roundRobinLosePlayer = 0;
	$: roundRobinSelected = roundRobinWinPlayer != 0 || roundRobinLosePlayer != 0;

	const resetRoundRobinSelect = function () {
		roundRobinWinPlayer = 0;
		roundRobinLosePlayer = 0;
	};

	/**
	 * State and functions for submitting matches.
	 */
	$: singleSubmitDisabledReason = !validMemberSelection ? 'Select players in teams' : '';
	$: multiSubmitDisabledReason = !validMemberSelection
		? 'Select players in teams'
		: multiMatchWins.length == 0
		? 'Add match results'
		: '';
	$: roundRobinSubmitDisabledReason =
		selectedPlayers.length != 4
			? 'Select 4 players (2v2)'
			: !roundRobinSelected
			? 'Select player who won/lost'
			: '';

	/**
	 *
	 * @param teams Array of games, each with an array teams, with each team being an array of player IDs.
	 * @param winners An array of games, each with values for the 1-indexed position of the winning team.
	 */
	const submitMatchGames = function (teams: number[][][], winners: number[]) {
		const allSubmitButtons = document.getElementsByClassName('submit-button');
		const url = `/${currentActivity}/api/add_matches`;
		const json = {
			teams: teams,
			wins: winners
		};
		// Disable all submit buttons during request to prevent double-submissions.
		for (let element of allSubmitButtons) {
			(element as HTMLButtonElement).disabled = true;
		}
		fetch(url, {
			method: 'post',
			headers: {
				Accept: 'application/json',
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(json)
		})
			.then((response) => {
				if (!response.ok) {
					return Promise.reject(response);
				}
				return response.json();
			})
			.then((data) => {
				dispatch('submit', data);
			})
			.catch((err) => {
				console.error(err);
				dispatch('error', err);
			})
			.finally(() => {
				// Re-enable all submit buttons.
				for (let element of allSubmitButtons) {
					(element as HTMLButtonElement).disabled = false;
				}
			});
	};

	const submitMultiGames = function (winners: number[]) {
		const teams = Array.apply(null, Array(winners.length)).map(function () {
			return (
				selectedMemberIds
					// Exclude zero player IDs.
					.map((team) => team.filter((pid) => pid != 0))
			);
		});

		if (winners.length > 1) {
			const count1 = winners.filter((val) => val == 1).length;
			const count2 = winners.filter((val) => val == 2).length;
			const result =
				count1 == count2 ? 'teams tied' : count1 > count2 ? 'Team 1 won' : 'Team 2 won';
			const resultDetailed = count1 + ' vs ' + count2;
			const question =
				`Confirm that you want to submit a set of ${winners.length}` +
				` matches with results of ${resultDetailed} (${result})?`;
			if (confirm(question)) {
				submitMatchGames(teams, winners);
			}
		} else {
			submitMatchGames(teams, winners);
		}
	};

	const submitSingleGame = function (winner: number) {
		submitMultiGames([winner]);
	};

	const submitRoundRobinGames = function () {
		// TODO: handle non-2v2 cases
		const uniquePlayers = selectedMemberIds.flat().filter((id) => id != 0).length;
		if (uniquePlayers != 4) {
			console.log('Round-robin only supported for 2v2 games');
			return;
		}
		const smi = selectedMemberIds.flat();
		const teamsPerGame = [
			[
				[smi[0], smi[1]],
				[smi[2], smi[3]]
			],
			[
				[smi[0], smi[2]],
				[smi[1], smi[3]]
			],
			[
				[smi[0], smi[3]],
				[smi[2], smi[1]]
			]
		];
		const indexesOfTeamWithPlayer = function (playerId: number) {
			return teamsPerGame.map((game) => {
				if (game[0].indexOf(playerId) != -1) {
					return 1;
				}
				if (game[1].indexOf(playerId) != -1) {
					return 2;
				}
				return -1;
			});
		};
		let winners: number[] = [];
		if (roundRobinWinPlayer != 0) {
			winners = indexesOfTeamWithPlayer(roundRobinWinPlayer);
		} else if (roundRobinLosePlayer != 0) {
			winners = indexesOfTeamWithPlayer(roundRobinLosePlayer);
		} else {
			console.log('No winner/loser selected');
			return;
		}
		// Todo: add confirmation before submitting multiple matches
		submitMatchGames(teamsPerGame, winners);
	};
</script>

<h3 class="font-bold text-2xl">Match results</h3>
<p class="pt-4">Specify the teams that played:</p>

<div>
	<!-- Select teams & players -->
	{#each teamNames as team, teamIdx}
		<table class="table">
			<thead>
				<tr class="bg-base-200">
					<th class="text-center text-white text-lg">{team}</th>
				</tr>
			</thead>
			<tbody>
				<tr class="flex flex-col sm:flex-row">
					{#each defaultNames[teamIdx] as member, memberIdx}
						<select
							bind:value={selectedMemberIds[teamIdx][memberIdx]}
							on:change={() => resetRoundRobinSelect()}
							class="flex-1 m-1 sm:m-3 select select-bordered sm:max-w-xs"
						>
							<option selected value={0}>[{member}]</option>
							{#each players as player}
								<option value={player.id} disabled={isSelected(player.id)}>{player.name}</option>
							{/each}
						</select>
					{/each}
				</tr>
			</tbody>
		</table>
	{/each}

	<!-- Multiple ways to select the winnig team or submit multiple match results. -->
	<Tabs
		hashPrefix=""
		data={[
			{ title: 'Single Match', id: 'single-match' },
			{ title: 'Multiple Matches', id: 'multi-match' },
			{ title: 'Round-Tobin Teams', id: 'round-robin' }
		]}
	>
		<div id="single-match">
			<p class="pt-4">Select the winning team for a single game:</p>
			<div class="flex flex-col sm:flex-row gap-6">
				<button
					on:click={() => submitSingleGame(1)}
					class="submit-button btn btn-accent flex-1"
					disabled={!validMemberSelection}
				>
					Team 1
				</button>
				<button
					on:click={() => submitSingleGame(2)}
					class="submit-button btn btn-accent flex-1"
					disabled={!validMemberSelection}
				>
					Team 2
				</button>
			</div>
			<div
				class="w-full text-center text-sm text-gray-600"
				class:hidden={!singleSubmitDisabledReason}
			>
				[{singleSubmitDisabledReason}]
			</div>
		</div>

		<div id="multi-match">
			<p class="pt-4">Select the results for multiple games (between the same teams):</p>
			<div class="flex flex-row gap-6">
				<div class="flex-1 flex flex-col gap-6">
					<button class="btn flex-1" on:click={() => addMultiMatchResult(1)}>Team 1</button>
					<button class="btn flex-1" on:click={() => addMultiMatchResult(2)}>Team 2</button>
				</div>
				<div class="flex-1">
					<select bind:this={multiMatchList} multiple size={8} class="w-full h-full">
						{#each multiMatchWins as matchWinner, idx}
							<option value={idx}>Team {matchWinner} win</option>
						{/each}
					</select>
				</div>
				<div class="flex-1 flex flex-col gap-6">
					<button class="btn btn-neutral flex-1" on:click={() => removeSelectedMultiMatches()}
						>Remove selected</button
					>
					<button
						on:click={() => submitMultiGames(multiMatchWins)}
						class="submit-button btn btn-accent flex-1"
						disabled={!validMemberSelection || multiMatchWins.length == 0}
					>
						Submit
					</button>
				</div>
			</div>
			<div
				class="w-full text-center text-sm text-gray-600"
				class:hidden={!multiSubmitDisabledReason}
			>
				[{multiSubmitDisabledReason}]
			</div>
		</div>

		<div id="round-robin">
			<p class="pt-4">Select a result for a set of games consisting of all team combinations:</p>
			<div class="flex flex-col items-center">
				<span class="flex flex-row items-baseline">
					<p>Won 3 games:</p>
					<select
						bind:value={roundRobinWinPlayer}
						disabled={roundRobinLosePlayer != 0}
						class="flex-1 m-1 sm:m-3 select select-bordered sm:max-w-xs"
					>
						<option selected value={0}>(None)</option>
						{#each selectedPlayers as player}
							<option value={player.id}>{player.name}</option>
						{/each}
					</select>
				</span>
				<span class="flex flex-row items-baseline">
					<p>Lost 3 games:</p>
					<select
						bind:value={roundRobinLosePlayer}
						disabled={roundRobinWinPlayer != 0}
						class="flex-1 m-1 sm:m-3 select select-bordered sm:max-w-xs"
					>
						<option selected value={0}>(None)</option>
						{#each selectedPlayers as player}
							<option value={player.id}>{player.name}</option>
						{/each}
					</select>
				</span>
				<button
					on:click={() => submitRoundRobinGames()}
					class="submit-button btn btn-accent flex-1 md:w-1/2"
					disabled={selectedPlayers.length != 4 || !roundRobinSelected}
				>
					Submit
				</button>
				<div
					class="w-full text-center text-sm text-gray-600"
					class:hidden={!roundRobinSubmitDisabledReason}
				>
					[{roundRobinSubmitDisabledReason}]
				</div>
			</div>
		</div>
	</Tabs>
</div>
