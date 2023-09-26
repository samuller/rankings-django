<script lang="ts">
	import type { PageableAPIStore } from '../../store';
	import Icon from './icon.svelte';

	export let pageNr = 1;
	export let pageable: PageableAPIStore<any>;

	function setQuery(key: string, value: string) {
		const currURL = new URL(window.location.href);
		currURL.searchParams.set(key, value);
		return currURL;
	}

	let showFirst = false;
	let showPrev = false;
	let showNext = false;
	let showLast = false;
	let lastURL = '';

	$: if ($pageable) {
		showFirst = pageable.paged() && pageable.firstURL() != null && pageable.prevURL() != null;
		showPrev = pageable.paged() && pageable.prevURL() != null;
		showNext = pageable.paged() && pageable.nextURL() != null;
		showLast = pageable.paged() && pageable.lastURL() != null && pageable.nextURL() != null;
		lastURL = pageable.lastURL() ?? '';
	}
</script>

<div class="join">
	<div class="tooltip" data-tip="First">
		<a
			href={setQuery('page', '1').href}
			class="join-item btn text-xl"
			class:btn-disabled={!showFirst}
		>
			&laquo;
		</a>
	</div>
	<div class="tooltip" data-tip="Previous">
		<a
			href={setQuery('page', (pageNr - 1).toString()).href}
			class="join-item btn btn-disabled text-xl"
			class:btn-disabled={!showPrev}
		>
			<Icon name="left-bracket" width="24" height="24" class="h-6 w-6 fill-current md:h-8 md:w-8" />
		</a>
	</div>
	<button class="join-item btn normal-case">Page {pageNr}</button>
	<div class="tooltip" data-tip="Next">
		<a
			href={setQuery('page', (pageNr + 1).toString()).href}
			class="join-item btn text-xl"
			class:btn-disabled={!showNext}
		>
			<Icon name="right-bracket" class="h-6 w-6 fill-current md:h-8 md:w-8" />
		</a>
	</div>
	<div class="tooltip" data-tip="Last">
		<a
			href={setQuery('page', pageable.pageFromURL(lastURL).toString()).href}
			class="join-item btn normal-case text-xl"
			class:btn-disabled={!showLast}
		>
			&raquo;
		</a>
	</div>
</div>
