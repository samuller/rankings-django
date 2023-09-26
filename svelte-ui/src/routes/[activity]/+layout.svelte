<script lang="ts">
	import { page } from '$app/stores'
	import { Card, DynamicData } from '$lib/components';
	import {
		currentActivityUrl,
		currentActivity,
		navTitle,
		activities,
	} from '../../store';

	currentActivityUrl.set($page.params.activity);
	$: if ($currentActivity) { navTitle.set($currentActivity.name); }
    $: viewingPlayerProfile = $page.url.pathname.includes("/player/");
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
    {#if !viewingPlayerProfile}
        <Card class="w-full md:w-1/2 2xl:w-[calc(0.5*1536px)] flex justify-center" style="tight">
            <span class="normal-case text-xl font-semibold">{$currentActivity.name}</span>
        </Card>
    {/if}

	<slot />
{:else if $currentActivity === null}
	<div class="text-red-500">
		<h3>Invalid activity: <code>{$currentActivityUrl}</code></h3>
		<p>See list of activities <code><a href="/" class="underline text-sky-500">here</a></code>.</p>
	</div>
{/if}
