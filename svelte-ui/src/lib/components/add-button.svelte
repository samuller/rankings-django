<script lang="ts">
	import { onMount } from 'svelte';
	import { Icon } from '.';

	export let color = 'text-white bg-teal-500 hover:bg-teal-400 focus:ring-teal-600';

	let animate = '';
	onMount(() => {
		// Animation to draw attention to button for the first few seconds you see it.
		animate = 'animate-spin ring-4';
		setInterval(() => {
			animate = '';
		}, 2000);
	});
</script>

<div data-dial-init class="fixed right-6 bottom-6 group">
	<button
		type="button"
		on:click
		data-dial-toggle="speed-dial-menu-default"
		aria-controls="speed-dial-menu-default"
		aria-expanded="false"
		class={`${animate} rounded-full w-14 h-14 flex items-center justify-center ${color} focus:ring-4 focus:outline-none`}
	>
		<Icon name="plus" class="w-8 h-8 transition-transform group-hover:rotate-45" />
		<span class="sr-only">Open actions menu</span>
	</button>
</div>
