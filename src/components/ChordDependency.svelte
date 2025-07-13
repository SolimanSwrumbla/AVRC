<script lang="ts">
	import { mechanicColors, type BoardGame } from '$lib';
	import D3 from './D3.svelte';
	import { select, chord, ribbon, arc, scaleOrdinal, schemeCategory10, descending, max as d3Max } from 'd3';

	export let games: BoardGame[];

	async function setup(container: HTMLElement) {
		const width = 700;
		const height = 700;
		const outerRadius = Math.min(width, height) * 0.5 - 40;
		const innerRadius = outerRadius - 20;

		// 1. Conta occorrenze di ogni meccanica
		const countMap = new Map<string, number>();
		for (const g of games) {
			for (const m of g.mechanics ?? []) {
				countMap.set(m, (countMap.get(m) || 0) + 1);
			}
		}

		// 2. Prendi le top 20 meccaniche per frequenza
		const topMechanics = Array.from(countMap.entries())
			.sort((a, b) => b[1] - a[1])
			.slice(0, 20)
			.map(([m]) => m);

		// 3. Mappa meccanica -> indice
		const mechIndex = new Map<string, number>();
		topMechanics.forEach((m, i) => mechIndex.set(m, i));

		const n = topMechanics.length;
		// 4. Costruisci matrice NxN co‑occorrenze
		const matrix: number[][] = Array.from({ length: n }, () => Array(n).fill(0));
		for (const g of games) {
			// filtra solo meccaniche in top20 e uniche
			const mechs = Array.from(new Set(g.mechanics ?? [])).filter((m) => mechIndex.has(m));
			for (let i = 0; i < mechs.length; i++) {
				for (let j = i + 1; j < mechs.length; j++) {
					const a = mechIndex.get(mechs[i])!;
					const b = mechIndex.get(mechs[j])!;
					matrix[a][b] += 1;
					matrix[b][a] += 1;
				}
			}
		}

		// 5. Palette colori
		const colors = topMechanics.map((m) => mechanicColors?.[m] || schemeCategory10[m.length % 10]);

		const color = scaleOrdinal().domain(topMechanics).range(colors);

		// 6. Layout chord
		const chords = chord().padAngle(0.05).sortSubgroups(descending)(matrix);

		const ribbonGen = ribbon().radius(innerRadius);
		const arcGen = arc().innerRadius(innerRadius).outerRadius(outerRadius);

		// 7. SVG setup
		const svg = select(container)
			.append('svg')
			.attr('viewBox', [-width / 2, -height / 2, width, height].join(' '))
			.attr('font-size', 10)
			.attr('font-family', 'sans-serif')
			.attr('width', '85%')
			.attr('height', '85%')
			.attr('overflow', 'visible');

		// 8. Gruppi esterni (archi)
		const group = svg.append('g').selectAll('g').data(chords.groups).enter().append('g');

		group
			.append('path')
			.attr('fill', (d) => color(topMechanics[d.index]))
			.attr('d', arcGen);

		group
			.append('text')
			.each((d) => (d.angle = (d.startAngle + d.endAngle) / 2))
			.attr('dy', '.35em')
			.attr(
				'transform',
				(d) =>
					`rotate(${(d.angle * 180) / Math.PI - 90}) translate(${outerRadius + 5})` +
					(d.angle > Math.PI ? ' rotate(180)' : '')
			)
			.attr('text-anchor', (d) => (d.angle > Math.PI ? 'end' : 'start'))
			.text((d) => topMechanics[d.index]);

		// 9. Ribbons (co‑occorrenze)
		svg
			.append('g')
			.attr('fill-opacity', 0.7)
			.selectAll('path')
			.data(chords)
			.enter()
			.append('path')
			.attr('d', ribbonGen)
			.attr('fill', (d) => color(topMechanics[d.source.index]))
			.attr('stroke', (d) => color(topMechanics[d.source.index]));
	}
</script>

<D3 {setup} />
