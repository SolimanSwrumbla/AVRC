<script lang="ts">
	import BoardGameGraph from '$components/BoardGameGraph.svelte';
	import ChordDependency from '$components/ChordDependency.svelte';
	import ScatterPlot from '$components/ScatterPlot.svelte';
	import StackedBarChart from '$components/StackedBarChart.svelte';

	const { data } = $props();
</script>

<div class="container">
	<div class="graph-container">
		{#await data.games then games}
			<BoardGameGraph {games} />
		{/await}
	</div>
	<div class="graph-container">
		{#await data.games then games}
			<StackedBarChart {games} />
		{/await}
	</div>
	<div class="graph-container">
		{#await data.games then games}
			<ChordDependency {games} />
		{/await}
	</div>
	<div class="graph-container">
		{#await data.games then games}
			<ScatterPlot {games} />
		{/await}
	</div>
</div>

<style>
	.container {
		scroll-snap-type: y mandatory;
		scroll-behavior: smooth;
		overflow-y: scroll;
		height: 100dvh;
		width: 100%;
		display: flex;
		flex-direction: column;
	}

	.graph-container {
		position: relative;
		scroll-snap-align: start;
		width: 100%;
		min-height: 100%;
	}
</style>
