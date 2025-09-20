import os
import pandas as pd
import networkx as nx
import heapq
import dash
from dash import dcc, html
import plotly.graph_objects as go

# ------------------------------------------------------------
# Algoritmo de Dijkstra com heapq 
# ------------------------------------------------------------
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

    # Retorna o caminho (lista de nós) e a distância total
    return path, dist[target]



# ------------------------------------------------------------
# Função para plotar o grafo geográfico
# ------------------------------------------------------------
def plot_geo_graph(G, path=[]):
    edge_traces = []
    for u, v in G.edges():
        x = [G.nodes[u]['lon'], G.nodes[v]['lon']]
        y = [G.nodes[u]['lat'], G.nodes[v]['lat']]
        edge_traces.append(go.Scattergeo(
            lon=x,
            lat=y,
            mode='lines',
            line=dict(width=0.5, color='grey'),
            hoverinfo='none'
        ))

    node_trace = go.Scattergeo(
        lon=[G.nodes[n]['lon'] for n in G.nodes()],
        lat=[G.nodes[n]['lat'] for n in G.nodes()],
        text=[G.nodes[n]['name'] for n in G.nodes()],
        mode='markers',
        marker=dict(size=6, color='blue'),
        hoverinfo='text'
    )

    path_trace = go.Scattergeo(
        lon=[G.nodes[n]['lon'] for n in path],
        lat=[G.nodes[n]['lat'] for n in path],
        mode='lines+markers',
        line=dict(width=3, color='red'),
        marker=dict(size=8, color='red'),
        hoverinfo='none'
    ) if path else None

    data = edge_traces + [node_trace]
    if path_trace:
        data.append(path_trace)

    fig = go.Figure(data=data)
    fig.update_layout(
        geo=dict(
            projection_type='natural earth',
            showland=True, landcolor='rgb(243,243,243)',
            showocean=True, oceancolor='rgb(230,245,255)',
            showcountries=True, countrycolor='rgb(204,204,204)'
        ),
        margin=dict(l=0, r=0, t=0, b=0)
    )
    return fig

# ------------------------------------------------------------
# Carregar dados
# ------------------------------------------------------------
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")
airports_file = os.path.join(data_dir, "airports_min.csv")
routes_file = os.path.join(data_dir, "routes_min.csv")

if not os.path.exists(airports_file) or not os.path.exists(routes_file):
    raise FileNotFoundError("Certifique-se de que os arquivos CSV estão em ./data/")

airports_df = pd.read_csv(airports_file)
routes_df = pd.read_csv(routes_file)

# ------------------------------------------------------------
# Criar grafo com pesos reais (distance_km)
# ------------------------------------------------------------
G = nx.Graph()
for _, row in airports_df.iterrows():
    G.add_node(row['id'], name=row['name'], lat=row['lat'], lon=row['lon'])

for _, row in routes_df.iterrows():
    if row['src_id'] in G.nodes and row['dst_id'] in G.nodes:
        # Usar distance_km como peso
        G.add_edge(row['src_id'], row['dst_id'], weight=row['distance_km'])

# ------------------------------------------------------------
# Criar app Dash
# ------------------------------------------------------------
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Grafo de Aeroportos no Mapa Mundial - Dijkstra"),
    html.Div([
        html.Label("Origem:"),
        dcc.Dropdown(
            id="source",
            options=[{"label": G.nodes[n]['name'], "value": n} for n in G.nodes],
            placeholder="Selecione aeroporto de origem",
            searchable=True,
            clearable=True
        ),
    ], style={"width": "48%", "display": "inline-block"}),
    html.Div([
        html.Label("Destino:"),
        dcc.Dropdown(
            id="target",
            options=[{"label": G.nodes[n]['name'], "value": n} for n in G.nodes],
            placeholder="Selecione aeroporto de destino",
            searchable=True,
            clearable=True
        ),
    ], style={"width": "48%", "display": "inline-block"}),
    dcc.Graph(id="graph"),
    html.Div(id="path_output", style={"margin-top": "20px", "font-size": "18px"})
])

# ------------------------------------------------------------
# Callback do Dash
# ------------------------------------------------------------
@app.callback(
    [dash.Output("graph", "figure"),
     dash.Output("path_output", "children")],
    [dash.Input("source", "value"),
     dash.Input("target", "value")]
)
def update_graph(source, target):
    if source and target:
        path, distance = dijkstra_shortest_path(G, source, target)
        if path:
            path_text = (
                f"Caminho: {' → '.join(G.nodes[n]['name'] for n in path)}\n"
                f"Custo total: {distance:.2f} km"
            )
        else:
            path_text = "Não há caminho entre os aeroportos selecionados."
    else:
        path = []
        path_text = "Selecione dois aeroportos."
    fig = plot_geo_graph(G, path)
    return fig, path_text

# ------------------------------------------------------------
# Executar app
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
