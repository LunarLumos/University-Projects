// Global variables
let currentAlertTraversal = 'inorder';
let alertAnalysisData = null;

// Show selected module and hide others
function showModule(moduleId) {
    // Hide all modules
    document.querySelectorAll('.module').forEach(module => {
        module.style.display = 'none';
    });
    
    // Show selected module
    document.getElementById(`${moduleId}-module`).style.display = 'block';
    
    // Initialize module if needed
    if (moduleId === 'password') {
        initPasswordModule();
    } else if (moduleId === 'phishing') {
        initPhishingModule();
    } else if (moduleId === 'path') {
        initPathModule();
    } else if (moduleId === 'delay') {
        initDelayModule();
    }
}

// Password Attack Simulator
function initPasswordModule() {
    fetch('/password_attack')
        .then(response => response.json())
        .then(data => {
            document.getElementById('password-list').textContent = data.passwords.join('\n');
            document.getElementById('password-target').value = data.default_target;
        });
}

function runPasswordAttack() {
    const target = document.getElementById('password-target').value;
    
    fetch('/password_attack', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `target=${encodeURIComponent(target)}`
    })
    .then(response => response.json())
    .then(data => {
        // Display binary search results
        const binaryResult = document.getElementById('binary-result');
        binaryResult.innerHTML = `
            <p>Target: ${target}</p>
            <p>Found: ${data.binary.found ? 'Yes' : 'No'}</p>
            <p>Steps: ${data.binary.steps}</p>
            <p>Time: ${data.binary.time.toFixed(6)} seconds</p>
        `;
        
        // Display binary search visualization
        const binaryImage = document.getElementById('binary-image');
        binaryImage.src = `data:image/png;base64,${data.binary.image}`;
        
        // Display linear search results
        const linearResult = document.getElementById('linear-result');
        linearResult.innerHTML = `
            <p>Target: ${target}</p>
            <p>Found: ${data.linear.found ? 'Yes' : 'No'}</p>
            <p>Steps: ${data.linear.steps}</p>
            <p>Time: ${data.linear.time.toFixed(6)} seconds</p>
        `;
        
        // Display linear search visualization
        const linearImage = document.getElementById('linear-image');
        linearImage.src = `data:image/png;base64,${data.linear.image}`;
    });
}

// Log Analyzer & Sorter
function runLogAnalysis() {
    fetch('/log_analyzer')
        .then(response => response.json())
        .then(data => {
            // Display original logs
            document.getElementById('original-logs').textContent = data.sorted_by_time.join('\n');
            
            // Display time sorted logs
            document.getElementById('time-sorted-logs').textContent = data.sorted_by_time.join('\n');
            document.getElementById('time-sort-image').src = `data:image/png;base64,${data.time_sort_image}`;
            
            // Display severity sorted logs
            document.getElementById('severity-sorted-logs').textContent = data.sorted_by_severity.join('\n');
            document.getElementById('severity-sort-image').src = `data:image/png;base64,${data.severity_sort_image}`;
        });
}

// Tree-Based Alert Tracer
function runAlertAnalysis() {
    fetch('/alert_tracer')
        .then(response => response.json())
        .then(data => {
            alertAnalysisData = data;
            showTraversal('inorder');
        });
}

function showTraversal(traversalType) {
    if (!alertAnalysisData) return;
    
    currentAlertTraversal = traversalType;
    const traversal = alertAnalysisData.traversals[traversalType];
    
    // Display traversal path
    document.getElementById('traversal-path').textContent = traversal.join(' → ');
    
    // Display visualization
    document.getElementById('alert-tree-image').src = `data:image/png;base64,${alertAnalysisData.images[traversalType]}`;
}

// Phishing Redirect Tracker
function initPhishingModule() {
    fetch('/phishing_tracker')
        .then(response => response.json())
        .then(data => {
            const startSelect = document.getElementById('phishing-start');
            const endSelect = document.getElementById('phishing-end');
            
            // Clear existing options
            startSelect.innerHTML = '';
            endSelect.innerHTML = '';
            
            // Add options for each node
            data.nodes.forEach(node => {
                const option1 = document.createElement('option');
                option1.value = node.id;
                option1.textContent = `${node.label} (${node.id})`;
                
                const option2 = document.createElement('option');
                option2.value = node.id;
                option2.textContent = `${node.label} (${node.id})`;
                
                startSelect.appendChild(option1);
                endSelect.appendChild(option2);
            });
            
            // Set default values
            startSelect.value = data.default_start;
            endSelect.value = data.default_end;
        });
}

function runPhishingTracker() {
    const start = document.getElementById('phishing-start').value;
    const end = document.getElementById('phishing-end').value;
    
    fetch('/phishing_tracker', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `start=${start}&end=${end}`
    })
    .then(response => response.json())
    .then(data => {
        // Display visualization
        document.getElementById('phishing-graph-image').src = `data:image/png;base64,${data.image}`;
        
        // Display BFS path
        const bfsPath = document.getElementById('bfs-path');
        if (data.paths.bfs_path) {
            bfsPath.textContent = data.paths.bfs_path.join(' → ');
        } else {
            bfsPath.textContent = "No path found";
        }
        
        // Display DFS path
        const dfsPath = document.getElementById('dfs-path');
        if (data.paths.dfs_path) {
            dfsPath.textContent = data.paths.dfs_path.join(' → ');
        } else {
            dfsPath.textContent = "No path found";
        }
    });
}

// Secure Network Path Finder
function initPathModule() {
    fetch('/path_finder')
        .then(response => response.json())
        .then(data => {
            const startSelect = document.getElementById('path-start');
            const endSelect = document.getElementById('path-end');
            
            // Clear existing options
            startSelect.innerHTML = '';
            endSelect.innerHTML = '';
            
            // Add options for each node
            data.nodes.forEach(node => {
                const option1 = document.createElement('option');
                option1.value = node.id;
                option1.textContent = `${node.label} (${node.id})`;
                
                const option2 = document.createElement('option');
                option2.value = node.id;
                option2.textContent = `${node.label} (${node.id})`;
                
                startSelect.appendChild(option1);
                endSelect.appendChild(option2);
            });
            
            // Set default values
            startSelect.value = data.default_start;
            endSelect.value = data.default_end;
        });
}

function runPathFinder() {
    const start = document.getElementById('path-start').value;
    const end = document.getElementById('path-end').value;
    
    fetch('/path_finder', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `start=${start}&end=${end}`
    })
    .then(response => response.json())
    .then(data => {
        // Display visualization
        document.getElementById('path-graph-image').src = `data:image/png;base64,${data.image}`;
        
        // Display shortest path
        const shortestPath = document.getElementById('shortest-path');
        if (data.paths.shortest_path.path) {
            shortestPath.innerHTML = `
                <p>Path: ${data.paths.shortest_path.path.join(' → ')}</p>
                <p>Total Latency: ${data.paths.shortest_path.total_latency}ms</p>
            `;
        } else {
            shortestPath.textContent = "No path found";
        }
        
        // Display safest path
        const safestPath = document.getElementById('safest-path');
        if (data.paths.safest_path.path) {
            safestPath.innerHTML = `
                <p>Path: ${data.paths.safest_path.path.join(' → ')}</p>
                <p>Total Hops: ${data.paths.safest_path.total_hops}</p>
            `;
        } else {
            safestPath.textContent = "No path found";
        }
    });
}

// Suspicious Delay Detection
function initDelayModule() {
    fetch('/delay_detection')
        .then(response => response.json())
        .then(data => {
            const startSelect = document.getElementById('delay-start');
            
            // Clear existing options
            startSelect.innerHTML = '';
            
            // Add options for each node
            data.nodes.forEach(node => {
                const option = document.createElement('option');
                option.value = node.id;
                option.textContent = `${node.label} (${node.id})`;
                startSelect.appendChild(option);
            });
            
            // Set default value
            startSelect.value = data.default_start;
        });
}

function runDelayDetection() {
    const start = document.getElementById('delay-start').value;
    
    fetch('/delay_detection', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `start=${start}`
    })
    .then(response => response.json())
    .then(data => {
        // Display visualization
        document.getElementById('delay-graph-image').src = `data:image/png;base64,${data.image}`;
        
        // Display node distances
        const distances = document.getElementById('node-distances');
        distances.innerHTML = Object.entries(data.analysis.distances)
            .map(([node, dist]) => `<p>Node ${node}: ${dist === Infinity ? '∞' : dist}ms</p>`)
            .join('');
        
        // Display suspicious elements
        const suspicious = document.getElementById('suspicious-elements');
        
        let suspiciousHtml = `<p>Average Latency: ${data.analysis.average_latency.toFixed(2)}ms</p>`;
        
        if (data.analysis.suspicious_edges.length > 0) {
            suspiciousHtml += `<p>High Latency Links:</p><ul>${
                data.analysis.suspicious_edges.map(edge => 
                    `<li>${edge[0]} → ${edge[1]}</li>`
                ).join('')
            }</ul>`;
        } else {
            suspiciousHtml += "<p>No high latency links detected.</p>";
        }
        
        if (data.analysis.negative_cycle_edges.length > 0) {
            suspiciousHtml += `<p>Potential Issues:</p><ul>${
                data.analysis.negative_cycle_edges.map(edge => 
                    `<li>${edge[0]} → ${edge[1]}</li>`
                ).join('')
            }</ul>`;
        } else {
            suspiciousHtml += "<p>No potential issues detected.</p>";
        }
        
        suspicious.innerHTML = suspiciousHtml;
    });
}

// Hacker Movement Optimizer
function runHackerOptimizer() {
    const nodes = document.getElementById('hacker-nodes').value;
    
    fetch('/hacker_optimizer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: `nodes=${nodes}`
    })
    .then(response => response.json())
    .then(data => {
        // Display visualization
        document.getElementById('hacker-graph-image').src = `data:image/png;base64,${data.image}`;
        
        // Display optimal path
        const optimalPath = document.getElementById('optimal-path');
        if (data.solution.optimal_path.path) {
            optimalPath.innerHTML = `
                <p>Path: ${data.solution.optimal_path.path.join(' → ')}</p>
                <p>Total Distance: ${data.solution.optimal_path.total_distance}ms</p>
            `;
        } else {
            optimalPath.textContent = "No optimal path found (too many nodes for exact solution)";
        }
        
        // Display heuristic path
        const heuristicPath = document.getElementById('heuristic-path');
        if (data.solution.heuristic_path.path) {
            heuristicPath.innerHTML = `
                <p>Path: ${data.solution.heuristic_path.path.join(' → ')}</p>
                <p>Total Distance: ${data.solution.heuristic_path.total_distance}ms</p>
            `;
        } else {
            heuristicPath.textContent = "No path found";
        }
    });
}

// Initialize the application
document.addEventListener('DOMContentLoaded', () => {
    // Show the first module by default
    showModule('password');
    
    // Initialize modules that need it
    initPasswordModule();
});