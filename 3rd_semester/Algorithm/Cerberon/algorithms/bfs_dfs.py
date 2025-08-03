import json
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
import base64

def load_network_graph(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def build_graph(data):
    G = nx.DiGraph()
    
    for node in data['nodes']:
        G.add_node(node['id'], label=node['label'], group=node['group'])
    
    for edge in data['edges']:
        G.add_edge(edge['from'], edge['to'], weight=edge['weight'], label=edge['label'])
    
    return G

def bfs_path(graph, start, end):
    visited = set()
    queue = [(start, [start])]
    
    while queue:
        node, path = queue.pop(0)
        if node == end:
            return path
        
        if node not in visited:
            visited.add(node)
            for neighbor in graph.neighbors(node):
                queue.append((neighbor, path + [neighbor]))
    
    return None

def dfs_path(graph, start, end, path=None, visited=None):
    if path is None:
        path = []
    if visited is None:
        visited = set()
    
    path = path + [start]
    visited.add(start)
    
    if start == end:
        return path
    
    for neighbor in graph.neighbors(start):
        if neighbor not in visited:
            new_path = dfs_path(graph, neighbor, end, path, visited)
            if new_path:
                return new_path
    
    return None

def detect_phishing_route(graph, start_node, end_node):
    G = build_graph(graph)
    
    bfs_result = bfs_path(G, start_node, end_node)
    dfs_result = dfs_path(G, start_node, end_node)
    
    return {
        'bfs_path': bfs_result,
        'dfs_path': dfs_result
    }

def visualize_graph_paths(graph_data, paths):
    G = build_graph(graph_data)
    pos = nx.spring_layout(G, seed=42)
    
    plt.figure(figsize=(12, 8))
    
    # Draw nodes with different colors for groups
    groups = set(nx.get_node_attributes(G, 'group').values())
    colors = ['skyblue', 'lightgreen', 'salmon', 'gold', 'violet', 'orange']
    group_colors = {group: colors[i] for i, group in enumerate(groups)}
    
    for group in groups:
        nodes = [node for node, attrs in G.nodes(data=True) if attrs['group'] == group]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                             node_color=group_colors[group], 
                             node_size=2000,
                             label=group)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.5, edge_color='gray', arrows=True)
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Draw node labels
    labels = {node: attrs['label'] for node, attrs in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    # Highlight paths
    colors = ['red', 'blue', 'green', 'purple']
    for i, (name, path) in enumerate(paths.items()):
        if path:
            edges = list(zip(path[:-1], path[1:]))
            nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                 width=3, edge_color=colors[i], 
                                 alpha=0.7, label=name)
    
    plt.title('Network Graph with Phishing Routes')
    plt.legend()
    plt.axis('off')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')