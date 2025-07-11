import * as d3 from 'd3';
import { allMechanics, similarity, type BoardGame } from "$lib";

type Position = { x: number; y: number };

export function renderForceGraph(width: number, height: number, nodes: BoardGame[], onHover: (node: (BoardGame & Position) | null) => void): [HTMLCanvasElement, (search: string | undefined, goto?: { x: number; y: number }) => void] {
    const MIN_LINK_SIMILARITY = 0.75;
    
    const canvas = d3.create('canvas').style('display', 'block').style('width', '100%').style('height', '100%').node() as HTMLCanvasElement;
    canvas.width = width;
    canvas.height = height;
    const ctx = canvas.getContext('2d')!;

    const nodesWithPosition = nodes as (BoardGame & Position)[];
    const [links, linkMap] = generateLinks(nodes) as unknown as [
        { source: BoardGame & Position; target: BoardGame & Position; shared: string[]; similarity: number }[],
        Map<string, { source: BoardGame & Position; target: BoardGame & Position; shared: string[]; similarity: number }[]>
    ];

    const simulation = d3
		.forceSimulation(nodes)
		.force(
			'link',
			d3
				.forceLink(links.filter((link) => link.similarity >= MIN_LINK_SIMILARITY))
				.id((d: any) => d.id)
				.distance(50)
				.strength((link) => (link.similarity - MIN_LINK_SIMILARITY))
		)
		.force('charge', d3.forceManyBody().strength(-100))
		.force('center', d3.forceCenter(width / 2, height / 2))
		.force(
			'collision',
			d3.forceCollide().radius((d) => nodeRadius(d as BoardGame) + 4)
		);

    let transform = d3.zoomIdentity;
    let selectedGame: (BoardGame & Position) | null = null;
    let searchedGame: string | undefined = undefined;

    const zoom = d3.zoom<HTMLCanvasElement, unknown>()
	    .scaleExtent([0.1, 5])
	    .on('zoom', (event) => {
	    	transform = event.transform;
	    	draw(searchedGame);
	    })

    d3.select(canvas).call(zoom);

    simulation.on('tick', () => draw(searchedGame));

    canvas.addEventListener('mousemove', (e) => {
    	const rect = canvas.getBoundingClientRect();
    	const mouseX = (e.clientX - rect.left - transform.x) / transform.k;
    	const mouseY = (e.clientY - rect.top - transform.y) / transform.k;

    	let found = false;
    	for (const node of nodesWithPosition) {
    		const r = nodeRadius(node) + 4;
    		const dx = mouseX - node.x;
    		const dy = mouseY - node.y;
    		if (dx * dx + dy * dy < r * r) {
    			onHover({
    				...node,
    				x: e.pageX,
    				y: e.pageY
    			});
    			found = true;
    			break;
    		}
    	}
    	if (!found) onHover(null);
    });

    canvas.addEventListener('mouseleave', () => {
        onHover(null);
    });

    canvas.addEventListener('click', (e) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = (e.clientX - rect.left - transform.x) / transform.k;
        const mouseY = (e.clientY - rect.top - transform.y) / transform.k;
        for (const node of nodesWithPosition) {
            const r = nodeRadius(node);
            const dx = mouseX - node.x;
            const dy = mouseY - node.y;
            if (dx * dx + dy * dy < r * r) {
                selectedGame = selectedGame?.id === node.id ? null : node;
                draw(searchedGame);
                return;
            }
        }
    });

    function draw(search?: string, goto?: { x: number; y: number }, showMechanics: boolean[] = Array(allMechanics.length).fill(true)) {
        searchedGame = search;

        if (goto) {
            const scale = 3;
            const tx = width / 2 - goto.x * scale;
            const ty = height / 2 - goto.y * scale;
            transform = d3.zoomIdentity.translate(tx, ty).scale(scale);
            d3.select(canvas).call(zoom.transform, transform);
        }

        ctx.save();
	    ctx.clearRect(0, 0, canvas.width, canvas.height);
	    ctx.translate(transform.x, transform.y);
	    ctx.scale(transform.k, transform.k);

        if (selectedGame) {
            const linkedNodes = linkMap.get(selectedGame.id)!;
            for (const link of linkedNodes) {
                if (link.similarity >= MIN_LINK_SIMILARITY) {
                    ctx.lineWidth = (link.similarity - 0.65) * 15;
                    ctx.beginPath();
                    ctx.strokeStyle = '#69b3a2';
                    ctx.globalAlpha = link.similarity;
                    ctx.moveTo(link.source.x, link.source.y);
                    ctx.lineTo(link.target.x, link.target.y);
                    ctx.stroke();
                }
            }
        }
        ctx.globalAlpha = 1;

	    for (const node of nodesWithPosition) {
            if (!showMechanics.some((show, index) => show && node.mechanics.includes(allMechanics[index]))) {
                continue;
            }
	    	ctx.beginPath();
	    	ctx.arc(node.x, node.y, nodeRadius(node), 0, 2 * Math.PI);
            if (selectedGame){
                const linked = linkMap.get(selectedGame.id)?.find((link) => link.source.id === node.id || link.target.id === node.id);
                if (linked) {
                    ctx.fillStyle = linked.similarity < MIN_LINK_SIMILARITY ? '#999' : '#69b3a2';
                } else {
                    ctx.fillStyle = '#999';
                }
                if (selectedGame.id === node.id) {
                    ctx.fillStyle = '#3B82F6';
                }
            } else {
                ctx.fillStyle = '#69b3a2';
            }
            if (search === node.id) {
                ctx.fillStyle = '#F97316';
            }
	    	ctx.fill();
	    	ctx.strokeStyle = selectedGame?.id === node.id ? '#000' : '#fff';
	    	ctx.lineWidth = 1.5;
	    	ctx.stroke();
	    }

	    ctx.restore();
    }

    return [canvas, draw];
}

function generateLinks(nodes: BoardGame[]) {
    const links: { source: string; target: string; shared: string[] }[] = [];
    const linkMap = new Map<string, { source: string; target: string; shared: string[] }[]>();
    
    for (const nodeA of nodes) {
        linkMap.set(nodeA.id, []);
        for (const nodeB of nodes) {
            if (nodeA.id !== nodeB.id) {
                const shared = nodeA.mechanics.filter((item) => nodeB.mechanics.includes(item));
                if (shared.length > 0) {
                    const link = { source: nodeA.id, target: nodeB.id, shared, similarity: similarity(nodeA.mechanicsVector, nodeB.mechanicsVector) };
                    links.push(link);
                    linkMap.get(nodeA.id)?.push(link);
                }
            }
        }
    }

    return [links, linkMap];
}

function nodeRadius(node: BoardGame): number {
    return Math.max(1, Math.sqrt(node.popularity) / 8);
}