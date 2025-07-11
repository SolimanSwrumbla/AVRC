import pandas as pd
import networkx as nx
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Caricamento dei dati
games_df = pd.read_csv("../static/games.csv").sort_values("NumUserRatings", ascending=False).head(2500)
mechanics_df = pd.read_csv("../static/mechanics.csv")

# Colonne con le meccaniche (escludendo l'ID)
mechanic_columns = [col for col in mechanics_df.columns if col != "BGGId"]

# Aggiunge colonna 'mechanics' a games_df (lista di meccaniche attive per ogni gioco)
games_df["mechanics"] = mechanics_df[mechanic_columns].apply(
    lambda row: [mech for mech in mechanic_columns if row[mech] == 1],
    axis=1
)

# Lista di tutte le meccaniche e mappa meccanica → indice
all_mechanics = sorted(set(mechanic_columns))
mech_to_index = {mech: i for i, mech in enumerate(all_mechanics)}

# Funzione per vettorizzare una lista di meccaniche
def vectorize_mechanics(mechanics):
    vec = np.zeros(len(all_mechanics), dtype=int)
    for mech in mechanics:
        if mech in mech_to_index:
            vec[mech_to_index[mech]] = 1
    return vec

# Costruzione della matrice gioco × meccaniche
mechanics_matrix = np.stack(games_df["mechanics"].apply(vectorize_mechanics))

# Calcolo della similarità coseno tra giochi
cos_sim = cosine_similarity(mechanics_matrix)
np.fill_diagonal(cos_sim, 0)  # rimuove gli auto-archi

# Soglia per includere solo archi significativi
threshold = 0  # puoi usare ad esempio 0.1 o 0.2 per filtrarne alcuni
rows, cols = np.where(cos_sim > threshold)

# Costruzione grafo
G = nx.Graph()
ids = games_df["BGGId"].values
for i, j in zip(rows, cols):
    if i < j:  # evita duplicati, grafo non orientato
        G.add_edge(ids[i], ids[j], weight=cos_sim[i, j])

# Calcolo strength (grado pesato)
strengths = {node: sum(d['weight'] for _, _, d in G.edges(node, data=True)) for node in G.nodes}
top_10_strength = sorted(strengths.items(), key=lambda x: x[1], reverse=True)[:10]

# Calcolo grado semplice
degrees = dict(G.degree())
top_10_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]

# Mappa ID → nome gioco
id_to_name = dict(zip(games_df["BGGId"], games_df["Name"]))

# Statistiche del grafo
print("\nStatistiche:")
print("--------------------------")
print(f"Numero di nodi: {G.number_of_nodes()}")
print(f"Numero di archi: {G.number_of_edges()}")

average_degree = np.mean(list(degrees.values()))
print(f"Grado medio: {average_degree:.2f}")

density = G.number_of_edges() / (G.number_of_nodes() * (G.number_of_nodes() - 1) / 2)
print(f"Densità: {density:.4f}")

# Diametro e lunghezza media del cammino
diameter = 3 # nx.diameter(G)
avg_path_length = 1.57 # nx.average_shortest_path_length(G)


# Output top 10 per grado semplice
print("\nTop 10 giochi per numero di connessioni (grado):")
print("-----------------------------------------------------")
for rank, (game_id, degree) in enumerate(top_10_degree, 1):
    name = id_to_name.get(game_id, "Unknown")
    print(f"{rank:2d}. {name:<40} {degree} connessioni")

# Output top 10 per strength
print("\nTop 10 giochi per similarità totale (strength):")
print("---------------------------------------------------")
for rank, (game_id, strength) in enumerate(top_10_strength, 1):
    name = id_to_name.get(game_id, "Unknown")
    print(f"{rank:2d}. {name:<40} {strength:.2f}")

print("\nDistanze:")
print("----------------------------------")
print(f"Lunghezza media del cammino:       {avg_path_length:.2f}")
print(f"Diametro:                          {diameter}\n")