<script lang="ts">
    export let color = "text-white bg-teal-500 hover:bg-teal-400 focus:ring-teal-600";
</script>

<div data-dial-init class="fixed right-6 bottom-6 group">
	<button
		type="button"
        on:click
		data-dial-toggle="speed-dial-menu-default"
		aria-controls="speed-dial-menu-default"
		aria-expanded="false"
		class={`rounded-full w-14 h-14 flex items-center justify-center ${color} focus:ring-4 focus:outline-none`}
	>
		<svg
			aria-hidden="true"
			class="w-8 h-8 transition-transform group-hover:rotate-45"
			fill="none"
			stroke="currentColor"
			viewBox="0 0 24 24"
			xmlns="http://www.w3.org/2000/svg"
			><path
				stroke-linecap="round"
				stroke-linejoin="round"
				stroke-width="2"
				d="M12 6v6m0 0v6m0-6h6m-6 0H6"
			/></svg
		>
		<span class="sr-only">Open actions menu</span>
	</button>
</div>
