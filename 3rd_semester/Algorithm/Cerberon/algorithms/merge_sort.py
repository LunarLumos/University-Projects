import matplotlib.pyplot as plt
from io import BytesIO
import base64
import time

def merge_sort(arr, steps=None, level=0):
    if steps is None:
        steps = []
    
    if len(arr) > 1:
        mid = len(arr) // 2
        left = arr[:mid]
        right = arr[mid:]
        
        steps.append({
            'action': 'split',
            'left': left.copy(),
            'right': right.copy(),
            'full': [x[0] for x in arr],  # Extract just the time_seconds for visualization
            'level': level
        })
        
        left, steps = merge_sort(left, steps, level+1)
        right, steps = merge_sort(right, steps, level+1)
        
        i = j = k = 0
        
        while i < len(left) and j < len(right):
            if left[i][0] < right[j][0]:  # Compare time_seconds
                arr[k] = left[i]
                i += 1
            else:
                arr[k] = right[j]
                j += 1
            k += 1
        
        while i < len(left):
            arr[k] = left[i]
            i += 1
            k += 1
        
        while j < len(right):
            arr[k] = right[j]
            j += 1
            k += 1
        
        steps.append({
            'action': 'merge',
            'result': [x[0] for x in arr],  # Extract just the time_seconds for visualization
            'left': [x[0] for x in left],
            'right': [x[0] for x in right],
            'full': [x[0] for x in arr],
            'level': level
        })
    
    return arr, steps

def visualize_sort(steps):
    plt.figure(figsize=(12, 8))
    
    for i, step in enumerate(steps):
        plt.subplot(len(steps), 1, i+1)
        
        if step['action'] == 'split':
            # For split steps, show left and right partitions
            left_data = step['left']
            right_data = step['right']
            
            # Convert to numerical values if they're tuples
            if isinstance(left_data[0], tuple):
                left_data = [x[0] for x in left_data]
                right_data = [x[0] for x in right_data]
            
            plt.bar(['Left'] * len(left_data) + ['Right'] * len(right_data), 
                   left_data + right_data)
            plt.title(f"Level {step['level']}: Split into {len(left_data)} and {len(right_data)} elements")
        else:
            # For merge steps, show the merged result
            result_data = step['result']
            
            # Convert to numerical values if they're tuples
            if isinstance(result_data[0], tuple):
                result_data = [x[0] for x in result_data]
            
            plt.bar(range(len(result_data)), result_data)
            plt.title(f"Level {step['level']}: Merged {len(result_data)} elements")
        
        plt.grid(True)
    
    plt.tight_layout()
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

def analyze_logs(log_file):
    with open(log_file, 'r') as file:
        logs = [line.strip() for line in file]
    
    # Extract timestamps and severity levels
    timestamps = [log.split()[1] for log in logs]
    severities = [log.split()[2] for log in logs]
    
    # Convert timestamps to seconds since midnight for sorting
    time_seconds = []
    for ts in timestamps:
        h, m, s = map(int, ts.split(':'))
        time_seconds.append(h * 3600 + m * 60 + s)
    
    # Create a list of tuples for sorting (time_seconds, severity, log)
    log_data = list(zip(time_seconds, severities, logs))
    
    # Sort by time
    start_time = time.time()
    sorted_by_time, time_steps = merge_sort(log_data.copy())
    time_sort_duration = time.time() - start_time
    
    # Sort by severity (convert severity to numerical value for comparison)
    severity_order = {'INFO': 0, 'WARNING': 1, 'ERROR': 2, 'CRITICAL': 3}
    severity_data = [(severity_order[sev], ts, log) for ts, sev, log in log_data]
    
    start_time = time.time()
    sorted_by_severity, severity_steps = merge_sort(severity_data.copy())
    severity_sort_duration = time.time() - start_time
    
    # Convert back to original format
    sorted_by_severity = [(ts, ['INFO', 'WARNING', 'ERROR', 'CRITICAL'][sev], log) 
                         for sev, ts, log in sorted_by_severity]
    
    time_img = visualize_sort(time_steps)
    severity_img = visualize_sort(severity_steps)
    
    return {
        'sorted_by_time': [log for _, _, log in sorted_by_time],
        'sorted_by_severity': [log for _, _, log in sorted_by_severity],
        'time_sort_duration': time_sort_duration,
        'severity_sort_duration': severity_sort_duration,
        'time_sort_image': time_img,
        'severity_sort_image': severity_img
    }
