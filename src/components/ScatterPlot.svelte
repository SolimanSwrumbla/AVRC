<script lang="ts">
	import { select, scaleLinear, axisBottom, axisLeft, line, extent } from 'd3';
	import { mechanicColors, type BoardGame } from '$lib';
	import D3 from './D3.svelte';
	import Tooltip from './Tooltip.svelte';
	import GameSearch from './GameSearch.svelte';

	export let games: BoardGame[] = [];
	let hoveredGame: { game: BoardGame; x: number; y: number } | null = null;

	function linearRegression(x: number[], y: number[]) {
		const n = x.length;
		const sumX = x.reduce((a, b) => a + b, 0);
		const sumY = y.reduce((a, b) => a + b, 0);
		const sumXY = x.reduce((acc, val, i) => acc + val * y[i], 0);
		const sumX2 = x.reduce((acc, val) => acc + val * val, 0);

		const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
		const intercept = (sumY - slope * sumX) / n;

		return { slope, intercept };
	}

	function getEfficientFrontier(games: BoardGame[]): Set<string> {
		const sorted = [...games].sort((a, b) => a.difficulty - b.difficulty);

		const frontier = new Set<string>();
		let maxRatingSoFar = -Infinity;

		for (const game of sorted) {
			if (game.averageRating > maxRatingSoFar) {
				frontier.add(game.id);
				maxRatingSoFar = game.averageRating;
			}
		}

		return frontier;
	}

	function genColor(game: BoardGame, efficientFrontier: Set<string>): string {
		if (efficientFrontier.has(game.id)) {
			return '#ff7f0e';
		}
		return '#4477AA';
	}

	async function setup(container: HTMLElement) {
		if (!games.length) return;

		const efficientFrontier = getEfficientFrontier(games);

		const margin = { top: 40, right: 20, bottom: 50, left: 60 };
		const width = window.innerWidth * 0.75 - margin.left - margin.right;
		const height = window.innerHeight * 0.75 - margin.top - margin.bottom;

		const svg = select(container)
			.append('svg')
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom)
			.attr('overflow', 'visible');

		const plotArea = svg.append('g').attr('transform', `translate(${margin.left},${margin.top})`);

		// Estrai dati validi (non null/undefined)
		const filtered = games.filter(
			(g) =>
				g.difficulty !== null && g.difficulty !== undefined && g.averageRating !== null && g.averageRating !== undefined
		);

		const xVals = filtered.map((g) => +g.difficulty);
		const yVals = filtered.map((g) => +g.averageRating);

		const xScale = scaleLinear()
			.domain(extent(xVals) as [number, number])
			.nice()
			.range([0, width]);

		const yScale = scaleLinear()
			.domain(extent(yVals) as [number, number])
			.nice()
			.range([height, 0]);

		// Assi
		plotArea
			.append('g')
			.attr('transform', `translate(0,${height})`)
			.call(axisBottom(xScale))
			.style('font-size', '24px');

		plotArea.append('g').call(axisLeft(yScale)).style('font-size', '24px');

		// Etichette assi
		svg
			.append('text')
			.attr('x', margin.left + width / 2)
			.attr('y', height + margin.top + 60)
			.attr('text-anchor', 'middle')
			.attr('font-size', '32px')
			.text('Complessità del gioco');

		svg
			.append('text')
			.attr('x', -(margin.top + height / 2))
			.attr('y', 5)
			.attr('transform', 'rotate(-90)')
			.attr('text-anchor', 'middle')
			.attr('font-size', '32px')
			.text('Valutazione media');

		// Punti scatter
		plotArea
			.selectAll('circle')
			.data(filtered)
			.enter()
			.append('circle')
			.attr('cx', (d) => xScale(d.difficulty))
			.attr('cy', (d) => yScale(d.averageRating))
			.attr('r', 4)
			.attr('fill', (d) => genColor(d, efficientFrontier))
			.attr('opacity', 0.7)
			.on('mouseenter', (event, d) => {
				hoveredGame = {
					game: d,
					x: event.pageX,
					y: event.pageY,
				};
			})
			.on('mousemove', (event) => {
				hoveredGame = { ...hoveredGame!, x: event.pageX, y: event.pageY };
			})
			.on('mouseleave', () => {
				hoveredGame = null;
			});

		// Calcolo regressione lineare
		const { slope, intercept } = linearRegression(xVals, yVals);

		// Linea di regressione
		const lineFunc = line<number>()
			.x((x) => xScale(x))
			.y((x) => yScale(slope * x + intercept));

		const xDomain = xScale.domain();

		plotArea
			.append('path')
			.datum([xDomain[0], xDomain[1]])
			.attr('fill', 'none')
			.attr('stroke', 'red')
			.attr('stroke-width', 2)
			.attr('d', lineFunc);
	}
</script>

<D3 {setup} --overflow="visible" />
{#if hoveredGame}
	<Tooltip game={hoveredGame.game} --top={hoveredGame.y + 10 + 'px'} --left={hoveredGame.x + 10 + 'px'} />
{/if}
