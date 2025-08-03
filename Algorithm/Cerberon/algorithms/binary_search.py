import time
import matplotlib.pyplot as plt
from io import BytesIO
import base64

def load_passwords(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def binary_search(arr, target):
    steps = []
    left, right = 0, len(arr) - 1
    while left <= right:
        mid = (left + right) // 2
        steps.append({
            'left': left,
            'right': right,
            'mid': mid,
            'current': arr[mid],
            'target': target
        })
        if arr[mid] == target:
            return True, steps
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return False, steps

def linear_search(arr, target):
    steps = []
    for i, item in enumerate(arr):
        steps.append({
            'position': i,
            'current': item,
            'target': target
        })
        if item == target:
            return True, steps
    return False, steps

def visualize_search(steps, algorithm_name):
    positions = [step['mid'] if 'mid' in step else step['position'] for step in steps]
    values = [step['current'] for step in steps]
    targets = [step['target'] for step in steps]
    
    plt.figure(figsize=(10, 6))
    plt.plot(positions, 'bo-', label='Search Position')
    plt.axhline(y=targets[0], color='r', linestyle='--', label='Target')
    
    for i, (pos, val) in enumerate(zip(positions, values)):
        plt.text(pos, val, str(val), ha='center', va='bottom')
        plt.text(pos, pos, f"Step {i+1}", ha='center', va='top')
    
    plt.title(f'{algorithm_name} Search Steps')
    plt.xlabel('Step Number')
    plt.ylabel('Array Position / Value')
    plt.legend()
    plt.grid(True)
    
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plt.close()
    return base64.b64encode(img.getvalue()).decode('utf-8')

def compare_search_algorithms(sorted_passwords, target):
    start_time = time.time()
    binary_found, binary_steps = binary_search(sorted_passwords, target)
    binary_time = time.time() - start_time
    
    start_time = time.time()
    linear_found, linear_steps = linear_search(sorted_passwords, target)
    linear_time = time.time() - start_time
    
    binary_img = visualize_search(binary_steps, 'Binary')
    linear_img = visualize_search(linear_steps, 'Linear')
    
    return {
        'binary': {
            'found': binary_found,
            'steps': len(binary_steps),
            'time': binary_time,
            'image': binary_img
        },
        'linear': {
            'found': linear_found,
            'steps': len(linear_steps),
            'time': linear_time,
            'image': linear_img
        }
    }