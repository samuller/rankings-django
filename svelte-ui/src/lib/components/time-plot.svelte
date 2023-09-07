<!--
@component
A plot with time-based data on the x-axis that autoscales the y-range to fit visible data on screen.

Usage:
	```tsx
	<TimePlot></TimePlot>
	```
-->
<script lang="ts">
	import PlotlyWrapper from './plotly-wrapper.svelte';
</script>

<PlotlyWrapper {...$$props}></PlotlyWrapper>
