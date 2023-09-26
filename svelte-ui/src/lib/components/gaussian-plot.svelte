<!--
@component
A plot that shows a centered Gaussian with a fixed x-axis.

Usage:
	```tsx
	<GaussianPlot></GaussianPlot>
	```
-->
<script lang="ts">
	import PlotlyWrapper from './plotly-wrapper.svelte';

	export let mu;
	export let sigma;
	export let limits: [number, number] = [0, 100];
	export let steps = 100;
	export let verticalIndicators: { xPos: number; title: string }[] = [];

	$: annotations = verticalIndicators.map((indicator) => {
		return {
			x: indicator.xPos + 0.5,
			yref: 'paper',
			y: 0.99,
			text: indicator.title,
			textangle: '90',
			showarrow: false,
			font: {
				color: 'black',
				size: 12
			}
		};
	});

	$: shapes = verticalIndicators.map((indicator) => {
		return {
			type: 'line',
			x0: indicator.xPos,
			y0: 0,
			x1: indicator.xPos,
			yref: 'paper',
			y1: 1,
			line: {
				color: 'grey',
				width: 1.5,
				dash: 'dashdot'
			}
		};
	});

	const gaussian = function (mu: number, sigma: number, stepCount: number = 100) {
		var step = (limits[1] - limits[0]) / stepCount;
		var dataX = [];
		let dataY = [];
		for (var x = limits[0]; x < limits[1]; x += step) {
			var y =
				(1 / (sigma * Math.sqrt(2 * Math.PI))) *
				Math.pow(Math.E, -Math.pow(x - mu, 2) / (2 * sigma * sigma));
			dataX.push(x);
			// Turn normalised value into percentage.
			dataY.push(100 * y);
		}
		return { x: dataX, y: dataY };
	};

	const data = gaussian(mu, sigma, steps);
</script>

<PlotlyWrapper
	{data}
	{...$$restProps}
	initRangeX={limits}
	xAxisFixedRange={true}
	yRangeMinMax={[0, null]}
	chartType="scatter"
	fill="tozeroy"
	{shapes}
	{annotations}
	smoothing={1.0}
	dtick={5}
/>
