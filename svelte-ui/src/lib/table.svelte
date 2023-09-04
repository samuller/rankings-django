<script lang="ts">
    export let columnNames: string[];
    export let rows: string[][];

    $: columnAlignments = columnNames.map((val, idx) => {
        return idx == columnNames.length - 1 ? "text-right" : "text-left"
    });
</script>

<div class="relative overflow-x-auto">
    <table class="w-full table-auto sm:w-96 mx-auto text-sm text-left text-gray-500 dark:text-gray-400">
        <thead class="text-xs text-gray-700 uppercase bg-gray-50 dark:bg-gray-700 dark:text-gray-400">
            <tr>
                {#each columnNames as name, idx}
                <th scope="col" class="px-6 py-3 {columnAlignments[idx]}">
                    {name}
                </th>
                {/each}
            </tr>
        </thead>
        <tbody>
            {#each rows as row, row_idx}
            <tr class="bg-white border-b dark:bg-gray-800 dark:border-gray-700">
                {#each row as cell, cell_idx}
                <td class="px-6 py-4 text-white {columnAlignments[cell_idx]}">
                    {cell}
                </td>
                {/each}
            </tr>
            {/each}
        </tbody>
    </table>
</div>
