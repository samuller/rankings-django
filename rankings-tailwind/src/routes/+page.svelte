<script lang="ts">
	import Table from "../lib/table.svelte";
	import AddButton from "../lib/add-button.svelte";
	import Card from "../lib/card.svelte";
	import { page_title } from '../store';

    let activities = ['⚽ Foosball', '🏓 Table tennis', '🏆 Table Tennis Tournament 2022'];
    page_title.set("");
</script>

{#each activities as activity}
    <a href="#">
        <Card class="w-96 md:w-[600px] hover:bg-sky-500 hover:ring-sky-500">
                <p class="text-center text-white group-hover:[text-shadow:_0_0_3px_blue] text-2xl">{activity}</p>
        </Card>
    </a>
{/each}

<Table></Table>

<AddButton></AddButton>

<style lang="postcss">
    :global(html) {
        /* background-color: theme(colors.gray.100); */
    }
</style>
