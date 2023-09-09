<script lang="ts">
    import type { PageableAPIStore } from '../../store';

    export let pageNr = 1;
    export let pageable: PageableAPIStore<any>;

    function setQuery(key: string, value: string) {
		const currURL = new URL(window.location.href);
		currURL.searchParams.set(key, value);
		return currURL;
	}
</script>


<div class="join">
    {#if pageable.paged() && pageable.firstURL() && pageable.prevURL()}
    <div class="tooltip" data-tip="First">
        <a href={setQuery('page', '1').href}  class="join-item btn">&lt;&lt;</a>
    </div>
    {/if}
    {#if pageable.paged() && pageable.prevURL()}
    <div class="tooltip" data-tip="Previous">
        <a href={setQuery('page', (pageNr - 1).toString()).href}  class="join-item btn">&lt;</a>
    </div>
    {/if}
    {#if pageable.paged() && pageable.nextURL()}
    <div class="tooltip" data-tip="Next">
        <a href={setQuery('page', (pageNr + 1).toString()).href} class="join-item btn">&gt;</a>
    </div>
    {/if}
    {#if pageable.paged() && pageable.lastURL() && pageable.nextURL()}
    <div class="tooltip" data-tip="last">
        <a
            href={setQuery('page', pageable.pageFromURL(pageable.lastURL() ?? '').toString()).href}
            class="join-item btn normal-case">&gt;&gt;</a>
    </div>
    {/if}
</div>