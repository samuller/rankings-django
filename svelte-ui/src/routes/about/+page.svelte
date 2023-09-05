<script lang="ts">
	import Card from "$lib/card.svelte";
	import Tabs from "$lib/tabs.svelte";
    import { navTitle } from '../../store';

    navTitle.set("About");

	const TABS = [
		{
            id: 'trueskill',
			title: 'Trueskill',
			content: `<p>
                    These rankings are based on the <a href="http://research.microsoft.com/en-us/projects/trueskill/">Trueskill™</a>
                    algorithm that was developed by Microsoft Research. The system represents skill as a Normal
                    distribution which is updated after every game according to Bayesian probability.
                </p>`
		},
		{
            id: 'foosball',
			title: 'Foosball',
			content: ''
		},
		{
            id: 'table_tennis',
			title: 'Table tennis',
			content: ''
		},
		{
            id: 'website',
			title: 'Website',
			content: `<h5>Credits</h5>
				<p>
                    This site was created using <a href="https://kit.svelte.dev/">SvelteKit</a> and
                    <a href="https://daisyui.com/">daisyUI</a> for the interface,
                    <a href="http://www.highcharts.com/">Highcharts</a>
                    for the graphs and the <a href="https://github.com/moserware/Skills">Skills</a> library for
                    calculating the skill algorithm.
                </p>`
		}
	];
</script>

<Card class="w-full lg:w-3/4 2xl:w-[calc(0.75*1536px)]">
    <Tabs data={TABS}></Tabs>
</Card>
