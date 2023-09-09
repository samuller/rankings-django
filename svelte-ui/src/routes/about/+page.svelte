<script lang="ts">
	import { onMount } from 'svelte';
	import { Card, Tabs } from "$lib/components";

	let TABS: any[] = [];

	onMount(() => {
		TABS = [
			{
				id: 'trueskill',
				title: 'Trueskill',
				content: document.getElementById('about-trueskill')?.innerHTML ?? '',
			},
			{
				id: 'website',
				title: 'Website',
				content: document.getElementById('about-website')?.innerHTML ?? '',
			}
		];
	});
</script>

<Card class="w-full lg:w-3/4 2xl:w-[calc(0.75*1536px)]">
    <Tabs data={TABS}></Tabs>
</Card>

<template id="about-trueskill">
	<p class="mt-3 text-justify">
		These rankings are based on the <a href="http://research.microsoft.com/en-us/projects/trueskill/">Trueskill™</a>
		algorithm that was developed by Microsoft Research. The system represents skill as a Normal
		distribution which is updated after every game according to Bayesian probability.
	</p>
	<p class="text-justify">
		By representing skill as a Normal distribution it is therefore described by two values, μ and σ which
		respectively represent the player's average skill and the degree of uncertainty in the player's skill.
		After each game result the uncertainty will decrease, although it will never become zero as to allow for
		player skills that change over time. For ranking purposes the two values are combined into a single
		'conservative skill estimate' (by using μ-3*σ) which represents a 99% confidence that a player has a skill
		higher than the given value.
	</p>
	<p class="text-justify">
		In Trueskill each game type needs to define a few crucial parameters that specify how games vary in skill
		level and how player progression and skill values are represented. These parameters are as follows:
	</p>
	<table>
		<thead>
		  <tr class="text-left">
			<th>Parameter</th>
			<th class="w-40 text-center">Default Value</th>
			<th>Meaning</th>
		  </tr>
		</thead>
		<tbody>
			<tr>
				<td>Skill value</td>
				<td>0 to 50</td>
				<td>The skill value is defined to vary within this range so that values are more comfortable for people to work with (as opposed to values such as 0.008746 or 783,139).</td>
			</tr>
			<tr>
				<td>Initial mean (𝛍<span style="vertical-align: bottom; font-size: 0.4em;">O</span>)</td>
				<td>25</td>
				<td>The mean of an average player and which is also assigned as the initial mean value to all new players.</td>
			</tr>
			<tr>
				<td>Initial standard deviation (𝛔<span style="vertical-align: bottom; font-size: 0.4em;">O</span>)</td>
				<td><sup>25</sup>&frasl;<sub>3</sub> = 8.333...</td>
				<td>The standard deviation of a completely new player about which no information is yet known.</td>
			</tr>
			<tr>
				<td>Dynamics factor (𝛕)</td>
				<td><sup>25</sup>&frasl;<sub>300</sub> = 0.08333...</td>
				<td>A variable added to a player's standard deviation before every game to account for the fact that player's skills change over time.</td>
			</tr>
			<tr>
				<td>Skill chain (𝛃)</td>
				<td><sup>25</sup>&frasl;<sub>6</sub> = 4.1667...</td>
				<td>Defines the level of skill of a game. The skill chain defines the skill difference between the lowest and highest possible skill levels that can be achieved.</td>
			</tr>
			<tr>
				<td>Draw probability (𝛆)</td>
				<td>10%</td>
				<td>The chance of a draw occuring. Even for games where draws are technically impossible, this value is still needed for calculations such as finding match set-ups that are likely to be very close to drawing.</td>
			</tr>
		</tbody>
	</table>
</template>

<template id="about-website">
	<h5 class="text-xl my-3">Credits</h5>
	<p>	
		This site's web interface was created using <a href="https://kit.svelte.dev/">SvelteKit</a>
		and <a href="https://daisyui.com/">DaisyUI</a>, while
		<a href="https://plotly.com/javascript/">Plotly.js</a> was used for the graphs.
	</p>
	<p>
		The backend is written in <a href="https://www.python.org/">Python</a> and uses
		<a href="https://www.djangoproject.com/">Django</a> combined with
		<a href="https://www.django-rest-framework.org/">Django REST framework</a>.
		The skill algorithm's calculations are implemented by the
		<a href="https://github.com/moserware/Skills">Skills</a> library.
	</p>
	<p>
		This site was created by me, <a href="https://samuller.net/">Simon Muller</a>. It's source code
		is openly available on <a href="https://github.com/samuller/rankings-django">Github</a>.
	</p>
</template>

<style lang="postcss">
	table {
		@apply bg-gray-500;
	}

	th {
		@apply bg-gray-900;
		color: white;
	}

	tr:nth-of-type(odd) {
		@apply bg-gray-700;
	}

	td, th {
		padding: 10px;
	}

	td:nth-child(2) {
		text-align:center;
	}
</style>