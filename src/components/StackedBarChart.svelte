<script lang="ts">
	import { mechanicColors, type BoardGame } from '$lib';
	import D3 from './D3.svelte';
	import Tooltip from './Tooltip.svelte'; // assicurati di averlo o crealo
	import { select, scaleBand, scaleLinear, axisBottom, axisLeft, max } from 'd3';

	export let games: BoardGame[];

	const currentYear = 2020;
	const years = Array.from({ length: 20 }, (_, i) => currentYear - 19 + i);

	let hoveredBar: BoardGame | null = null;

	async function setup(container: HTMLElement) {
		const margin = { top: 40, right: 200, bottom: 50, left: 60 };
		const width = window.innerWidth * 0.75 - margin.left - margin.right;
		const height = window.innerHeight * 0.75 - margin.top - margin.bottom;

		const svg = select(container)
			.append('svg')
			.attr('width', width + margin.left + margin.right)
			.attr('height', height + margin.top + margin.bottom)
			.attr('overflow', 'visible')
			.append('g')
			.attr('transform', `translate(${margin.left},${margin.top})`);

		// Preparazione dati come prima
		const data = years.map((year) => ({
			year: year.toString(),
			total: 0,
			prevalentMech: 'N/A',
			prevalentCount: 0,
			otherCount: 0,
			mostPopularGame: null as BoardGame | null,
			mechanicCounts: new Map<string, number>(),
		}));

		const yearIndex = new Map<string, number>();
		data.forEach((d, i) => yearIndex.set(d.year, i));

		for (const game of games) {
			const y = game.publishYear;
			if (!years.includes(y)) continue;

			const idx = yearIndex.get(y.toString())!;
			data[idx].total++;

			for (const mech of game.mechanics ?? []) {
				const prev = data[idx].mechanicCounts.get(mech) || 0;
				data[idx].mechanicCounts.set(mech, prev + 1);
			}

			if (!data[idx].mostPopularGame || game.averageRating > data[idx].mostPopularGame.userRatings) {
				data[idx].mostPopularGame = game;
			}
		}

		for (const d of data) {
			let top = 'N/A',
				topCount = -1;
			for (const [mech, c] of d.mechanicCounts) {
				if (c > topCount) {
					top = mech;
					topCount = c;
				}
			}
			d.prevalentMech = top;
			d.prevalentCount = topCount > 0 ? topCount : 0;
			d.otherCount = d.total - d.prevalentCount;
		}

		const x = scaleBand()
			.domain(data.map((d) => d.year))
			.range([0, width])
			.padding(0.1);

		const y = scaleLinear()
			.domain([0, max(data, (d) => d.total) || 0])
			.range([height, 0]);

		const bars = svg
			.selectAll('g.bar')
			.data(data)
			.enter()
			.append('g')
			.attr('class', 'bar')
			.attr('transform', (d) => `translate(${x(d.year)},0)`);

		// Parte "Altro"
		bars
			.append('rect')
			.on('mousemove', (event, d) => {
				const [mx, my] = [event.clientX, event.clientY];
				console.log(mx, my, hoveredBar);
				hoveredBar = { ...d.mostPopularGame, x: mx, y: my } as unknown as BoardGame;
			})
			.on('mouseout', () => {
				hoveredBar = null;
			})
			.attr('y', (d) => y(d.total)) // base superiore della barra "Altro"
			.attr('height', (d) => y(0) - y(d.otherCount)) // differenza tra base e 0
			.attr('width', x.bandwidth())
			.attr('fill', '#8896A5');

		// Parte "Prevalente" con eventi mouseover/out
		bars
			.append('rect')
			.attr('x', 0)
			.attr('y', (d) => y(d.prevalentCount))
			.attr('height', (d) => y(d.otherCount) - y(d.total))
			.attr('width', x.bandwidth())
			.attr('fill', (d) => mechanicColors[d.prevalentMech] || '#999999')
			.on('mousemove', (event, d) => {
				const [mx, my] = [event.clientX, event.clientY];
				console.log(mx, my, hoveredBar);
				hoveredBar = { ...d.mostPopularGame, x: mx, y: my } as unknown as BoardGame;
			})
			.on('mouseout', () => {
				hoveredBar = null;
			});

		// Assi
		svg
			.append('g')
			.attr('transform', `translate(0,${height})`)
			.call(axisBottom(x).tickValues(data.map((d) => d.year).filter((_, i) => i % 2 === 1)))
			.selectAll('text')
			.attr('font-size', '24px');

		svg.append('g').call(axisLeft(y)).selectAll('text').attr('font-size', '24px');

		// Titolo
		svg
			.append('text')
			.attr('x', width / 2)
			.attr('y', -15)
			.attr('text-anchor', 'middle')
			.style('font-size', '32px')
			.text('Giochi pubblicati per anno (meccanica prevalente)');

		// LEGGENDA in alto a destra
		const legend = svg.append('g').attr('transform', `translate(${width + 20}, 0)`);

		const mechanics = Array.from(new Set(data.map((d) => d.prevalentMech))).filter((m) => m !== 'N/A');
		mechanics.forEach((mech, i) => {
			const g = legend.append('g').attr('transform', `translate(0, ${i * 25})`);
			g.append('rect').attr('width', 24).attr('height', 24).attr('fill', mechanicColors[mech]);
			g.append('text').attr('x', 32).attr('y', 20).style('font-size', '24px').text(mech);
		});

		const gAltro = legend.append('g').attr('transform', `translate(0, ${mechanics.length * 20 + 10})`);
		gAltro.append('rect').attr('width', 24).attr('height', 24).attr('fill', '#8896A5');
		gAltro.append('text').attr('x', 32).attr('y', 18).style('font-size', '24px').text('Altro');
	}
</script>

<D3 {setup} --overflow="visible" />

{#if hoveredBar}
	<Tooltip game={hoveredBar} --top={hoveredBar.y! + 10 + 'px'} --left={hoveredBar.x! + 10 + 'px'} />
{/if}
