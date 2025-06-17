<script lang="ts">
	import { mechanicColors, type BoardGame } from '$lib';

	const { game }: { game: BoardGame } = $props();

	function stars(rating: number) {
		const scaled = rating / 2;
		const full = Math.floor(scaled);
		const half = scaled % 1 >= 0.5;
		const empty = 5 - full - (half ? 1 : 0);

		return {
			full,
			half,
			empty,
		};
	}
</script>

<div class="tooltip">
	<img src={game.imageUrl} alt={game.name} class="thumb" />
	<div class="info">
		<div class="title">
			<strong>{game.name}</strong>
			<span class="id">#{game.id}</span>
		</div>
		<div class="description">
			{#if game.description}
				{game.description.length > 100 ? game.description.slice(0, 100) + '...' : game.description}
			{:else}
				No description available.
			{/if}
		</div>
		<div class="mechanics-container">
			{#each game.mechanics as mechanic}
				<span
					class="mechanic"
					style="border: 1px solid {mechanicColors[mechanic]}; background-color: {mechanicColors[mechanic]}40"
					>{mechanic}</span
				>
			{/each}
		</div>
		<div class="rating">
			{#each Array(stars(game.averageRating).full) as _}
				<span class="star">★</span>
			{/each}
			{#if stars(game.averageRating).half}
				<span class="star half">★</span>
			{/if}
			{#each Array(stars(game.averageRating).empty) as _}
				<span class="star empty">★</span>
			{/each}
			<span class="value">({game.averageRating.toFixed(1)})</span>
		</div>
	</div>
</div>

<style>
	.tooltip {
		position: fixed;
		display: flex;
		align-items: flex-start;
		background: #fff;
		color: #333;
		border: 1px solid #ddd;
		border-radius: 8px;
		padding: 10px;
		font-size: 14px;
		line-height: 1.4;
		box-shadow: 0 6px 20px rgba(0, 0, 0, 0.1);
		pointer-events: none;
		top: var(--top);
		left: var(--left);
		transform: translate(10px, 10px);
		z-index: 1000;
		max-width: 400px;
	}

	.thumb {
		width: 100px;
		height: 100px;
		object-fit: cover;
		border-radius: 6px;
		margin-right: 10px;
		flex-shrink: 0;
	}

	.info {
		display: flex;
		flex-direction: column;
	}

	.title {
		display: flex;
		align-items: center;
		gap: 8px;
		font-size: 24px;
		margin-bottom: 4px;
	}

	.description {
		display: flex;
		text-wrap: wrap;
		align-items: center;
		gap: 8px;
		font-size: 16px;
		margin-bottom: 8px;
	}

	.mechanics-container {
		display: flex;
		flex-wrap: wrap;
		margin-bottom: 4px;
		gap: 6px 8px;
	}

	.mechanic {
		display: flex;
		text-wrap: wrap;
		align-items: center;
		font-size: 14px;
		padding: 2px 6px;
		border-radius: 6px;
		color: black;
	}

	.id {
		color: #888;
		font-size: 13px;
	}

	.rating {
		display: flex;
		align-items: center;
		gap: 4px;
	}

	.star {
		color: #fbc02d;
		font-size: 16px;
	}

	.star.empty {
		color: #ddd;
	}

	.star.half {
		color: #ddd;
		position: relative;
	}

	.star.half::after {
		content: '★';
		color: #fbc02d;
		position: absolute;
		left: 0;
		overflow: hidden;
		width: 50%;
	}

	.value {
		color: #666;
		font-size: 13px;
		margin-left: 6px;
	}
</style>
