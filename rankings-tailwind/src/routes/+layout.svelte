<script>
  import "../app.css";
	import Footer from "../lib/footer.svelte";
	import Navbar from "../lib/navbar.svelte";
</script>

<svelte:head>
    <title>Rankings</title> 
</svelte:head>

<div class="h-screen flex flex-col">
  <Navbar></Navbar>
  <section class="bg-gray-300 flex-1 flex flex-col justify-start items-center gap-6 p-4">
  <slot />
  </section>
  <Footer></Footer>
</div>
