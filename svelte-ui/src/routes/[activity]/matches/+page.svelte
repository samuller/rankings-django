<script lang="ts">
	import { page } from '$app/stores';
	import type { ActivityPage } from './+page';
	import { AddButton, Card, DynamicData, PagingNav, Table, type RowDetail } from '$lib/components';
	import {
		currentActivityUrl,
		currentActivity,
		navTitle,
		activities,
		type Matches,
		apiMatches,
	} from '../../../store';

	export let data: ActivityPage;
	currentActivityUrl.set(data.activity_url);
	$: pageNr = parseInt($page.url.searchParams.get('page') ?? '1');

	let matchesTable: RowDetail[][] = [];

	$: if ($currentActivity) { navTitle.set($currentActivity.name); }
	$: matches = apiMatches(data.activity_url, pageNr);
	$: matchesTable = $matches
		.map((match: Matches) => [
			{ text: match.id },
			{ text: new Date(match.datetime*1000).toISOString().replace('T', ' ').split('.')[0]+"Z" },
			{ text: match.teams[0].members.map((member) => member.player.name).join(" & ") },
			{ text: match.teams[1].members.map((member) => member.player.name).join(" & ") },
		]);
</script>

<svelte:head>
{#if $currentActivity}
	<title>Rankings - {$navTitle}</title>
{:else}
	<title>Rankings</title>
{/if}
</svelte:head>

<DynamicData data={activities}></DynamicData>

{#if $currentActivity}
	<Card class="w-full md:w-1/2 2xl:w-[calc(0.5*1536px)] flex justify-center" style="tight">
		<span class="normal-case text-xl font-semibold">{$currentActivity.name}</span>
	</Card>

	<div class="w-full md:w-1/2 text-gray-700">
		<h2 class="text-2xl font-bold text-left">Match history</h2>
		<p class="text-left">Reported matches which have been validated.</p>
	</div>
	<DynamicData data={matches}></DynamicData>
	{#if matchesTable.length > 0}
		<PagingNav {pageNr} pageable={matches}></PagingNav>
		<Table
			columnNames={['ID #', 'Date', 'Team 1', 'Team 2']}
			columnAlignments={['text-center', 'text-center', 'text-center', 'text-center']}
			rows={matchesTable}
		></Table>
	{/if}
{/if}
