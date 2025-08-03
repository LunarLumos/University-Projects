import json
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
import base64
import heapq

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

def dijkstra_shortest_path(graph, start, end):
    # Priority queue: (distance, node, path)
    queue = [(0, start, [start])]
    visited = set()
    
    while queue:
        distance, node, path = heapq.heappop(queue)
        
        if node == end:
            return path, distance
        
        if node not in visited:
            visited.add(node)
            
            for neighbor in graph.neighbors(node):
                edge_weight = graph.get_edge_data(node, neighbor)['weight']
                new_distance = distance + edge_weight
                new_path = path + [neighbor]
                heapq.heappush(queue, (new_distance, neighbor, new_path))
    
    return None, float('inf')

def find_secure_paths(graph_data, start_node, end_node):
    G = build_graph(graph_data)
    
    # Find shortest path based on weights (latency)
    shortest_path, shortest_distance = dijkstra_shortest_path(G, start_node, end_node)
    
    # Find safest path (least hops)
    # To do this, we set all weights to 1 and run Dijkstra's
    H = G.copy()
    for u, v in H.edges():
        H.edges[u, v]['weight'] = 1
    
    safest_path, safest_hops = dijkstra_shortest_path(H, start_node, end_node)
    
    return {
        'shortest_path': {
            'path': shortest_path,
            'total_latency': shortest_distance
        },
        'safest_path': {
            'path': safest_path,
            'total_hops': safest_hops
        }
    }

def visualize_secure_paths(graph_data, paths):
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
    
    # Draw edges with weights
    nx.draw_networkx_edges(G, pos, width=1.5, edge_color='gray', arrows=True)
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    
    # Draw node labels
    labels = {node: attrs['label'] for node, attrs in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    # Highlight paths
    if paths['shortest_path']['path']:
        edges = list(zip(paths['shortest_path']['path'][:-1], paths['shortest_path']['path'][1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges, 
                             width=3, edge_color='red', 
                             alpha=0.7, label=f"Shortest (Latency: {paths['shortest_path']['total_latency']}ms)")
    
    if paths['safest_path']['path']:
        edges = list(zip(paths['safest_path']['path'][:-1], paths['safest_path']['path'][1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges, 
                             width=3, edge_color='blue', 
                             alpha=0.7, label=f"Safest (Hops: {paths['safest_path']['total_hops']})")
    
    plt.title('Secure Network Paths')
    plt.legend()
    plt.axis('off')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')