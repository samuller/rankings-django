<script lang="ts">
	import Table from "../lib/table.svelte";
	import AddButton from "../lib/add-button.svelte";
	import Card from "../lib/card.svelte";
</script>

<!--
<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>

<h1 class="text-3xl font-bold underline">
    Hello world!
</h1> -->

<Card>
    <p class="text-white group-hover:text-white text-lg">Table tennis</p>
</Card>

<Card>
    <div class="flex items-center space-x-3">
    <h3 class="text-white group-hover:text-white text-sm font-semibold">New project</h3>
    </div>
    <p class="text-white group-hover:text-white text-sm">Create a new project from a variety of starting templates.</p>
</Card>

<Table></Table>
<AddButton></AddButton>

<style lang="postcss">
    :global(html) {
        /* background-color: theme(colors.gray.100); */
    }
</style>
