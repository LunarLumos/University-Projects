from flask import Flask, render_template, request, jsonify
import os
from algorithms.binary_search import load_passwords, compare_search_algorithms
from algorithms.merge_sort import analyze_logs
from algorithms.quick_sort import detect_anomalies
from algorithms.tree_traversal import analyze_alert_tree
from algorithms.bfs_dfs import detect_phishing_route, visualize_graph_paths
from algorithms.dijkstra import find_secure_paths, visualize_secure_paths
from algorithms.bellman_ford import detect_suspicious_delays, visualize_suspicious_delays
from algorithms.tsp import optimize_hacker_route, visualize_tsp_solution
import json

app = Flask(__name__)
app.config.from_pyfile('config.py')

@app.route('/')
def index():
    return render_template('index.html')

# Binary Search - Password Attack Simulator
@app.route('/password_attack', methods=['GET', 'POST'])
def password_attack():
    passwords = load_passwords(os.path.join(app.config['DATA_FOLDER'], 'passwords.txt'))
    sorted_passwords = sorted(passwords)
    
    if request.method == 'POST':
        target = request.form.get('target', 'admin')
        result = compare_search_algorithms(sorted_passwords, target)
        return jsonify(result)
    
    return jsonify({
        'passwords': sorted_passwords,
        'default_target': 'admin'
    })

# Merge Sort - Log Analyzer
@app.route('/log_analyzer', methods=['GET'])
def log_analyzer():
    result = analyze_logs(os.path.join(app.config['DATA_FOLDER'], 'log_entries.txt'))
    return jsonify(result)

# Quick Sort - Anomaly Detection
@app.route('/anomaly_detection', methods=['GET'])
def anomaly_detection():
    result = detect_anomalies(os.path.join(app.config['DATA_FOLDER'], 'log_entries.txt'))
    return jsonify(result)

# Tree Traversal - Alert Tracer
@app.route('/alert_tracer', methods=['GET'])
def alert_tracer():
    result = analyze_alert_tree(os.path.join(app.config['DATA_FOLDER'], 'alert_tree.json'))
    return jsonify(result)

# BFS/DFS - Phishing Tracker
@app.route('/phishing_tracker', methods=['GET', 'POST'])
def phishing_tracker():
    with open(os.path.join(app.config['DATA_FOLDER'], 'network_graph.json')) as f:
        graph_data = json.load(f)
    
    if request.method == 'POST':
        start = int(request.form.get('start', 1))
        end = int(request.form.get('end', 4))
        paths = detect_phishing_route(graph_data, start, end)
        image = visualize_graph_paths(graph_data, {
            'BFS': paths['bfs_path'],
            'DFS': paths['dfs_path']
        })
        return jsonify({
            'paths': paths,
            'image': image
        })
    
    return jsonify({
        'nodes': graph_data['nodes'],
        'default_start': 1,
        'default_end': 4
    })

# Dijkstra - Secure Path Finder
@app.route('/path_finder', methods=['GET', 'POST'])
def path_finder():
    with open(os.path.join(app.config['DATA_FOLDER'], 'network_graph.json')) as f:
        graph_data = json.load(f)
    
    if request.method == 'POST':
        start = int(request.form.get('start', 1))
        end = int(request.form.get('end', 5))
        paths = find_secure_paths(graph_data, start, end)
        image = visualize_secure_paths(graph_data, paths)
        return jsonify({
            'paths': paths,
            'image': image
        })
    
    return jsonify({
        'nodes': graph_data['nodes'],
        'default_start': 1,
        'default_end': 5
    })

# Bellman-Ford - Suspicious Delay Detection
@app.route('/delay_detection', methods=['GET', 'POST'])
def delay_detection():
    with open(os.path.join(app.config['DATA_FOLDER'], 'network_graph.json')) as f:
        graph_data = json.load(f)
    
    if request.method == 'POST':
        start = int(request.form.get('start', 1))
        analysis = detect_suspicious_delays(graph_data, start)
        image = visualize_suspicious_delays(graph_data, analysis)
        return jsonify({
            'analysis': analysis,
            'image': image
        })
    
    return jsonify({
        'nodes': graph_data['nodes'],
        'default_start': 1
    })

# TSP - Hacker Movement Optimizer
@app.route('/hacker_optimizer', methods=['GET', 'POST'])
def hacker_optimizer():
    with open(os.path.join(app.config['DATA_FOLDER'], 'network_graph.json')) as f:
        graph_data = json.load(f)
    
    if request.method == 'POST':
        nodes = list(map(int, request.form.get('nodes', '1,2,3,4').split(',')))
        solution = optimize_hacker_route(graph_data, nodes)
        image = visualize_tsp_solution(graph_data, solution)
        return jsonify({
            'solution': solution,
            'image': image
        })
    
    return jsonify({
        'nodes': graph_data['nodes'],
        'default_nodes': '1,2,3,4'
    })

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'])