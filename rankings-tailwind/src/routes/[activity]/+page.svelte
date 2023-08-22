<script lang="ts">
	import type { ActivityPage } from "./+page";
	import Card from "$lib/card.svelte";
	import Table from "../../lib/table.svelte";
	import TimePlot from "$lib/time-plot.svelte";
	import AddButton from "../../lib/add-button.svelte";
	import { page_title } from '../../store';

	export let data: ActivityPage;

	page_title.set(data.url); // activity.title
</script>

<Card class="w-1/2 2xl:w-[calc(0.5*1536px)] flex justify-center" style="tight">
	<a class="normal-case text-xl font-semibold">{data.url}</a>
</Card>


<Table></Table>

<TimePlot></TimePlot>

<AddButton></AddButton>
