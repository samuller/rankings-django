<!--
@component
A wrapper around the Plotly.js plotting library.

This is not really a generic wrapper, but more a place for all code shared among our other types of plots.

Usage:
	```tsx
	<PlotlyWrapper></PlotlyWrapper>
	```
-->
<script lang="ts">
	import { browser } from '$app/environment';
	import { onMount } from 'svelte';

	// Data to plot.
	export let data: { x: number[]; y: number[] } = { x: [], y: [] };
	// Options for hard-coding or auto-scaling axes.
	export let initRangeX: [number | null, number | null] | null = [null, null];
	export let yRangeMinMax: (number | null)[] = [null, null];
	// Plot titles.
	export let title = '';
	export let xAxisTitle = '';
	export let yAxisTitle = '';

	export let showRangeSlider = false;
	export let xAxisFixedRange = false;
	export let chartType = 'lines+markers';
	export let fill = '';
	export let shapes: any[] = [];
	export let annotations: any[] = [];
	export let smoothing = 0;
	export let dtick = 1;

	let loadingMessage = 'Loading charting library...';

	// Add 10% marging if near edge of axes.
	const axisMargin = 0.1;
	const gridColor = '#bbb';
	const bgColor = 'rgba(0,0,0,0)';

	let loadingPlotlyLibrary = true;
	let plotElement: HTMLElement;
	// A mutex to prevent us from triggering a relayout while one is already in progress.
	let busyRelayout = false;

	/**
	 * Get values in a sorted list that are closest to the given value.
	 * See: https://stackoverflow.com/questions/4431259/formal-way-of-getting-closest-values-in-array-in-javascript-given-a-value-and-a
	 * @param sorted_array A sorted array of numbers.
	 * @param value Value to get close to.
	 */
	const getClosestValues = function (sorted_array: number[], value: number): number[] {
		var lo = -1,
			hi = sorted_array.length;
		while (hi - lo > 1) {
			var mid = Math.round((lo + hi) / 2);
			if (sorted_array[mid] <= value) {
				lo = mid;
			} else {
				hi = mid;
			}
		}
		if (sorted_array[lo] == value) hi = lo;
		// Either value might be undefined if value is beyond the edge limits.
		return [sorted_array[lo], sorted_array[hi]];
	};

	const getClosestValid = function (sorted_array: number[], value: number): number {
		const closest = getClosestValues(sorted_array, value);
		return closest[0] ?? closest[1];
	};

	/**
	 * We do our own custom updating of range limits.
	 *
	 * Plotly.js doesn't yet have a config for this, see: https://github.com/plotly/plotly.js/issues/1876
	 * Though one might soon (within weeks?) be implemented: https://github.com/plotly/plotly.js/pull/6547
	 * Update: see xaxis.minallowed & xaxis.maxallowed in plotly.js v2.26.0.
	 */
	const limitXAxisScrolling = function (data_x: number[], data_y: number[], x_range: number[]) {
		let new_x_range = x_range;
		let new_layout: { [key: string]: any } = {};

		// Add 10% buffer if near edge of x-axes.
		const x_width = x_range[1] - x_range[0];
		const x_axis_buffer_dist = x_width * axisMargin;
		const min_x = data_x[0];
		const max_x = data_x[data_x.length - 1];
		if (x_range[0] < min_x) {
			const new_min_x = min_x - x_axis_buffer_dist;
			new_x_range = [new_min_x, new_min_x + x_width];
		}
		if (x_range[1] > max_x) {
			const new_max_x = max_x + x_axis_buffer_dist;
			new_x_range = [new_max_x - x_width, new_max_x];
		}
		new_layout['xaxis.range'] = new_x_range;

		const data_y_subset = data_y.slice(
			data_x.indexOf(getClosestValid(data_x, new_x_range[0])),
			data_x.indexOf(getClosestValid(data_x, new_x_range[1])) + 1
		);
		const min_y_data = Math.min(...data_y_subset);
		const max_y_data = Math.max(...data_y_subset);

		const yRangeMin = yRangeMinMax[0];
		const yRangeMax = yRangeMinMax[1];
		// Add 10% buffer if near edge of y-axes.
		const y_axis_buffer_dist = (max_y_data - min_y_data) * axisMargin;
		const min_y = min_y_data - y_axis_buffer_dist;
		const max_y = max_y_data + y_axis_buffer_dist;
		new_layout['yaxis.range'] = [yRangeMin != null ? yRangeMin - y_axis_buffer_dist : min_y, max_y];

		return new_layout;
	};

	/**
	 * Our custom handling when user scrolls interface.
	 */
	const onRelayout = async function (
		Plotly: any,
		data_x: number[],
		data_y: number[],
		relayoutData: any
	) {
		// We currently only have handling for changes to the x-axis.
		if (!('xaxis.range[0]' in relayoutData && 'xaxis.range[1]' in relayoutData)) {
			return;
		}
		const x_range = [relayoutData['xaxis.range[0]'], relayoutData['xaxis.range[1]']];
		const new_layout: { [key: string]: any } = limitXAxisScrolling(data_x, data_y, x_range);

		if (!busyRelayout) {
			Plotly.relayout(plotElement, new_layout).then(() => {
				busyRelayout = false;
			});
			busyRelayout = true;
		}
	};

	const setupPlot = async function () {
		// @ts-ignore
		const Plotly = window?.Plotly;
		// Check if library has been loaded.
		if (!Plotly) {
			return;
		}
		loadingPlotlyLibrary = false;

		// const domElement = document.getElementById('tester');
		const data_x = data.x;
		const data_y = data.y;
		const traces = [
			{
				x: data_x,
				y: data_y,
				mode: chartType,
				...(fill && { fill: fill }),
				...(smoothing && { line: { shape: 'spline', smoothing: smoothing } })
			}
		];
		const layout = {
			// b: 0 -> Causes bottom tick labels to be cut-off.
			// t: 0 -> Causes title to be cut-off.
			margin: { t: 30, b: 40 },
			paper_bgcolor: bgColor,
			plot_bgcolor: bgColor,
			dragmode: 'pan',
			// https://stackoverflow.com/questions/47892127/succinct-concise-syntax-for-optional-object-keys-in-es6-es7
			...(title && { title: { text: title } }),
			xaxis: {
				showgrid: false,
				dtick: dtick,
				gridcolor: gridColor,
				// Available since plotly.js v2.26.0. We don't use it yet as it triggers scaling when scrolling
				// past limits.
				// minallowed: 0,
				// maxallowed: 100,
				...(true && { range: initRangeX }),
				...(xAxisTitle && { title: { text: xAxisTitle } }),
				...(showRangeSlider && { rangeslider: { visible: true } }),
				...(xAxisFixedRange && { fixedrange: true })
			},
			// , autorange: true
			yaxis: {
				gridcolor: gridColor,
				fixedrange: true,
				hoverformat: '.2f',
				...(yAxisTitle && { title: { text: yAxisTitle } })
			},
			...(shapes && { shapes: shapes }),
			...(annotations && { annotations: annotations })
		};
		const config = {
			// staticPlot: true,
			responsive: true,
			showAxisDragHandles: false,
			scrollZoom: false,
			displayModeBar: false
		};
		Plotly.newPlot(plotElement, traces, layout, config);

		// await Plotly.react(plotElement, data, layout, config);
		// await Plotly.relayout(plotElement, {
		//	 "yaxis.autorange": true,
		// });

		// @ts-ignore Plotly has on() that matches jQuery.
		plotElement.on('plotly_relayout', async function (relayoutData) {
			await onRelayout(Plotly, data_x, data_y, relayoutData);
		});
	};

	// Update plot if "data" prop changes.
	$: if (data && plotElement) {
		setupPlot();
	}

	// Ensure code only runs in browser (and not on server).
	onMount(() => {
		// When charting library takes very long to load, we try to suggest that something's up.
		// It might just be very slow, but it could also be blocked or require a page refresh.
		setTimeout(() => {
			loadingMessage = 'Loading charting library... hopefully...';
		}, 10000);
	});
</script>

<svelte:head>
	<script
		on:load|once={setupPlot}
		src="https://cdn.plot.ly/plotly-2.26.0.min.js"
		charset="utf-8"
	></script>
</svelte:head>

{#if browser && !('Plotly' in window) && loadingPlotlyLibrary}
	<div>{loadingMessage}</div>
{/if}
<!-- style="width:600px;height:250px;" -->
<div bind:this={plotElement} />

<style lang="postcss">
	/*
	  Disable plotly preventing text selection.
	  See: https://community.plotly.com/t/selecting-copying-axis-label-text-and-table-cell-contents/47805
	*/
	:global(.plotly .user-select-none) {
		user-select: text !important;
	}
	/* Allow selecting text in title layer. */
	:global(.plotly .infolayer) {
		pointer-events: all;
	}

	/*
	  Disable plotly's rangeSlider's handle bars.
	  See: https://community.plotly.com/t/hide-the-handler-grabarea-of-rangeslider/17437/2
	*/
	:global(.plotly .rangeslider-grabber-min) {
		display: none;
	}
	:global(.plotly .rangeslider-grabber-max) {
		display: none;
	}
	/* rangeslider-container */
	:global(.rangeslider-mask-min) {
		user-select: none;
		pointer-events: none;
	}
	:global(.rangeslider-mask-max) {
		user-select: none;
		pointer-events: none;
	}
</style>
