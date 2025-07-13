import type { SimulationNodeDatum } from "d3";

export interface BoardGame extends SimulationNodeDatum {
    id: string;
    name: string;
    description: string;
    publishYear: number;
    difficulty: number;
    averageRating: number;
    userRatings: number;
    ownedByBoardGameGeekUsers: number;
    wantedByBoardGameGeekUsers: number;
    wishlistedByBoardGameGeekUsers: number;
    minPlayers: number;
    maxPlayers: number;
    mechanics: string[];
    mechanicsVector: number[];
    imageUrl?: string;
    popularity: number;
}

export async function loadMechanicsFromCsv(fetch: typeof globalThis.fetch, mechanicsUrl: string): Promise<Record<string, string[]>> {
    const response = await fetch(mechanicsUrl);
    if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`);
    }
    const text = await response.text();
    const [header, ...lines] = text.split('\n');
    const columns = parseCsvLine(header);
    const allMechanics = columns.slice(1);
    const mechanicsMap: Record<string, string[]> = {};
    for (const line of lines) {
        if (line.trim()) {
            const data = parseCsvLine(line);
            const gameId = data[columns.indexOf('BGGId')];
            const mechanics = allMechanics.filter((_, index) => data[index + 1] === '1');
            mechanicsMap[gameId] = mechanics;
        }
    }
    return mechanicsMap;
}

export async function* loadBordGamesFromCsv(fetch: typeof globalThis.fetch, gamesUrl: string, mechanicsUrl: string): AsyncGenerator<BoardGame> {
    const mechanics = await loadMechanicsFromCsv(fetch, mechanicsUrl);

    const response = await fetch(gamesUrl);
    if (!response.ok) {
        throw new Error(`Failed to fetch data: ${response.statusText}`);
    }
    
    const text = await response.text();
    const [header, ...lines] = text.split('\n');
    const columns = parseCsvLine(header);

    const id = columns.indexOf('BGGId');
    const name = columns.indexOf('Name');
    const description = columns.indexOf('Description');
    const yearPublished = columns.indexOf('YearPublished');
    const gameWeight = columns.indexOf('GameWeight');
    const avgRating = columns.indexOf('AvgRating');
    const userRatings = columns.indexOf('NumUserRatings');
    const numOwned = columns.indexOf('NumOwned');
    const numWant = columns.indexOf('NumWant');
    const numWish = columns.indexOf('NumWish');
    const minPlayers = columns.indexOf('MinPlayers');
    const maxPlayers = columns.indexOf('MaxPlayers');
    const imagePath = columns.indexOf('ImagePath');

    for (const line of lines) {
        if (line.trim()) {
            const data = parseCsvLine(line);
            yield {
                id: data[id],
                name: data[name],
                description: data[description],
                publishYear: parseInt(data[yearPublished], 10),
                difficulty: parseFloat(data[gameWeight]),
                averageRating: parseFloat(data[avgRating]),
                userRatings: parseInt(data[userRatings], 10),
                ownedByBoardGameGeekUsers: parseInt(data[numOwned], 10),
                wantedByBoardGameGeekUsers: parseInt(data[numWant], 10),
                wishlistedByBoardGameGeekUsers: parseInt(data[numWish], 10),
                minPlayers: parseInt(data[minPlayers], 10),
                maxPlayers: parseInt(data[maxPlayers], 10),
                mechanics: mechanics[data[id]] || [],
                mechanicsVector: mechanicsToVector(...(mechanics[data[id]] || [])),
                imageUrl: data[imagePath] || undefined,
                popularity: parseInt(data[userRatings], 10)
            };
        }
    }
}

function parseCsvLine(line: string): string[] {
  const result = [];
  let current = '';
  let insideQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      if (insideQuotes && line[i + 1] === '"') {
        current += '"';
        i++;
      } else {
        insideQuotes = !insideQuotes;
      }
    } else if (char === ',' && !insideQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);
  return result;
}

export function debounce<Args extends Array<unknown>>(fn: (...args: Args) => void, delay: number): (...args: Args) => void {
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    return (...args) => {
        if (timeoutId) {
            clearTimeout(timeoutId);
        }
        timeoutId = setTimeout(() => {
            fn(...args);
            timeoutId = null;
        }, delay);
    };
}

export function throttle(fn: () => void, delay: number): () => void {
    let lastCall = 0;
    return () => {
        const now = Date.now();
        if (now - lastCall >= delay) {
            fn();
            lastCall = now;
        }
    };
}

export function topN<T>(array: T[], n: number, key: (item: T) => number): T[] {
  return array
    .slice()
    .sort((a, b) => key(b) - key(a))
    .slice(0, n);
}

export function similarity(a: number[], b: number[]): number {
    const dot = a.reduce((sum, val, i) => sum + val * b[i], 0);
	const normA = Math.sqrt(a.reduce((sum, val) => sum + val * val, 0));
	const normB = Math.sqrt(b.reduce((sum, val) => sum + val * val, 0));
	return dot / (normA * normB || 1);
}

function mechanicsToVector(...mechanics: string[]): number[] {
    const vector = Array(allMechanics.length).fill(0);
    mechanics.forEach((mechanic) => {
        if (mechanicVectors[mechanic]) {
            vector[allMechanics.indexOf(mechanic)] = 1;
        }
    });
    return vector;
}

export const mechanicColors: Record<string, string> = {'Alliances': '#771155', 'Area Majority / Influence': '#AA4488', 'Auction/Bidding': '#CC99BB', 'Dice Rolling': '#CCCCCC', 'Hand Management': '#4477AA', 'Simultaneous Action Selection': '#77AADD', 'Trick-taking': '#117777', 'Hexagon Grid': '#44AAAA', 'Once-Per-Game Abilities': '#77CCCC', 'Set Collection': '#117744', 'Tile Placement': '#44AA77', 'Action Points': '#88CCAA', 'Investment': '#777711', 'Market': '#AAAA44', 'Square Grid': '#DDDD77', 'Stock Holding': '#774411', 'Victory Points as a Resource': '#AA7744', 'Enclosure': '#DDAA77', 'Pattern Building': '#771122', 'Pattern Recognition': '#AA4455', 'Modular Board': '#DD7788', 'Network and Route Building': '#a6cee3', 'Point to Point Movement': '#1f78b4', 'Melding and Splaying': '#b2df8a', 'Negotiation': '#33a02c', 'Trading': '#fb9a99', 'Push Your Luck': '#e31a1c', 'Income': '#fdbf6f', 'Race': '#ff7f00', 'Random Production': '#cab2d6', 'Variable Set-up': '#6a3d9a', 'Roll / Spin and Move': '#ffff99', 'Variable Player Powers': '#b15928', 'Action Queue': '#7fc97f', 'Bias': '#beaed4', 'Grid Movement': '#fdc086', 'Lose a Turn': '#ffff99', 'Programmed Movement': '#386cb0', 'Scenario / Mission / Campaign Game': '#f0027f', 'Voting': '#bf5b17', 'Events': '#666666', 'Paper-and-Pencil': '#771155', 'Player Elimination': '#AA4488', 'Role Playing': '#CC99BB', 'Movement Points': '#114477', 'Simulation': '#4477AA', 'Variable Phase Order': '#77AADD', 'Area Movement': '#117777', 'Commodity Speculation': '#44AAAA', 'Cooperative Game': '#77CCCC', 'Deduction': '#117744', 'Sudden Death Ending': '#44AA77', 'Connections': '#88CCAA', 'Highest-Lowest Scoring': '#777711', 'Betting and Bluffing': '#AAAA44', 'Memory': '#DDDD77', 'Score-and-Reset Game': '#774411', 'Layering': '#AA7744', 'Map Addition': '#DDAA77', 'Secret Unit Deployment': '#771122', 'Increase Value of Unchosen Resources': '#AA4455', 'Ratio / Combat Results Table': '#DD7788', 'Take That': '#a6cee3', 'Team-Based Game': '#1f78b4', 'Campaign / Battle Card Driven': '#b2df8a', 'Tech Trees / Tech Tracks': '#33a02c', 'Player Judge': '#fb9a99', 'Chit-Pull System': '#e31a1c', 'Three Dimensional Movement': '#fdbf6f', 'Action Drafting': '#ff7f00', 'Minimap Resolution': '#cab2d6', 'Stat Check Resolution': '#6a3d9a', 'Action Timer': '#ffff99', 'Pick-up and Deliver': '#b15928', 'Map Deformation': '#7fc97f', 'Bingo': '#beaed4', 'Crayon Rail System': '#fdc086', 'Multiple Maps': '#ffff99', 'Hidden Roles': '#386cb0', 'Line Drawing': '#f0027f', 'Tug of War': '#bf5b17', 'Pattern Movement': '#666666', 'Static Capture': '#771155', 'Different Dice Movement': '#AA4488', 'Chaining': '#CC99BB', 'Ladder Climbing': '#114477', 'Predictive Bid': '#4477AA', 'Solo / Solitaire Game': '#77AADD', 'Line of Sight': '#117777', 'Critical Hits and Failures': '#44AAAA', 'Interrupts': '#77CCCC', 'Zone of Control': '#117744', 'Bribery': '#44AA77', 'End Game Bonuses': '#88CCAA', 'Area-Impulse': '#777711', 'Worker Placement': '#AAAA44', 'Measurement Movement': '#DDDD77', 'Map Reduction': '#774411', 'Real-Time': '#AA7744', 'Resource to Move': '#DDAA77', 'Mancala': '#771122', 'Ownership': '#AA4455', 'Kill Steal': '#DD7788', 'Hidden Movement': '#a6cee3', 'Track Movement': '#1f78b4', 'Deck Construction': '#b2df8a', 'Drafting': '#33a02c', 'TableauBuilding': '#fb9a99', "Prisoner's Dilemma": '#e31a1c', 'Hidden Victory Points': '#fdbf6f', 'Movement Template': '#ff7f00', 'Slide/Push': '#cab2d6', 'Targeted Clues': '#6a3d9a', 'Command Cards': '#ffff99', 'Grid Coverage': '#b15928', 'Relative Movement': '#7fc97f', 'Action/Event': '#beaed4', 'Card Play Conflict Resolution': '#fdc086', 'I Cut, You Choose': '#ffff99', 'Die Icon Resolution': '#386cb0', 'Elapsed Real Time Ending': '#f0027f', 'Advantage Token': '#bf5b17', 'Storytelling': '#666666', 'Catch the Leader': '#771155', 'Roles with Asymmetric Information': '#AA4488', 'Traitor Game': '#CC99BB', 'Moving Multiple Units': '#114477', 'Semi-Cooperative Game': '#4477AA', 'Communication Limits': '#77AADD', 'Time Track': '#117777', 'Speed Matching': '#44AAAA', 'Cube Tower': '#77CCCC', 'Re-rolling and Locking': '#117744', 'Impulse Movement': '#44AA77', 'Loans': '#88CCAA', 'Delayed Purchase': '#777711', 'Deck, Bag, and Pool Building': '#AAAA44', 'Move Through Deck': '#DDDD77', 'Single Loser Game': '#774411', 'Matching': '#AA7744', 'Induction': '#DDAA77', 'Physical Removal': '#771122', 'Narrative Choice / Paragraph': '#AA4455', 'Pieces as Map': '#DD7788', 'Follow': '#a6cee3', 'Finale Ending': '#1f78b4', 'Order Counters': '#b2df8a', 'Contracts': '#33a02c', 'Passed Action Token': '#fb9a99', 'King of the Hill': '#e31a1c', 'Action Retrieval': '#fdbf6f', 'Force Commitment': '#ff7f00', 'Rondel': '#cab2d6', 'Automatic Resource Growth': '#6a3d9a', 'Legacy Game': '#ffff99', 'Dexterity': '#b15928', 'Physical': '#7fc97f'};
export const allMechanics = Object.keys(mechanicColors);
export const mechanicVectors: Record<string, number[]> = allMechanics.reduce((acc, key, i) => {
    const vector = Array(allMechanics.length).fill(0);
    vector[i] = 1;
    return {
        ...acc,
        [key]: vector
    };
}, {})