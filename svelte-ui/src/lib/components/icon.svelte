<!--
    See: https://stackoverflow.com/questions/66069647/best-way-to-import-svg-icons-into-a-svelte-app
-->
<script lang="ts">
	export let name: keyof typeof customStyle;
	export let width = '1em';
	export let height = '1em';
	export let focusable: string | number | null | undefined = undefined;

	const customStyle: { [key: string]: any } = {
		language: {},
		plus: {},
		'left-bracket': { stroke: 'none' },
		'right-bracket': { stroke: 'none' },
		'bolt-slash': {}
	};
	const iconStyle = customStyle[name] ?? { stroke: 'goldenrod' };
</script>

<svg
	{width}
	{height}
	viewBox="0 0 {iconStyle.box ?? 24} {iconStyle.box ?? 24}"
	class={$$props.class}
	stroke={iconStyle.stroke ?? 'currentColor'}
	fill="none"
	stroke-width={iconStyle.strokeWidth ?? 1.5}
	{focusable}
>
	{#if name == 'language'}
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			d="M10.5 21l5.25-11.25L21 21m-9-3h7.5M3 5.621a48.474 48.474 0 016-.371m0 0c1.12 0 2.233.038 3.334.114M9 5.25V3m3.334 2.364C11.176 10.658 7.69 15.08 3 17.502m9.334-12.138c.896.061 1.785.147 2.666.257m-4.589 8.495a18.023 18.023 0 01-3.827-5.802"
		/>
	{:else if name == 'plus'}
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			stroke-width="2"
			d="M12 6v6m0 0v6m0-6h6m-6 0H6"
		/>
	{:else if name == 'left-bracket'}
		<path d="M15.41,16.58L10.83,12L15.41,7.41L14,6L8,12L14,18L15.41,16.58Z" />
	{:else if name == 'right-bracket'}
		<path d="M8.59,16.58L13.17,12L8.59,7.41L10,6L16,12L10,18L8.59,16.58Z" />
	{:else if name == 'bolt-slash'}
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			d="M11.412 15.655L9.75 21.75l3.745-4.012M9.257 13.5H3.75l2.659-2.849m2.048-2.194L14.25 2.25 12 10.5h8.25l-4.707 5.043M8.457 8.457L3 3m5.457 5.457l7.086 7.086m0 0L21 21"
		/>
	{:else}
		<!-- Use bolt-slash as default/fallback/error indicator. -->
		<path
			stroke-linecap="round"
			stroke-linejoin="round"
			d="M11.412 15.655L9.75 21.75l3.745-4.012M9.257 13.5H3.75l2.659-2.849m2.048-2.194L14.25 2.25 12 10.5h8.25l-4.707 5.043M8.457 8.457L3 3m5.457 5.457l7.086 7.086m0 0L21 21"
		/>
	{/if}
</svg>
