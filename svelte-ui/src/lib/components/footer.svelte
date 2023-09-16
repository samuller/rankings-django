<script lang="ts">
	import { readJSONAPI } from "$lib/api";

    const version = readJSONAPI<any>({}, '/assets/version.json');
    $: buildDate = ($version["build-date"] ?? "unknown").slice(0, 10);
</script>

<footer class="footer p-2 flex">
    <div class="tooltip" data-tip={new Date().toISOString()}>
        <span>Build date: {buildDate}</span>
    </div>
    <div class="flex-1"></div>
</footer>
