<script>
	import { SvelteToast } from '@zerodevx/svelte-toast';
	import '../app.css';
	import { Footer, Navbar } from '$lib/components';
	import { players } from '../store';

	// Load player data into the store for whenever it's needed,
	players.load();

	const toastStyle = {
		reversed: true,
		intro: { y: 192 },
		duration: 10000,
		pausable: true
	};
</script>

<div class="h-screen flex flex-col">
	<Navbar />
	<section class="bg-gray-300 flex-1 flex flex-col justify-start items-center gap-6 p-4">
		<slot />
	</section>
	<Footer />
</div>

<SvelteToast options={toastStyle} />

<style lang="postcss">
	:root {
		--toastContainerTop: auto;
		--toastContainerRight: auto;
		--toastContainerBottom: 1rem;
		--toastContainerLeft: calc(50vw - 8rem);
	}

	:global(.toast-as-error) {
		--toastBackground: rgb(220, 38, 38);
		--toastBarBackground: rgb(248, 113, 113);
	}

	:global(.toast-as-success) {
		--toastColor: mintcream;
		--toastBackground: rgb(72, 187, 120);
		--toastBarBackground: #2f855a;
	}

	:global(.toast-as-info) {
		--toastBackground: #4299e1;
		--toastBarBackground: #2b6cb0;
	}
</style>
