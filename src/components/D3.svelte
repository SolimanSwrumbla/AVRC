<script lang="ts">
	const { setup }: { setup: (element: HTMLElement) => Promise<void> } = $props();

	function init(element: HTMLElement) {
		setup(element);
	}
</script>

<div {@attach init}></div>

<style>
	div {
		width: 100%;
		height: 100%;
		overflow: var(--overflow);
		display: flex;
		justify-content: center;
		align-items: center;
	}
</style>
