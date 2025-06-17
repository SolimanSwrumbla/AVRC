<script lang="ts">
	import { debounce, type BoardGame } from '$lib';
	import D3 from './D3.svelte';
	import Tooltip from './Tooltip.svelte';
	import { renderForceGraph } from '$lib/d3';
	import GameSearch from './GameSearch.svelte';

	const { games }: { games: BoardGame[] } = $props();
	let hoveredGame: (BoardGame & { x: number; y: number }) | null = $state(null);
	let searchedGameIndex: number | undefined = $state();
	let draw: (search?: string, goto?: { x: number; y: number }) => void = () => {};

	$effect(() =>
		draw(
			searchedGameIndex !== undefined ? games[searchedGameIndex].id : undefined,
			searchedGameIndex !== undefined ? { x: games[searchedGameIndex].x!, y: games[searchedGameIndex].y! } : undefined
		)
	);

	async function setup(element: HTMLElement) {
		const { width, height } = element.getBoundingClientRect();
		const [canvas, drawFn] = renderForceGraph(width, height, games, (node) => (hoveredGame = node));
		element.appendChild(canvas);
		draw = drawFn;

		const observer = new ResizeObserver(
			debounce((entries) => {
				for (const entry of entries) {
					const { width, height } = entry.contentRect;
					canvas.width = width;
					canvas.height = height;
					searchedGameIndex = undefined;
					draw(searchedGameIndex !== undefined ? games[searchedGameIndex].id : undefined);
				}
			}, 100)
		);

		observer.observe(element);
	}
</script>

<D3 {setup} --overflow="hidden" />
<div class="search-container">
	<GameSearch suggestions={games} bind:selectedIndex={searchedGameIndex} />
</div>
{#if hoveredGame}
	<Tooltip game={hoveredGame} --left={hoveredGame.x + 10 + 'px'} --top={hoveredGame.y + 10 + 'px'} />
{/if}

<style>
	.search-container {
		position: absolute;
		top: 10px;
		left: 10px;
	}
</style>
