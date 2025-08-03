import matplotlib.pyplot as plt
from io import BytesIO
import base64
import time

def quick_sort(arr, steps=None, level=0, side='root'):
    if steps is None:
        steps = []
    
    if len(arr) <= 1:
        return arr, steps
    
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    
    steps.append({
        'level': level,
        'side': side,
        'pivot': pivot,
        'left': left.copy(),
        'middle': middle.copy(),
        'right': right.copy(),
        'full': arr.copy()
    })
    
    left_sorted, steps = quick_sort(left, steps, level+1, 'left')
    right_sorted, steps = quick_sort(right, steps, level+1, 'right')
    
    result = left_sorted + middle + right_sorted
    
    steps.append({
        'level': level,
        'side': side,
        'result': result.copy(),
        'full': arr.copy()
    })
    
    return result, steps

def visualize_quick_sort(steps):
    plt.figure(figsize=(12, 8))
    levels = max(step['level'] for step in steps) + 1
    
    for i, step in enumerate(steps):
        plt.subplot(len(steps), 1, i+1)
        
        if 'pivot' in step:
            plt.bar(['Left'] * len(step['left']) + ['Pivot'] * len(step['middle']) + ['Right'] * len(step['right']), 
                    step['left'] + step['middle'] + step['right'])
            plt.title(f"Level {step['level']} ({step['side']}): Pivot = {step['pivot']}")
        else:
            plt.bar(range(len(step['result'])), step['result'])
            plt.title(f"Level {step['level']} ({step['side']}): Merged {len(step['result'])} elements")
        
        plt.grid(True)
    
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

def detect_anomalies(log_file):
    with open(log_file, 'r') as file:
        logs = [line.strip() for line in file]
    
    # Extract response times (simulated for this example)
    # In a real system, these would come from actual log data
    import random
    response_times = [random.randint(50, 200) for _ in logs]  # Most between 50-200ms
    # Add some anomalies
    response_times[2] = 1500  # Database timeout
    response_times[5] = 2500  # Disk space critical
    
    # Create list of tuples (time, log)
    log_data = list(zip(response_times, logs))
    
    # Sort by response time
    start_time = time.time()
    sorted_logs, steps = quick_sort(log_data.copy())
    sort_duration = time.time() - start_time
    
    # Identify anomalies (top 10% slowest responses)
    threshold = int(0.9 * len(sorted_logs))
    normal_logs = sorted_logs[:threshold]
    anomaly_logs = sorted_logs[threshold:]
    
    # Visualize
    img = visualize_quick_sort(steps)
    
    return {
        'sorted_logs': [log for _, log in sorted_logs],
        'normal_logs': [log for _, log in normal_logs],
        'anomaly_logs': [log for _, log in anomaly_logs],
        'sort_duration': sort_duration,
        'visualization': img
    }