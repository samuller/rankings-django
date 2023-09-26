<script lang="ts">
	let classes = '';
	export { classes as class };
	export let popupClass = '';
	// export let directionIcon = false;
	// TODO: support dropdown options that aren't <li></li> items (or at least document <li> requirement)

	/**
	 * Close dropdown menu if it is currently open - use with on:blur to close on click-away.
	 *
	 * This function is only needed when you want to use DaisyUI's dropdown menu based on the <details> tag.
	 * See: https://daisyui.com/components/dropdown/#dropdown-menu-using-details-tag
	 */
	function closeMenuIfOpen(event: Event) {
		if (!(event?.target instanceof HTMLElement)) {
			return;
		}
		// const target: HTMLElement = event?.target;
		// if (target?.parentElement && target.parentElement.hasAttribute("open")) {
		//     target.click();
		// }
	}
</script>

<details class={`dropdown ${classes}`}>
	<summary on:blur={closeMenuIfOpen}>
		<slot name="title" />
	</summary>
	<ul class={`dropdown-content ${popupClass}`}>
		<slot />
	</ul>
</details>

<style>
	summary {
		list-style: none;
	}
</style>
