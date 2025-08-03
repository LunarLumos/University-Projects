import json
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
import base64

def load_alert_tree(filename):
    with open(filename, 'r') as file:
        return json.load(file)

def build_tree(data, parent=None, G=None, pos=None, x=0, y=0, dx=1, dy=1):
    if G is None:
        G = nx.DiGraph()
        pos = {}
    
    node_id = data['node'] if 'node' in data else data['root']
    G.add_node(node_id)
    pos[node_id] = (x, y)
    
    if parent is not None:
        G.add_edge(parent, node_id)
    
    if 'children' in data and data['children']:
        num_children = len(data['children'])
        x_start = x - (num_children - 1) * dx / 2
        
        for i, child in enumerate(data['children']):
            child_x = x_start + i * dx
            child_y = y - dy
            G, pos = build_tree(child, node_id, G, pos, child_x, child_y, dx*0.8, dy)
    
    return G, pos

def traverse_tree(data, traversal_type='inorder'):
    result = []
    
    def inorder(node):
        if 'children' in node and node['children']:
            if len(node['children']) > 0:
                inorder(node['children'][0])
        result.append(node['node'] if 'node' in node else node['root'])
        if 'children' in node and node['children']:
            for child in node['children'][1:]:
                inorder(child)
    
    def preorder(node):
        result.append(node['node'] if 'node' in node else node['root'])
        if 'children' in node and node['children']:
            for child in node['children']:
                preorder(child)
    
    def postorder(node):
        if 'children' in node and node['children']:
            for child in node['children']:
                postorder(child)
        result.append(node['node'] if 'node' in node else node['root'])
    
    def bfs(node):
        from collections import deque
        queue = deque()
        queue.append(node)
        
        while queue:
            current = queue.popleft()
            result.append(current['node'] if 'node' in current else current['root'])
            if 'children' in current and current['children']:
                for child in current['children']:
                    queue.append(child)
    
    if traversal_type == 'inorder':
        inorder(data)
    elif traversal_type == 'preorder':
        preorder(data)
    elif traversal_type == 'postorder':
        postorder(data)
    elif traversal_type == 'bfs':
        bfs(data)
    
    return result

def visualize_tree(G, pos, traversal_order=None):
    plt.figure(figsize=(10, 8))
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color='skyblue', alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=2, edge_color='gray', arrows=True)
    
    # Draw labels
    labels = {node: node for node in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, font_size=10, font_weight='bold')
    
    # Highlight traversal path if provided
    if traversal_order:
        for i in range(len(traversal_order) - 1):
            plt.plot([pos[traversal_order[i]][0], pos[traversal_order[i+1]][0]],
                    [pos[traversal_order[i]][1], pos[traversal_order[i+1]][1]],
                    'r-', alpha=0.5, linewidth=2)
    
    plt.title('Alert Tree Visualization')
    plt.axis('off')
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

def analyze_alert_tree(tree_file):
    alert_tree = load_alert_tree(tree_file)
    G, pos = build_tree(alert_tree)
    
    traversals = {
        'inorder': traverse_tree(alert_tree, 'inorder'),
        'preorder': traverse_tree(alert_tree, 'preorder'),
        'postorder': traverse_tree(alert_tree, 'postorder'),
        'bfs': traverse_tree(alert_tree, 'bfs')
    }
    
    images = {}
    for name, order in traversals.items():
        images[name] = visualize_tree(G, pos, order)
    
    return {
        'traversals': traversals,
        'images': images
    }