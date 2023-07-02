<script>
  import "../app.css";
	import Footer from "../lib/footer.svelte";
	import Navbar from "../lib/navbar.svelte";
</script>

<div class="h-screen flex flex-col">
  <Navbar></Navbar>
  <section class="flex-1 p-4">
  <slot />
  </section>
  <Footer></Footer>
</div>
