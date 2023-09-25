<script lang="ts">
	import { onMount } from 'svelte';
	import { Card, TableWrap, Tabs } from "$lib/components";
	import { activitiesAbout, navTitle } from '../../store';

	let truekskillTab = {
		id: 'trueskill',
		title: 'Trueskill',
		content: 'Loading...',
	};
	let websiteTab = {
		id: 'website',
		title: 'Website',
		content: 'Loading...',
	};

	navTitle.set('');

	$: activityTabs = $activitiesAbout.filter((act) => act.about).map((act) => { return {
		id: act.url,
		title: act.name,
		// Adding some top spacing. 
		content: `<div class="mt-3"></div>${act.about}`,
	}});
	$: TABS = [truekskillTab, ...activityTabs, websiteTab];

	onMount(() => {
		truekskillTab.content = document.getElementById('about-trueskill')?.innerHTML ?? '';
		websiteTab.content = document.getElementById('about-website')?.innerHTML ?? '';
	});
</script>

<Card class="w-full lg:w-3/4 2xl:w-[calc(0.75*1536px)]">
    <Tabs data={TABS} hashPrefix=""></Tabs>
</Card>

<template id="about-trueskill">
	<p class="text-justify">
		These rankings are based on the <a href="http://research.microsoft.com/en-us/projects/trueskill/">Trueskill™</a>
		algorithm that was developed by Microsoft Research. The system represents skill as a Normal
		distribution which is updated after every game according to Bayesian probability.
	</p>
	<div class="bg-white">
		<img class="m-auto w-[228px] h-[200px]" alt="Normal distribution of skill" src="/images/skill-normal.jpg">
	</div>
	<p class="text-justify">
		By representing skill as a Normal distribution it is therefore described by two values, μ (mu) and
		σ (sigma) which respectively represent the player's average skill and the degree of uncertainty in the
		player's skill. After each game result the uncertainty will decrease, although it will never become zero
		as to allow for player skills that change over time. For ranking purposes the two values are combined
		into a single 'conservative skill estimate' (by using μ-3*σ) which represents a 99% confidence that a
		player has a skill higher than the given value.
	</p>
	<p class="text-justify">
		In Trueskill each game type needs to define a few crucial parameters that specify how games vary in skill
		level and how player progression and skill values are represented. These parameters are as follows:
	</p>
	<TableWrap
		columns={[
			{title: 'Parameter', classes: 'flex-1 pr-2'},
			{title: 'Default Value', classes: 'flex-1 pr-2 text-center'},
			{title: 'Meaning', classes: 'flex-[5_5_0%]'}
		]}
		rows={[
			['Skill value', '0 to 50', 'The skill value is defined to vary within this range so that values are more comfortable for people to work with (as opposed to values such as 0.008746 or 783,139).'],
			['Initial mean (𝛍<span class="align-bottom text-[0.4em]">O</span>)', '25', 'The mean of an average player and which is also assigned as the initial mean value to all new players.'],
			['Initial standard deviation (𝛔<span class="align-bottom text-[0.4em]">O</span>)', '<sup>25</sup>&frasl;<sub>3</sub> = 8.333...', 'The standard deviation of a completely new player about which no information is yet known.'],
			['Dynamics factor (𝛕)', '<sup>25</sup>&frasl;<sub>300</sub> = 0.08333...', "A variable added to a player's standard deviation before every game to account for the fact that player's skills change over time."],
			['Skill chain (𝛃)', '<sup>25</sup>&frasl;<sub>6</sub> = 4.1667...', 'Defines the level of skill of a game. The skill chain defines the skill difference between the lowest and highest possible skill levels that can be achieved.'],
			['Draw probability (𝛆)', '10%', 'The chance of a draw occuring. Even for games where draws are technically impossible, this value is still needed for calculations such as finding match set-ups that are likely to be very close to drawing.'],
		]}
	></TableWrap>
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
		This site was created by me, <a href="https://samuller.net/">Simon Muller</a>. Its source code
		is openly available on <a href="https://github.com/samuller/rankings-django">Github</a>.
	</p>
</template>

<style lang="postcss">
	p {
		@apply mt-3;
	}
</style>