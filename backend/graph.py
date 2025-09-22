import os
import pandas as pd
import networkx as nx
from collections import deque
import heapq

# BFS - algoritmo original (encontra caminho com menor número de arestas)
def bfs_shortest_path(graph, source, target):
    """
    Breadth-First Search: encontra o caminho com menor número de arestas,
    não necessariamente o de menor custo.
    """
    if source not in graph or target not in graph:
        return []
    
    queue = deque([source])
    parents = {source: None}
    
    while queue:
        current = queue.popleft()
        if current == target:
            path = []
            while current is not None:
                path.append(current)
                current = parents[current]
            
            # ---- Impressão das arestas percorridas e seus custos ----
            path.reverse()
            if len(path) > 1:
                print("\n=== Caminho BFS ===")
                total = 0
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    w = graph[u][v].get('weight', 1)
                    total += w
                    print(f"Aresta: {graph.nodes[u]['name']} -> {graph.nodes[v]['name']} | Custo: {w} km")
                print(f"Número de conexões: {len(path) - 1}")
                print(f"Custo total: {total:.2f} km\n")
            
            return path
            
        for neighbor in graph[current]:
            if neighbor not in parents:
                parents[neighbor] = current
                queue.append(neighbor)
    return []

# Algoritmo de Dijkstra com heapq 
def dijkstra_shortest_path(graph, source, target):
    """
    Retorna o caminho mais curto e a distância mínima entre source e target
    em um grafo ponderado (usando weight das arestas).
    Também imprime as arestas percorridas e o custo de cada uma.
    """

    # Verifica se os nós de origem e destino existem no grafo
    if source not in graph or target not in graph:
        return [], float('inf')

    # Inicializa todas as distâncias com infinito
    dist = {node: float('inf') for node in graph}
    dist[source] = 0  # A distância até o nó de origem é 0

    # Dicionário para reconstruir o caminho
    parent = {source: None}

    # Fila de prioridade (heap) inicializada com o nó de origem e distância 0
    heap = [(0, source)]

    # Loop principal do Dijkstra
    while heap:
        current_dist, u = heapq.heappop(heap)  # Remove o nó com menor distância

        # Se já encontramos uma distância menor para u, ignoramos
        if current_dist > dist[u]:
            continue

        # Se chegamos ao destino, podemos parar (otimização)
        if u == target:
            break

        # Itera sobre todos os vizinhos do nó atual
        for v in graph[u]:
            weight = graph[u][v].get('weight', 1)  # Pega o peso da aresta (ou 1 se não existir)
            new_dist = current_dist + weight       # Calcula distância acumulada até v

            # Se encontramos um caminho mais curto para v, atualizamos
            if new_dist < dist[v]:
                dist[v] = new_dist
                parent[v] = u                  # Armazena o pai para reconstruir o caminho
                heapq.heappush(heap, (new_dist, v))  # Adiciona na fila de prioridade

    # Se não existe caminho até o destino, retorna vazio
    if dist[target] == float('inf'):
        print("Nenhum caminho encontrado.")
        return [], float('inf')

    # Reconstrução do caminho a partir do destino
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent[node]
    path.reverse()  # Reverte a lista para ir da origem ao destino

    # ---- Impressão das arestas percorridas e seus custos ----
    print("\n=== Caminho Dijkstra ===")
    total = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        w = graph[u][v].get('weight', 1)
        total += w
        print(f"Aresta: {graph.nodes[u]['name']} -> {graph.nodes[v]['name']} | Custo: {w} km")
    print(f"Custo total: {total:.2f} km\n")
    
    return path, total

# Algoritmo de Kruskal - Árvore Geradora Mínima
def kruskal_mst_path(graph, source, target):
    """
    Implementa o algoritmo de Kruskal para encontrar a Árvore Geradora Mínima (MST)
    e depois encontra um caminho entre source e target na MST.
    Retorna o caminho e o custo total.
    """
    
    # Verifica se os nós existem
    if source not in graph or target not in graph:
        return [], float('inf')
    
    # Se source == target, retorna caminho trivial
    if source == target:
        return [source], 0
    
    # Classe para Union-Find (Disjoint Set Union)
    class UnionFind:
        def __init__(self, nodes):
            self.parent = {node: node for node in nodes}
            self.rank = {node: 0 for node in nodes}
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return False
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
            return True
    
    # Cria lista de todas as arestas com pesos
    edges = []
    for u, v, data in graph.edges(data=True):
        weight = data.get('weight', 1)
        edges.append((weight, u, v))
    
    # Ordena arestas por peso (menor para maior)
    edges.sort()
    
    # Aplica Kruskal para construir MST
    uf = UnionFind(graph.nodes())
    mst_edges = []
    mst_weight = 0
    
    for weight, u, v in edges:
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            mst_weight += weight
            if len(mst_edges) == len(graph.nodes()) - 1:
                break
    
    # Constrói grafo da MST
    mst_graph = nx.Graph()
    mst_graph.add_nodes_from(graph.nodes(data=True))
    for u, v, weight in mst_edges:
        mst_graph.add_edge(u, v, weight=weight)
    
    # Encontra caminho na MST usando BFS
    try:
        path = nx.shortest_path(mst_graph, source, target)
        
        # Calcula custo total do caminho
        total_cost = 0
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            total_cost += mst_graph[u][v].get('weight', 1)
        
        # ---- Impressão das arestas percorridas e seus custos ----
        print("\n=== Caminho Kruskal (MST) ===")
        print(f"Peso total da MST: {mst_weight:.2f} km")
        for i in range(len(path) - 1):
            u, v = path[i], path[i+1]
            w = mst_graph[u][v].get('weight', 1)
            print(f"Aresta: {graph.nodes[u]['name']} -> {graph.nodes[v]['name']} | Custo: {w} km")
        print(f"Custo total do caminho: {total_cost:.2f} km\n")
        
        return path, total_cost
        
    except nx.NetworkXNoPath:
        print("Nenhum caminho encontrado na MST.")
        return [], float('inf')

# Algoritmo de Kruskal - Árvore Geradora Mínima completa
def kruskal_full_mst(graph):
    """
    Implementa o algoritmo de Kruskal para construir toda a Árvore Geradora Mínima (MST).
    Retorna a MST como um grafo NetworkX e o peso total.
    """
    
    # Classe para Union-Find (Disjoint Set Union)
    class UnionFind:
        def __init__(self, nodes):
            self.parent = {node: node for node in nodes}
            self.rank = {node: 0 for node in nodes}
        
        def find(self, x):
            if self.parent[x] != x:
                self.parent[x] = self.find(self.parent[x])
            return self.parent[x]
        
        def union(self, x, y):
            px, py = self.find(x), self.find(y)
            if px == py:
                return False
            if self.rank[px] < self.rank[py]:
                px, py = py, px
            self.parent[py] = px
            if self.rank[px] == self.rank[py]:
                self.rank[px] += 1
            return True
    
    # Cria lista de todas as arestas com pesos
    edges = []
    for u, v, data in graph.edges(data=True):
        weight = data.get('weight', 1)
        edges.append((weight, u, v))
    
    # Ordena arestas por peso (menor para maior)
    edges.sort()
    
    # Aplica Kruskal para construir MST
    uf = UnionFind(graph.nodes())
    mst_edges = []
    mst_weight = 0
    
    for weight, u, v in edges:
        if uf.union(u, v):
            mst_edges.append((u, v, weight))
            mst_weight += weight
            if len(mst_edges) == len(graph.nodes()) - 1:
                break
    
    # Constrói grafo da MST
    mst_graph = nx.Graph()
    mst_graph.add_nodes_from(graph.nodes(data=True))
    for u, v, weight in mst_edges:
        mst_graph.add_edge(u, v, weight=weight)
    
    print(f"\n=== MST Completa (Kruskal) ===")
    print(f"Número de arestas na MST: {len(mst_edges)}")
    print(f"Peso total da MST: {mst_weight:.2f} km")
    print(f"Número de nós conectados: {len(mst_graph.nodes())}\n")
    
    return mst_graph, mst_weight

# carregar dados e criar grafo
# Determina o diretório do script atual e constrói o caminho correto
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(os.path.dirname(script_dir), "data")
airports_file = os.path.join(data_dir, "airports_min.csv")
routes_file = os.path.join(data_dir, "routes_min.csv")

if not os.path.exists(airports_file) or not os.path.exists(routes_file):
    raise FileNotFoundError("Certifique-se de que os arquivos CSV estão em ../data/")

airports_df = pd.read_csv(airports_file)
routes_df = pd.read_csv(routes_file)

# cria grafo com pesos reais (distance_km)
G = nx.Graph()
for _, row in airports_df.iterrows():
    G.add_node(row['id'], name=row['name'], lat=row['lat'], lon=row['lon'])

for _, row in routes_df.iterrows():
    if row['src_id'] in G.nodes and row['dst_id'] in G.nodes:
        # Usar distance_km como peso das arestas
        weight = row.get('distance_km', 1)  # Usa 1 como fallback se não houver distance_km
        G.add_edge(row['src_id'], row['dst_id'], weight=weight)