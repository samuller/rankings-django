<script lang="ts">
	import type { ActivityPage } from './+page';
	import { Card, DynamicData } from '$lib/components';
	import {
		currentActivityUrl,
		currentActivity,
		navTitle,
		activities,
	} from '../../store';

	export let data: ActivityPage;
	currentActivityUrl.set(data.activity_url);
	$: if ($currentActivity) { navTitle.set($currentActivity.name); }
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

	<slot />
{/if}
