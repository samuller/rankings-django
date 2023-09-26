<!--
  @component
  Generate unicode characters to display the flag of the given country code. Requires font support.

  Usage:
  ```tsx
  <Flag country="UN"></Flag>
  ```
-->
<script lang="ts">
	export let country = '';
	$: unicodePoints = [...country].map(
		(char) => char.toUpperCase().charCodeAt(0) - 'A'.charCodeAt(0)
	);
</script>

<span {...$$restProps}>
	<!-- See: https://en.wikipedia.org/wiki/Regional_indicator_symbol -->
	<!-- HTML entity for regional indicator "A" is "127462" (or in hex notation "&#x1f1e6;") -->
	{#each unicodePoints as code}
		{@html `&#${127462 + code};`}
	{/each}
</span>
