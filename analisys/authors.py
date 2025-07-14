import pandas as pd
from itertools import combinations
import networkx as nx
from collections import defaultdict
import community as community_louvain

games_df = pd.read_csv("../static/games.csv")
designers_df = pd.read_csv("../static/designers_reduced.csv")

designers = designers_df.columns.tolist()

def extract_designers(row):
    return [name for name, present in zip(designers, row) if present == 1 and name != "Low-Exp Designer"]

games_df["designers"] = designers_df.apply(extract_designers, axis=1)

G = nx.Graph()
collaboration_games = defaultdict(list)

# Aggiungi archi per ogni coppia di designer che ha collaborato
for idx, designers in games_df["designers"].dropna().items():
    if isinstance(designers, str):
        try:
            designers = eval(designers)
        except:
            continue
    game_title = games_df.at[idx, "Name"] if "Name" in games_df.columns else f"Game_{idx}"
    for d1, d2 in combinations(designers, 2):
        if G.has_edge(d1, d2):
            G[d1][d2]['weight'] += 1
        else:
            G.add_edge(d1, d2, weight=1)
        collaboration_games[frozenset([d1, d2])].append(game_title)

degrees = dict(G.degree())
strengths = {
    node: sum(data['weight'] for _, _, data in G.edges(node, data=True))
    for node in G.nodes
}

top_10_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_strength = sorted(strengths.items(), key=lambda x: x[1], reverse=True)[:10]
average_degree = sum(degrees.values()) / len(degrees)
density = nx.density(G)

largest_cc = max(nx.connected_components(G), key=len)
G_largest = G.subgraph(largest_cc)

diameter = nx.diameter(G_largest)
avg_path_length = nx.average_shortest_path_length(G_largest)

degree_centrality = nx.degree_centrality(G)
closeness_centrality = nx.closeness_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G)

top_10_degree_cent = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

bridges = list(nx.bridges(G))
num_bridges = len(bridges)

bridge_counts = defaultdict(int)
for u, v in bridges:
    bridge_counts[u] += 1
    bridge_counts[v] += 1

top_10_bridge_nodes = sorted(bridge_counts.items(), key=lambda x: x[1], reverse=True)[:10]

partition = community_louvain.best_partition(G)
num_communities = len(set(partition.values()))

communities_dict = defaultdict(list)
for node, comm_id in partition.items():
    communities_dict[comm_id].append(node)

communities_list = list(communities_dict.values())

sorted_communities = sorted(communities_list, key=len, reverse=True)

print("\nStatistiche:")
print("---------------------------------------")
print(f"Numero di nodi (designer):         {G.number_of_nodes()}")
print(f"Numero di archi (collaborazioni):  {G.number_of_edges()}")
print(f"Grado medio:                       {average_degree:.2f}")
print(f"Densità:                           {density:.4f}")
print(f"Numero di ponti (bridge edges):    {num_bridges}")

print("\nTop 10 designer per numero di collaboratori:")
print("-----------------------------------------------------")
for rank, (designer, degree) in enumerate(top_10_degree, 1):
    print(f"{rank:2d}. {designer:<30} Collaboratori: {degree}")

print("\nTop 10 designer per intensità di collaborazione (strength):")
print("-----------------------------------------------------------")
for rank, (designer, strength) in enumerate(top_10_strength, 1):
    print(f"{rank:2d}. {designer:<30} Strength: {strength}")

print("\nComponente connessa principale:")
print("---------------------------------------")
print(f"Nodi nella componente più grande:  {len(G_largest)}")
print(f"Lunghezza media del cammino:       {avg_path_length:.2f}")
print(f"Diametro:                          {diameter}")

ecc = nx.eccentricity(G_largest)
u = max(ecc, key=ecc.get)
v = max(nx.single_source_shortest_path_length(G_largest, u).items(), key=lambda x: x[1])[0]

diameter_path = nx.shortest_path(G_largest, source=u, target=v)

print("\nPath del diametro:")
print("--------------------------")
print(f"Da:          {u}")
print(f"A:           {v}")

print("Percorso:")
for i in range(len(diameter_path) - 1):
    d1 = diameter_path[i]
    d2 = diameter_path[i + 1]
    games = collaboration_games.get(frozenset([d1, d2]), ["<gioco sconosciuto>"])
    print(f"\n → {d1} — {d2}")
    for g in games:
        print(f"     • {g}")
print(f" → {diameter_path[-1]}")

print("\nTop 10 designer per centralità di grado:")
print("-----------------------------------------------------------")
for rank, (designer, cent) in enumerate(top_10_degree_cent, 1):
    print(f"{rank:2d}. {designer:<30} Centralità grado: {cent:.4f}")

print("\nTop 10 designer per centralità di prossimità (closeness):")
print("---------------------------------------------------------")
for rank, (designer, cent) in enumerate(top_10_closeness, 1):
    print(f"{rank:2d}. {designer:<30} Closeness: {cent:.4f}")

print("\nTop 10 designer per centralità di intermediazione (betweenness):")
print("----------------------------------------------------------------")
for rank, (designer, cent) in enumerate(top_10_betweenness, 1):
    print(f"{rank:2d}. {designer:<30} Betweenness: {cent:.4f}")

print("\nTop 10 designer per PageRank:")
print("-----------------------------------------------------")
for rank, (designer, pr) in enumerate(top_10_pagerank, 1):
    print(f"{rank:2d}. {designer:<30} PageRank: {pr:.6f}")

print("\nTop 10 designer più coinvolti in ponti (bridge edges):")
print("------------------------------------------------------")
for rank, (designer, count) in enumerate(top_10_bridge_nodes, 1):
    print(f"{rank:2d}. {designer:<30} Numero ponti: {count}")

print(f"\nNumero di comunità rilevate: {num_communities}")

print("\nTop 5 comunità per numero di membri:")
print("------------------------------------")
for i, comm in enumerate(sorted_communities[:5]):
    print(f"Comunità {i+1}: {len(comm)} membri")
    sample_members = ', '.join(comm[:5])
    print(f"  Esempi membri: {sample_members}\n")
