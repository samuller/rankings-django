<script lang="ts">
    interface ITabData {
        id: string;
        title: string;
        content: string;
    }

    export let data: ITabData[] = [];

    let selectedTabIdx = 0;
</script>

<!-- Headers -->
<div class="tabs">
{#each data as tab, idx}
    <a
        id="tab_{tab.id}"
        href="#"
        data-sveltekit-noscroll
        class="tab tab-lg tab-bordered"
        class:tab-active={selectedTabIdx == idx}
        on:click={() => (selectedTabIdx = idx)}>{tab.title}</a
    >
{/each}
</div>
<!-- Content -->
{#each data as tab, idx}
<div class:hidden={selectedTabIdx != idx}>
    <!-- Not safe against XSS injections unless sanitized -->
    {@html tab.content}
</div>
{/each}

<style lang="postcss">
    /*
    We extend the DaisyUI class "".tab-active" because we couldn't get a tailwind modifier for when this class has
    been added. Another alternative is to add the followin svelte code to the applicable components:
        class:tab-active={selectedTabIdx == idx}
        class:text-blue-600={selectedTabIdx == idx}
    */
    .tab-active {
        @apply text-white;
    }
</style>
