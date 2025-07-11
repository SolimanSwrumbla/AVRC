<script lang="ts">
	import BoardGameGraph from '$components/BoardGameGraph.svelte';

	const { data } = $props();
</script>

<div class="container">
	<div class="graph-container">
		{#await data.games then games}
			<BoardGameGraph {games} />
		{/await}
	</div>
	<div class="test"></div>
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

	.test {
		scroll-snap-align: start;
		min-height: 100%;
		width: 100%;
		background-color: red;
	}
</style>
