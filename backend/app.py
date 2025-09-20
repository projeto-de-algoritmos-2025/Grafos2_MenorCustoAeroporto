import dash
from dash import dcc, html
import plotly.graph_objects as go
from graph import G, dijkstra_shortest_path, bfs_shortest_path, kruskal_mst_path, kruskal_full_mst

# plotar grafo geográfico com cores diferentes para diferentes algoritmos
def plot_geo_graph(G, path=[], algorithm="dijkstra", mst_graph=None):
    # arestas do grafo original
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
    
    # Se for Kruskal e tiver MST, desenhar arestas da MST
    if algorithm == "kruskal" and mst_graph:
        mst_traces = []
        for u, v in mst_graph.edges():
            x = [mst_graph.nodes[u]['lon'], mst_graph.nodes[v]['lon']]
            y = [mst_graph.nodes[u]['lat'], mst_graph.nodes[v]['lat']]
            mst_traces.append(go.Scattergeo(
                lon=x,
                lat=y,
                mode='lines',
                line=dict(width=2, color='orange'),
                hoverinfo='none',
                name="MST"
            ))
        edge_traces = mst_traces  # Substitui arestas cinzas pelas da MST
    
    # nós
    node_trace = go.Scattergeo(
        lon=[G.nodes[n]['lon'] for n in G.nodes()],
        lat=[G.nodes[n]['lat'] for n in G.nodes()],
        text=[G.nodes[n]['name'] for n in G.nodes()],
        mode='markers',
        marker=dict(size=6, color='blue'),
        hoverinfo='text'
    )
    
    # Cores diferentes para cada algoritmo
    path_colors = {
        'bfs': 'green',
        'dijkstra': 'red', 
        'kruskal': 'orange'
    }
    
    # caminho encontrado (apenas para BFS e Dijkstra)
    path_trace = None
    if path and algorithm != "kruskal":
        path_trace = go.Scattergeo(
            lon=[G.nodes[n]['lon'] for n in path],
            lat=[G.nodes[n]['lat'] for n in path],
            mode='lines+markers',
            line=dict(width=4, color=path_colors.get(algorithm, 'red')),
            marker=dict(size=10, color=path_colors.get(algorithm, 'red')),
            hoverinfo='none',
            name=f"Caminho {algorithm.upper()}"
        )
    
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
        margin=dict(l=0,r=0,t=0,b=0),
        showlegend=True if (path or mst_graph) else False
    )
    return fig

# cria app Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Grafo de Aeroportos no Mapa Mundial - Algoritmos de Grafos"),
    
    # Seleção de algoritmo
    html.Div([
        html.Label("Algoritmo:"),
        dcc.Dropdown(
            id="algorithm",
            options=[
                {"label": "BFS (Breadth-First Search)", "value": "bfs"},
                {"label": "Dijkstra (Caminho Mínimo)", "value": "dijkstra"},
                {"label": "Kruskal (Árvore Geradora Mínima)", "value": "kruskal"}
            ],
            value="dijkstra",
            placeholder="Selecione um algoritmo",
            searchable=False,
            clearable=False,
            style={"margin-bottom": "20px"}
        ),
    ], style={"width": "100%", "margin-bottom": "20px"}),
    
    # Seleção de aeroportos
    html.Div([
        html.Div([
            html.Label("Origem:"),
            dcc.Dropdown(
                id="source",
                options=[{"label": G.nodes[n]['name'], "value": n} for n in G.nodes],
                placeholder="Selecione aeroporto de origem",
                searchable=True,
                clearable=True
            ),
        ], id="source-div", style={"width": "48%", "display": "inline-block"}),
        html.Div([
            html.Label("Destino:"),
            dcc.Dropdown(
                id="target",
                options=[{"label": G.nodes[n]['name'], "value": n} for n in G.nodes],
                placeholder="Selecione aeroporto de destino",
                searchable=True,
                clearable=True
            ),
        ], id="target-div", style={"width": "48%", "display": "inline-block", "margin-left": "4%"}),
    ]),
    
    dcc.Graph(id="graph"),
    html.Div(id="path_output", style={
        "margin-top": "20px", 
        "font-size": "16px",
        "padding": "15px",
        "background-color": "#f9f9f9",
        "border-radius": "10px",
        "white-space": "pre-line"
    })
])

# callback para controlar visibilidade dos dropdowns de aeroportos
@app.callback(
    [dash.Output("source-div", "style"),
     dash.Output("target-div", "style")],
    [dash.Input("algorithm", "value")]
)
def toggle_airport_dropdowns(algorithm):
    if algorithm == "kruskal":
        # Oculta ambos os dropdowns para Kruskal
        source_style = {"display": "none"}
        target_style = {"display": "none"}
    else:
        # Mostra ambos os dropdowns para BFS e Dijkstra
        source_style = {"width": "48%", "display": "inline-block"}
        target_style = {"width": "48%", "display": "inline-block", "margin-left": "4%"}
    
    return source_style, target_style

# callback principal 
@app.callback(
    [dash.Output("graph", "figure"),
     dash.Output("path_output", "children")],
    [dash.Input("source", "value"),
     dash.Input("target", "value"),
     dash.Input("algorithm", "value")]
)
def update_graph(source, target, algorithm):
    mst_graph = None
    
    if algorithm == "kruskal":
        # Para Kruskal, mostra toda a MST automaticamente
        mst_graph, mst_weight = kruskal_full_mst(G)
        path_text = (
            f"Algoritmo: Kruskal (Árvore Geradora Mínima)\n"
            f"Peso total da MST: {mst_weight:.2f} km\n"
            f"Número total de arestas na MST: {len(mst_graph.edges())}\n"
            f"A MST conecta todos os aeroportos com o menor custo total possível.\n"
            f"Esta árvore é única e independe da escolha de origem."
        )
        path = []
        fig = plot_geo_graph(G, path, algorithm, mst_graph)
        
    elif source and target:
        # Para BFS e Dijkstra, executa algoritmos normais
        if algorithm == "bfs":
            path = bfs_shortest_path(G, source, target)
            if path:
                # BFS não calcula distância, vamos calcular manualmente
                total_distance = 0
                for i in range(len(path) - 1):
                    u, v = path[i], path[i+1]
                    total_distance += G[u][v].get('weight', 1)
                path_text = (
                    f"Algoritmo: BFS (Breadth-First Search)\n"
                    f"Caminho: {' → '.join(G.nodes[n]['name'] for n in path)}\n"
                    f"Número de conexões: {len(path) - 1}\n"
                    f"Distância total: {total_distance:.2f} km"
                )
            else:
                path_text = "BFS: Não há caminho entre os aeroportos selecionados."
                
        elif algorithm == "dijkstra":
            path, distance = dijkstra_shortest_path(G, source, target)
            if path:
                path_text = (
                    f"Algoritmo: Dijkstra (Caminho Mínimo)\n"
                    f"Caminho: {' → '.join(G.nodes[n]['name'] for n in path)}\n"
                    f"Custo mínimo: {distance:.2f} km"
                )
            else:
                path_text = "Dijkstra: Não há caminho entre os aeroportos selecionados."
        else:
            path = []
            path_text = "Algoritmo não reconhecido."
            
        fig = plot_geo_graph(G, path, algorithm)
    else:
        path = []
        if algorithm == "kruskal":
            # Nunca chega aqui, mas mantém por consistência
            path_text = "Kruskal - MST será mostrada automaticamente."
        else:
            path_text = "Selecione dois aeroportos para encontrar o caminho."
        fig = plot_geo_graph(G, path, algorithm)
    
    return fig, path_text

# roda app
if __name__ == "__main__":
    app.run(debug=True)
