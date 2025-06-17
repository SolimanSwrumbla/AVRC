import { loadBordGamesFromCsv, topN } from "$lib";

export async function load({ fetch }) {
    const games = fromAsync(loadBordGamesFromCsv(fetch, '/games.csv', '/mechanics.csv')).then((games) => topN(games, 2500, (g) => g.userRatings));
    return { games };
}

async function fromAsync<T>(asyncIterable: AsyncGenerator<T>): Promise<T[]> {
    const result: T[] = [];
    for await (const item of asyncIterable) {
        result.push(item);
    }
    return result;
}