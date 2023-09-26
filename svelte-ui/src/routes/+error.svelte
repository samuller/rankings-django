<script>
	import { page } from '$app/stores';

    const url = new URL($page.url);
    const relativeUrl = url.pathname + url.search + url.hash;
    // TODO: would be nice if we could direct user to first valid parent URL.
    const parentUrl = url.pathname.split('/').slice(0, -1).join("/");
</script>

<div class="text-red-500">
{#if $page.status == 404}
<div>Page not found: <code>{relativeUrl}</code></div>
<div>
    Maybe try:
    <code><a href={parentUrl} class="underline text-sky-500">{parentUrl}</a></code>
</div>
{:else}
{$page.status}: {$page.error.message}
{/if}
</div>
