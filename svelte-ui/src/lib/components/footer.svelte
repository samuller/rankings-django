<script lang="ts">
	import { dateToLocalISOWithTZ } from '$lib/utils';

	// See vite.config.ts.
	// eslint-disable-next-line  no-undef
	const version = __APP_VERSION__;
	// Convert ISO formatted UTC date string to local Date and then back to ISO string that has local timezone.
	const buildDate = dateToLocalISOWithTZ(new Date(version.buildDate));
	$: shortBuildDate = buildDate.slice(0, 10);
	$: longBuildDate = buildDate.replaceAll(/[TZ]/g, ' ');
</script>

<footer class="footer p-2 flex">
	<div class="tooltip" data-tip={longBuildDate}>
		<span>Build date: {shortBuildDate} </span>
	</div>
	<div class="flex-1" />
</footer>
