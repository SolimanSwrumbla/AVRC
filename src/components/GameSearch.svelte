<script lang="ts">
	import { debounce, type BoardGame } from '$lib';

	let {
		query = '',
		selectedIndex = $bindable(),
		suggestions,
		placeholder = 'Search...',
	}: {
		query?: string;
		selectedIndex?: number;
		suggestions: BoardGame[];
		placeholder?: string;
	} = $props();

	let results: BoardGame[] = $state([]);
</script>

<div class="search-container">
	<input
		type="text"
		class="search-input"
		bind:value={query}
		{placeholder}
		oninput={debounce(() => {
			results = suggestions.filter((game) => game.name.toLowerCase().includes(query.toLowerCase()));
		}, 100)}
		disabled={selectedIndex !== undefined}
	/>

	{#if results.length > 0 && selectedIndex === undefined}
		<ul class="search-suggestions">
			{#each results as item, i}
				<li
					class:selected={selectedIndex === i}
					onclick={() => {
						selectedIndex = suggestions.findIndex((s) => s.id === item.id);
						query = item.name;
					}}
				>
					{item.name}
				</li>
			{/each}
		</ul>
	{/if}

	{#if selectedIndex !== undefined}
		<button
			class="clear-button"
			onclick={() => {
				selectedIndex = undefined;
				query = '';
				results = [];
			}}
		>
			&times;
		</button>
	{/if}
</div>

<style>
	.search-container {
		position: relative;
		display: flex;
		width: 100%;
	}

	.search-input {
		width: 100%;
		padding: 0.5rem;
		border: 1px solid #ccc;
		border-radius: 4px;
		font-size: 1rem;
		box-sizing: border-box;
	}

	.search-suggestions {
		position: absolute;
		top: 100%;
		left: 0;
		right: 0;
		margin-top: 0.25rem;
		max-height: 15rem;
		overflow-y: auto;
		border: 1px solid #ccc;
		border-radius: 4px;
		background-color: white;
		z-index: 10;
		list-style: none;
		padding: 0;
		margin: 0;
	}

	.search-suggestions li {
		padding: 0.5rem;
		cursor: pointer;
		transition: background-color 0.2s;
	}

	.search-suggestions li:hover {
		background-color: #f5f5f5;
	}

	.search-suggestions li.selected {
		background-color: #e0e0e0;
	}

	.clear-button {
		position: absolute;
		top: 0;
		right: 0;
		padding: 0.5rem;
		color: #d00;
		background: transparent;
		border: none;
		font-size: 1.25rem;
		cursor: pointer;
	}
</style>
