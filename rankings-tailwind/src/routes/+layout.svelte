<script>
  import "../app.css";
	import Footer from "../lib/footer.svelte";
	import Navbar from "../lib/navbar.svelte";
</script>

<div class="h-screen flex flex-col">
  <Navbar></Navbar>
  <section class="bg-gray-300 flex flex-col justify-start gap-6 p-4 flex-1">
  <slot />
  </section>
  <Footer></Footer>
</div>
