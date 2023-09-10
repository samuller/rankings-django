<script>
  import "../app.css";
	import { Footer, Navbar } from "$lib/components";
	import { players } from "../store";

  // Load player data into the store for whenever it's needed,
  players.load();
</script>

<div class="h-screen flex flex-col">
  <Navbar></Navbar>
  <section class="bg-gray-300 flex-1 flex flex-col justify-start items-center gap-6 p-4">
  <slot />
  </section>
  <Footer></Footer>
</div>
