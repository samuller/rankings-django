<script context="module" lang="ts">
    export interface CellDetail {
        // Type is actually anything that can be implicitly converted to a string.
        text: any;
        url?: string;
        tooltip?: string;
    }
</script>

<script lang="ts">
    export let columnNames: string[];
    export let columnAlignments: string[] = [];
    export let rows: CellDetail[][];
</script>

<div class="relative overflow-x-auto">
    <table class="w-full table-auto min-w-[16rem] md:min-w-[24rem] mx-auto text-sm text-left text-gray-500 dark:text-gray-400">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
                {#each columnNames as name, idx}
                <th scope="col" class="px-3 md:px-6 py-3 {columnAlignments[idx]}">
                    {name}
                </th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each rows as row, row_idx}
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                {#each row as cell, cell_idx}
                <td class="px-3 md:px-6 py-4 text-white {columnAlignments[cell_idx]}">
                    <div class:tooltip={cell.tooltip ?? false} data-tip={cell.tooltip}
                        class={cell.tooltip ? "has-tip" : ""}>
                    {#if cell.url}
                        <a href="{cell.url}" class="underline">{cell.text}</a>
                    {:else}
                        {cell.text}
                    {/if}
                    </div>
                </td>
                {/each}
            </tr>
            {/each}
        </tbody>
    </table>
</div>

<style lang="postcss">
    .has-tip {
        @apply font-bold;
        border-bottom: dotted 1px #cccccc;
    }
</style>