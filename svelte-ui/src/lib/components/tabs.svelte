<!--
  @component
  Tabs that are used to show/hide different parts of the interface below it.

  Usage:
  ```tsx
  // Method one: fully dynamic tabs, but can only use static HTML strings.
  <Tabs data={[
    {title: 'Tab 1', id: 'tab1', content: '<button>First tab</button>'},
    {title: 'Tab 2', id: 'tab2', content: '<button>Second tab</button>'},
  ]}></Tabs>
  // Method two: tabs can use full dynamic HTML, events, etc.
  <Tabs data={[
    {title: 'Tab 1', id: 'tab1'}
    {title: 'Tab 2', id: 'tab2'}
  ]}>
    <button id="tab1">First tab</button>
    <button id="tab2">Second tab</button>
  </Tabs>
  ```
-->
<script lang="ts">
	import { onMount } from 'svelte';

	interface ITabData {
		id: string;
		title: string;
		content?: string;
	}

	export let data: ITabData[] = [];
	export let hashPrefix = 'tab-';

	$: tabIds = data.map((tab) => `${hashPrefix}${tab.id}`);
	$: hashUrl = window.location.hash.slice(1);
	let selectedTabIdx = 0;
	$: if (tabIds.includes(hashUrl)) {
		selectedTabIdx = tabIds.indexOf(hashUrl);
	}

	const updateVisibleTabs = function (tabs: ITabData[], selectedTabIdx: number) {
		data.forEach((tab, idx) => {
			const tabEl = document.getElementById(tab.id);
			if (idx != selectedTabIdx) {
				tabEl?.classList.add('hidden');
			} else {
				tabEl?.classList.remove('hidden');
			}
		});
	};

	$: if (data) {
		updateVisibleTabs(data, selectedTabIdx);
	}

	onMount(() => {
		updateVisibleTabs(data, selectedTabIdx);
	});
</script>

<!-- Headers -->
<div class="block whitespace-nowrap overflow-x-scroll horz-scroll-edges">
	{#each data as tab, idx}
		<a
			id="tab_{tab.id}"
			href="#{hashPrefix}{tab.id}"
			data-sveltekit-noscroll
			class="tab tab-lg tab-bordered inline-block"
			class:tab-active={selectedTabIdx == idx}
			on:click={(event) => {
				// Scroll selected tab into view (mainly horizontally for small screens).
				if (event.target && 'scrollIntoView' in event.target) {
					// @ts-ignore
					event.target?.scrollIntoView?.({ behavior: 'smooth', block: 'start', inline: 'start' });
				}
				selectedTabIdx = idx;
			}}
		>
			{tab.title}
		</a>
	{/each}
</div>
<!-- Content -->
{#each data as tab, idx}
	{#if tab.content}
		<div class:hidden={selectedTabIdx != idx}>
			<!-- Not safe against XSS injections unless sanitized. -->
			{@html tab.content}
		</div>
	{/if}
{/each}

<slot />

<style lang="postcss">
	/*
    We extend the DaisyUI class "".tab-active" because we couldn't get a tailwind modifier for when this class has
    been added. Another alternative is to add the following svelte code to the applicable components:
        class:tab-active={selectedTabIdx == idx}
        class:text-blue-600={selectedTabIdx == idx}
    */
	.tab-active {
		@apply text-white;
	}

	/*
      Gradient edges used to hint at/indicate that horizontal scrolling is possible.
      Needed because horizontal scrollbar only appears on mouse over or click.
    */
	.horz-scroll-edges {
		mask-image: linear-gradient(90deg, #000 60%, #000 60px, transparent);
	}
</style>
