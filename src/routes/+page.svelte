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
</div>

<style>
	.container {
		height: 100dvh;
		width: 100%;
		display: flex;
		flex-direction: column;
	}

	.graph-container {
		width: 100%;
		height: 100%;
	}
</style>
