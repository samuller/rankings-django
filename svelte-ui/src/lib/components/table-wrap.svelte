<!--
  @component
  A table that wraps ending columns to under the row on smaller screens (uses <div>'s with CSS flex).

  Usage:
  ```tsx
  <TableWrap
  columns={[
      {title: 'Concept name', classes: 'flex-1 pr-2'},
      {title: 'Concept Value', classes: 'flex-1 pr-2 text-center'},
      {title: 'Detail', classes: 'flex-[5_5_0%]', headerClasses: 'max-sm:hidden'}
  ]}
  rows={[
      ['Concept', 'Some values', 'Long description'],
      ['2nd Concept', '2nd values', '2nd long description'],
  ]}
></TableWrap>
  ```
-->
<script lang="ts">
	export let columns: {
		title: string;
		// Classes that will be applied to all cells in this column.
		classes?: string;
		// Classes that will be only be applied to the header cells in this column.
		headerClasses?: string;
	}[];
	export let rows: string[][];
	// Number of first few columns that will never wrap, even on small screens.
	export let noWrapColumns = 2;
</script>

<div class="flex flex-col bg-gray-500">
	<!-- Table headers -->
	<div class="flex p-2 bg-gray-900 font-bold">
		{#each columns as header, hdr_idx}
			<div
				class={`${header.classes} ${header.headerClasses} my-auto text-left ${
					hdr_idx >= noWrapColumns ? 'max-sm:hidden' : ''
				}`}
			>
				{header.title}
			</div>
		{/each}
	</div>
	<!-- Table rows -->
	<!-- Style every second row to be darker. -->
	<div class="[&>:nth-child(odd)]:bg-gray-700">
		{#each rows as row}
			<div class="flex flex-wrap p-2">
				{#each row as cell, cell_idx}
					{#if cell_idx == noWrapColumns}
						<!-- Div that expands on small screens to fill row and force wrapping. -->
						<div class="flex-[0_0_100%] sm:hidden my-auto" />
					{/if}
					{#if cell_idx < noWrapColumns}
						<div class={`${columns[cell_idx].classes} my-auto`}>{@html cell}</div>
					{:else}
						<!-- Wraps that might get wrapped get a top border for separation. -->
						<div class={`${columns[cell_idx].classes} my-auto max-sm:border-t border-gray-400`}>
							{@html cell}
						</div>
					{/if}
				{/each}
			</div>
		{/each}
	</div>
</div>
