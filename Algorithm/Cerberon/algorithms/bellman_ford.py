import json
import matplotlib
matplotlib.use('Agg')  # Must be before pyplot import
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import networkx as nx
import os

def load_network_graph(filename):
    """Load network graph with error handling"""
    try:
        with open(filename, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        raise Exception(f"Network graph file not found: {filename}")
    except json.JSONDecodeError:
        raise Exception(f"Invalid JSON in network graph file: {filename}")

def build_graph(data):
    """Build networkx graph with validation"""
    if not data or 'nodes' not in data or 'edges' not in data:
        raise ValueError("Invalid graph data structure")
    
    G = nx.DiGraph()
    
    # Add nodes with attributes
    for node in data['nodes']:
        if 'id' not in node or 'label' not in node or 'group' not in node:
            raise ValueError("Node missing required fields")
        G.add_node(node['id'], label=node['label'], group=node['group'])
    
    # Add edges with attributes
    for edge in data['edges']:
        if 'from' not in edge or 'to' not in edge or 'weight' not in edge:
            raise ValueError("Edge missing required fields")
        G.add_edge(edge['from'], edge['to'], 
                  weight=float(edge['weight']), 
                  label=edge.get('label', ''))
    
    return G

def bellman_ford_detection(graph, start_node):
    """Bellman-Ford algorithm with enhanced error checking"""
    if start_node not in graph:
        raise ValueError(f"Start node {start_node} not in graph")
    
    distances = {node: float('inf') for node in graph.nodes()}
    distances[start_node] = 0
    
    # Relax edges
    for _ in range(len(graph.nodes()) - 1):
        for u, v, data in graph.edges(data=True):
            if distances[u] + data['weight'] < distances[v]:
                distances[v] = distances[u] + data['weight']
    
    # Check for negative cycles
    negative_edges = []
    for u, v, data in graph.edges(data=True):
        if distances[u] + data['weight'] < distances[v]:
            negative_edges.append((u, v))
    
    return distances, negative_edges

def detect_suspicious_delays(graph_data, start_node):
    """Main detection function with comprehensive validation"""
    try:
        G = build_graph(graph_data)
        
        # Validate start node
        if start_node not in G:
            available_nodes = list(G.nodes())
            raise ValueError(f"Start node {start_node} not found. Available nodes: {available_nodes}")
        
        # Calculate average latency
        weights = [data['weight'] for _, _, data in G.edges(data=True)]
        avg_weight = sum(weights) / len(weights) if weights else 0
        
        # Identify suspicious edges (2x average latency)
        suspicious_edges = [
            (u, v) for u, v, data in G.edges(data=True) 
            if data['weight'] > 2 * avg_weight
        ] if avg_weight > 0 else []
        
        # Run Bellman-Ford
        distances, negative_edges = bellman_ford_detection(G, start_node)
        
        return {
            'distances': distances,
            'suspicious_edges': suspicious_edges,
            'negative_cycle_edges': negative_edges,
            'average_latency': avg_weight,
            'status': 'success'
        }
    
    except Exception as e:
        return {
            'status': 'error',
            'message': str(e),
            'distances': {},
            'suspicious_edges': [],
            'negative_cycle_edges': [],
            'average_latency': 0
        }

def visualize_suspicious_delays(graph_data, analysis):
    """Visualization with robust error handling"""
    try:
        plt.figure(figsize=(14, 10))
        G = build_graph(graph_data)
        pos = nx.spring_layout(G, seed=42)
        
        # Node styling
        groups = set(nx.get_node_attributes(G, 'group').values())
        colors = plt.cm.tab10.colors
        group_colors = {group: colors[i % len(colors)] for i, group in enumerate(groups)}
        
        for group in groups:
            nodes = [n for n, attrs in G.nodes(data=True) if attrs['group'] == group]
            nx.draw_networkx_nodes(
                G, pos, nodelist=nodes,
                node_color=[group_colors[group]] * len(nodes),
                node_size=2500,
                label=group
            )
        
        # Edge styling
        all_edges = list(G.edges())
        normal_edges = [
            e for e in all_edges
            if e not in analysis.get('suspicious_edges', [])
            and e not in analysis.get('negative_cycle_edges', [])
        ]
        
        if normal_edges:
            nx.draw_networkx_edges(
                G, pos, edgelist=normal_edges,
                width=1, edge_color='gray',
                alpha=0.3, arrows=True
            )
        
        if analysis.get('suspicious_edges'):
            nx.draw_networkx_edges(
                G, pos, edgelist=analysis['suspicious_edges'],
                width=3, edge_color='red',
                alpha=0.8, label='High Latency'
            )
        
        if analysis.get('negative_cycle_edges'):
            nx.draw_networkx_edges(
                G, pos, edgelist=analysis['negative_cycle_edges'],
                width=3, edge_color='purple',
                alpha=0.8, label='Potential Issue'
            )
        
        # Labels and annotations
        edge_labels = nx.get_edge_attributes(G, 'label')
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
        
        node_labels = {
            node: f"{attrs['label']}\n({analysis['distances'].get(node, '∞')}ms)"
            for node, attrs in G.nodes(data=True)
        }
        nx.draw_networkx_labels(G, pos, labels=node_labels, font_size=9)
        
        plt.title('Network Latency Analysis\n(Bellman-Ford Algorithm)', pad=20)
        plt.legend(loc='upper right', bbox_to_anchor=(1.15, 1))
        plt.axis('off')
        
        # Save to buffer
        img = BytesIO()
        plt.savefig(img, format='png', bbox_inches='tight', dpi=100)
        img.seek(0)
        plt.close()
        
        return base64.b64encode(img.getvalue()).decode('utf-8')
    
    except Exception as e:
        print(f"Visualization error: {str(e)}")
        # Return a blank image with error message
        plt.figure(figsize=(8, 2))
        plt.text(0.5, 0.5, 'Visualization Error', ha='center', va='center')
        plt.axis('off')
        img = BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        plt.close()
        return base64.b64encode(img.getvalue()).decode('utf-8')