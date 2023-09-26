<script lang="ts">
	let classes: String = '';

	// Creates a `class` property, even though it is a reserved word
	// See: https://svelte.dev/docs/svelte-components#script-1-export-creates-a-component-prop
	export { classes as class };
	export let variant: 'normal' | 'tight' = 'normal';

	let padding = 'p-6';
	if (variant === 'tight') {
		padding = 'px-6 py-4';
	}
</script>

<div
	class="group block rounded-lg {padding} bg-gray-600 text-white ring-1 ring-slate-900/5 shadow-lg {classes}"
>
	<slot />
</div>
