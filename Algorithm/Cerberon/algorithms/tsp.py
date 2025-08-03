import json
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
import base64
import itertools

def load_network_graph(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def build_graph(data):
    G = nx.Graph()
    
    for node in data['nodes']:
        G.add_node(node['id'], label=node['label'], group=node['group'])
    
    for edge in data['edges']:
        G.add_edge(edge['from'], edge['to'], weight=edge['weight'], label=edge['label'])
    
    return G

def brute_force_tsp(graph, nodes_to_visit):
    if not nodes_to_visit:
        return [], 0
    
    start_node = nodes_to_visit[0]
    other_nodes = nodes_to_visit[1:]
    
    if not other_nodes:
        return [start_node], 0
    
    min_path = None
    min_distance = float('inf')
    
    for permutation in itertools.permutations(other_nodes):
        current_path = [start_node] + list(permutation) + [start_node]
        current_distance = 0
        
        for i in range(len(current_path) - 1):
            if graph.has_edge(current_path[i], current_path[i+1]):
                current_distance += graph.get_edge_data(current_path[i], current_path[i+1])['weight']
            else:
                try:
                    path = nx.shortest_path(graph, current_path[i], current_path[i+1], weight='weight')
                    current_distance += nx.shortest_path_length(graph, current_path[i], current_path[i+1], weight='weight')
                except:
                    current_distance = float('inf')
                    break
        
        if current_distance < min_distance:
            min_distance = current_distance
            min_path = current_path
    
    return min_path, min_distance

def optimize_hacker_route(graph_data, nodes_to_visit):
    if not nodes_to_visit:
        return {
            'optimal_path': {'path': [], 'total_distance': 0},
            'heuristic_path': {'path': [], 'total_distance': 0}
        }

    G = build_graph(graph_data)
    
    # Convert node IDs to integers if they're strings
    try:
        nodes_to_visit = [int(node) if isinstance(node, str) else node for node in nodes_to_visit]
    except:
        return {
            'optimal_path': {'path': None, 'total_distance': float('inf')},
            'heuristic_path': {'path': None, 'total_distance': float('inf')}
        }
    
    # Verify all nodes exist in the graph
    valid_nodes = [node for node in nodes_to_visit if node in G]
    if not valid_nodes:
        return {
            'optimal_path': {'path': None, 'total_distance': float('inf')},
            'heuristic_path': {'path': None, 'total_distance': float('inf')}
        }
    
    # Limit brute-force to small graphs (n <= 8 for performance)
    if len(valid_nodes) <= 8:
        optimal_path, optimal_distance = brute_force_tsp(G, valid_nodes)
    else:
        optimal_path, optimal_distance = None, float('inf')
    
    # Nearest neighbor heuristic with fallback to shortest path
    def nearest_neighbor(start, nodes):
        unvisited = set(nodes)
        unvisited.remove(start)
        path = [start]
        current = start
        total_distance = 0
        
        while unvisited:
            nearest = None
            min_dist = float('inf')
            
            for node in unvisited:
                if G.has_edge(current, node):
                    dist = G.get_edge_data(current, node)['weight']
                    if dist < min_dist:
                        min_dist = dist
                        nearest = node
            
            if nearest is None:
                # No direct path, find shortest path to any unvisited node
                try:
                    paths = nx.shortest_path(G, current, weight='weight')
                    for node in unvisited:
                        if node in paths:
                            dist = nx.shortest_path_length(G, current, node, weight='weight')
                            if dist < min_dist:
                                min_dist = dist
                                nearest = node
                except:
                    break
            
            if nearest is None:
                break  # Can't reach any unvisited nodes
            
            path.append(nearest)
            total_distance += min_dist
            current = nearest
            unvisited.remove(nearest)
        
        # Return to start if possible
        if G.has_edge(current, start):
            path.append(start)
            total_distance += G.get_edge_data(current, start)['weight']
        elif len(path) > 1:
            try:
                return_path = nx.shortest_path(G, current, start, weight='weight')
                path.extend(return_path[1:])
                total_distance += nx.shortest_path_length(G, current, start, weight='weight')
            except:
                pass
        
        return path, total_distance
    
    # Try nearest neighbor from each starting point
    nn_path = None
    nn_distance = float('inf')
    
    for start in valid_nodes:
        path, dist = nearest_neighbor(start, valid_nodes.copy())
        if dist < nn_distance:
            nn_path = path
            nn_distance = dist
    
    return {
        'optimal_path': {
            'path': optimal_path if optimal_path else [],
            'total_distance': optimal_distance
        },
        'heuristic_path': {
            'path': nn_path if nn_path else [],
            'total_distance': nn_distance
        }
    }

def visualize_tsp_solution(graph_data, solution):
    G = build_graph(graph_data)
    pos = nx.spring_layout(G, seed=42)
    
    plt.figure(figsize=(14, 10))
    
    # Draw nodes with different colors for groups
    groups = set(nx.get_node_attributes(G, 'group').values())
    colors = ['skyblue', 'lightgreen', 'salmon', 'gold', 'violet', 'orange']
    group_colors = {group: colors[i] for i, group in enumerate(groups)}
    
    for group in groups:
        nodes = [node for node, attrs in G.nodes(data=True) if attrs['group'] == group]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, 
                             node_color=group_colors[group], 
                             node_size=2500,
                             label=group)
    
    # Draw all edges lightly
    nx.draw_networkx_edges(G, pos, width=1, edge_color='gray', alpha=0.2)
    
    # Highlight optimal path if it exists and is valid
    if solution['optimal_path']['path'] and len(solution['optimal_path']['path']) > 1:
        try:
            edges = []
            for i in range(len(solution['optimal_path']['path']) - 1):
                u = solution['optimal_path']['path'][i]
                v = solution['optimal_path']['path'][i+1]
                if G.has_edge(u, v):
                    edges.append((u, v))
                else:
                    # Draw the full path if direct edges don't exist
                    path = nx.shortest_path(G, u, v, weight='weight')
                    edges.extend(list(zip(path[:-1], path[1:])))
            
            if edges:
                nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                     width=3, edge_color='red', 
                                     alpha=0.8, label=f"Optimal ({solution['optimal_path']['total_distance']}ms)")
        except:
            pass
    
    # Highlight heuristic path if it exists and is valid
    if solution['heuristic_path']['path'] and len(solution['heuristic_path']['path']) > 1:
        try:
            edges = []
            for i in range(len(solution['heuristic_path']['path']) - 1):
                u = solution['heuristic_path']['path'][i]
                v = solution['heuristic_path']['path'][i+1]
                if G.has_edge(u, v):
                    edges.append((u, v))
                else:
                    # Draw the full path if direct edges don't exist
                    path = nx.shortest_path(G, u, v, weight='weight')
                    edges.extend(list(zip(path[:-1], path[1:])))
            
            if edges:
                nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                     width=3, edge_color='blue', 
                                     alpha=0.8, label=f"Heuristic ({solution['heuristic_path']['total_distance']}ms)")
        except:
            pass
    
    # Draw edge labels
    edge_labels = nx.get_edge_attributes(G, 'label')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=10)
    
    # Draw node labels
    labels = {node: attrs['label'] for node, attrs in G.nodes(data=True)}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    plt.title('Hacker Movement Optimization (TSP)', pad=20)
    plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
    plt.axis('off')
    
    # Adjust layout
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')