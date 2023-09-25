<script lang="ts">
	import { readJSONAPI } from "$lib/api";

    // See vite.config.ts.
    const version = __APP_VERSION__;
    $: shortBuildDate = (version.buildDate ?? "unknown").slice(0, 10);
    $: longBuildDate = (version.buildDate ?? "unknown").replaceAll(/[TZ]/g, " ");
</script>

<footer class="footer p-2 flex">
    <div class="tooltip" data-tip={longBuildDate}>
        <span>Build date: {shortBuildDate}
        </span>
    </div>
    <div class="flex-1"></div>
</footer>
