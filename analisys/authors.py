import pandas as pd
from itertools import combinations
import networkx as nx

# Caricamento dati
games_df = pd.read_csv("../static/games.csv")
designers_df = pd.read_csv("../static/designers_reduced.csv")

# Lista dei nomi dei designer dalle colonne
designers = designers_df.columns.tolist()

# Estrai la lista dei designer per ogni gioco
def extract_designers(row):
    return [name for name, present in zip(designers, row) if present == 1]

games_df["designers"] = designers_df.apply(extract_designers, axis=1)

# Crea grafo
G = nx.Graph()

# Aggiungi archi per ogni coppia di designer che ha collaborato
for designers in games_df["designers"].dropna():
    if isinstance(designers, str):  # sicurezza: se la colonna è stata letta come stringa
        try:
            designers = eval(designers)
        except:
            continue
    for d1, d2 in combinations(designers, 2):
        if G.has_edge(d1, d2):
            G[d1][d2]['weight'] += 1
        else:
            G.add_edge(d1, d2, weight=1)

# === Calcoli ===

# Grado semplice (numero di collaboratori distinti)
degrees = dict(G.degree())

# Strength (somma pesi delle collaborazioni)
strengths = {
    node: sum(data['weight'] for _, _, data in G.edges(node, data=True))
    for node in G.nodes
}

# Top 10 designer per grado
top_10_degree = sorted(degrees.items(), key=lambda x: x[1], reverse=True)[:10]

# Top 10 designer per strength
top_10_strength = sorted(strengths.items(), key=lambda x: x[1], reverse=True)[:10]

# Statistiche globali
average_degree = sum(degrees.values()) / len(degrees)
density = nx.density(G)

# Componente connessa principale
largest_cc = max(nx.connected_components(G), key=len)
G_largest = G.subgraph(largest_cc)

diameter = nx.diameter(G_largest)
avg_path_length = nx.average_shortest_path_length(G_largest)

# === Output ordinato ===

print("\nStatistiche:")
print("----------------------------------")
print(f"Numero di nodi (designer):         {G.number_of_nodes()}")
print(f"Numero di archi (collaborazioni):  {G.number_of_edges()}")
print(f"Grado medio:                       {average_degree:.2f}")
print(f"Densità:                           {density:.4f}")

print("\nTop 10 designer per numero di collaboratori:")
print("-----------------------------------------------")
for rank, (designer, degree) in enumerate(top_10_degree, 1):
    print(f"{rank:2d}. {designer:<30} {degree} collaboratori")

print("\nTop 10 designer per intensità di collaborazione (peso totale):")
print("------------------------------------------------------------------")
for rank, (designer, strength) in enumerate(top_10_strength, 1):
    print(f"{rank:2d}. {designer:<30} Peso totale: {strength}")

print("\nComponente connessa principale:")
print("----------------------------------")
print(f"Nodi nella componente più grande:  {len(G_largest)}")
print(f"Lunghezza media del cammino:       {avg_path_length:.2f}")
print(f"Diametro:                          {diameter}\n")

# Trova la coppia di nodi a distanza massima (diametro)
ecc = nx.eccentricity(G_largest)
u = max(ecc, key=ecc.get)  # nodo con eccentricità massima
v = max(nx.single_source_shortest_path_length(G_largest, u).items(), key=lambda x: x[1])[0]

diameter_path = nx.shortest_path(G_largest, source=u, target=v)

print("\n🧭 Path del diametro:")
print("----------------------")
print(f"Da:    {u}")
print(f"A:     {v}")
print(f"Lunghezza: {len(diameter_path) - 1}")
print("Percorso:")
for step in diameter_path:
    print(f" → {step}")
