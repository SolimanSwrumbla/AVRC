import pandas as pd
import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from collections import defaultdict
import community as community_louvain

games_df = pd.read_csv("../static/games.csv").sort_values("NumUserRatings", ascending=False).head(500)
mechanics_df = pd.read_csv("../static/mechanics.csv")

mechanic_columns = [col for col in mechanics_df.columns if col != "BGGId"]

games_df["mechanics"] = mechanics_df[mechanic_columns].apply(
    lambda row: [mech for mech in mechanic_columns if row[mech] == 1], axis=1)

all_mechanics = sorted(set(mechanic_columns))
mech_to_index = {mech: i for i, mech in enumerate(all_mechanics)}

def vectorize_mechanics(mechanics):
    vec = np.zeros(len(all_mechanics), dtype=int)
    for mech in mechanics:
        if mech in mech_to_index:
            vec[mech_to_index[mech]] = 1
    return vec

mechanics_matrix = np.stack(games_df["mechanics"].apply(vectorize_mechanics))

cos_sim = cosine_similarity(mechanics_matrix)
np.fill_diagonal(cos_sim, 0)

threshold = 0
rows, cols = np.where(cos_sim > threshold)

G = nx.Graph()
ids = games_df["BGGId"].values
for i, j in zip(rows, cols):
    if i < j:
        G.add_edge(ids[i], ids[j], weight=cos_sim[i, j])

id_to_name = dict(zip(games_df["BGGId"], games_df["Name"]))

strengths = {node: sum(d['weight'] for _, _, d in G.edges(node, data=True)) for node in G.nodes}
top_10_strength = sorted(strengths.items(), key=lambda x: x[1], reverse=True)[:10]

degrees = dict(G.degree())
top_10_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]

average_degree = np.mean(list(degrees.values()))
density = nx.density(G)

print("\nStatistiche:")
print("---------------------------------------")
print(f"Numero di nodi (giochi):          {G.number_of_nodes()}")
print(f"Numero di archi (similarità):     {G.number_of_edges()}")
print(f"Grado medio:                      {average_degree:.2f}")
print(f"Densità:                          {density:.4f}")

print("\nTop 10 giochi per numero di connessioni (grado):")
print("-------------------------------------------------------------")
for rank, (game_id, degree) in enumerate(top_10_degree, 1):
    name = id_to_name.get(game_id, "Unknown")
    print(f"{rank:2d}. {name:<40} Connessioni: {degree}")

print("\nTop 10 giochi per similarità totale (strength):")
print("---------------------------------------------------------------")
for rank, (game_id, strength) in enumerate(top_10_strength, 1):
    name = id_to_name.get(game_id, "Unknown")
    print(f"{rank:2d}. {name:<40} Strength: {strength:.4f}")

largest_cc = max(nx.connected_components(G), key=len)
G_largest = G.subgraph(largest_cc)

try:
    diameter = nx.diameter(G_largest)
    avg_path_length = nx.average_shortest_path_length(G_largest)
    ecc = nx.eccentricity(G_largest)
    u = max(ecc, key=ecc.get)
    v = max(nx.single_source_shortest_path_length(G_largest, u).items(), key=lambda x: x[1])[0]
    diameter_path = nx.shortest_path(G_largest, source=u, target=v)

    print("\nComponente connessa principale:")
    print("---------------------------------------")
    print(f"Nodi nella componente più grande: {len(G_largest)}")
    print(f"Lunghezza media del cammino:      {avg_path_length:.4f}")
    print(f"Diametro:                         {diameter}")

    print("\nPath del diametro:")
    print("------------------------")
    for node in diameter_path:
        print(f" → {id_to_name.get(node, 'Unknown')}")

except nx.NetworkXError as e:
    print("\nErrore nel calcolo del diametro:", e)

degree_centrality = nx.degree_centrality(G)
closeness_centrality = nx.closeness_centrality(G)
betweenness_centrality = nx.betweenness_centrality(G)
pagerank = nx.pagerank(G)

top_10_degree_cent = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_closeness = sorted(closeness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_betweenness = sorted(betweenness_centrality.items(), key=lambda x: x[1], reverse=True)[:10]
top_10_pagerank = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)[:10]

print("\nTop 10 giochi per centralità di grado:")
print("-----------------------------------------------------------------------")
for rank, (game_id, cent) in enumerate(top_10_degree_cent, 1):
    print(f"{rank:2d}. {id_to_name.get(game_id, 'Unknown'):<40} Centralità grado: {cent:.6f}")

print("\nTop 10 giochi per centralità di prossimità (closeness):")
print("----------------------------------------------------------------")
for rank, (game_id, cent) in enumerate(top_10_closeness, 1):
    print(f"{rank:2d}. {id_to_name.get(game_id, 'Unknown'):<40} Closeness: {cent:.6f}")

print("\nTop 10 giochi per centralità di intermediazione (betweenness):")
print("------------------------------------------------------------------")
for rank, (game_id, cent) in enumerate(top_10_betweenness, 1):
    print(f"{rank:2d}. {id_to_name.get(game_id, 'Unknown'):<40} Betweenness: {cent:.6f}")

print("\nTop 10 giochi per PageRank:")
print("-----------------------------------------------------------------")
for rank, (game_id, pr) in enumerate(top_10_pagerank, 1):
    print(f"{rank:2d}. {id_to_name.get(game_id, 'Unknown'):<40} PageRank: {pr:.8f}")

partition = community_louvain.best_partition(G)
num_communities = len(set(partition.values()))

communities_dict = defaultdict(list)
for node, comm_id in partition.items():
    communities_dict[comm_id].append(node)

communities_list = list(communities_dict.values())
sorted_communities = sorted(communities_list, key=len, reverse=True)

print(f"\nNumero di comunità rilevate: {num_communities}")

print("\nTop 5 comunità per numero di membri:")
print("------------------------------------")
for i, comm in enumerate(sorted_communities[:5]):
    print(f"Comunità {i+1}: {len(comm)} membri")
    sample_members = ', '.join(id_to_name.get(node, "Unknown") for node in comm[:5])
    print(f"  Esempi membri: {sample_members}\n")
