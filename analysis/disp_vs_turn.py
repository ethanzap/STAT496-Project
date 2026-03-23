import glob
import json
import math
import matplotlib.pyplot as plt

def main():
    # Get all matching files in the current directory
    file_pattern = "output*.json"
    files = glob.glob(file_pattern)
    
    if not files:
        print(f"No files matching '{file_pattern}' were found.")
        return

    # We have 8 coordinates, meaning there are 7 consecutive pairs (steps)
    num_steps = 7
    total_distances = [0.0] * num_steps
    counts = [0] * num_steps
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON in {filepath}")
                continue
            
            # Iterate through each item in the file's dictionary
            for key, article_data in data.items():
                trajectory = article_data.get("political_alignment_trajectory")
                
                if trajectory:
                    # Iterate through the 7 steps (0->1, 1->2, ..., 6->7)
                    for i in range(num_steps):
                        curr_key = str(i)
                        next_key = str(i + 1)
                        
                        if curr_key in trajectory and next_key in trajectory:
                            p1 = trajectory[curr_key]
                            p2 = trajectory[next_key]
                            
                            # Validate coordinates and calculate Euclidean distance
                            if len(p1) == 2 and len(p2) == 2:
                                dist = math.dist(p1, p2)
                                total_distances[i] += dist
                                counts[i] += 1

    # Calculate the average distances
    avg_distances = []
    for i in range(num_steps):
        if counts[i] > 0:
            avg_distances.append(total_distances[i] / counts[i])
        else:
            avg_distances.append(0.0)
            
    # Generate the line plot
    x_labels = [f"{i + 1} \u2192 {i+2}" for i in range(num_steps)]
    
    plt.figure(figsize=(10, 6))
    plt.plot(x_labels, avg_distances, marker='o', linestyle='-', color='b', linewidth=2)
    
    # Formatting the plot
    plt.title('Average Displacement Over Each Round of Conversation', fontsize=14)
    plt.xlabel('Conversation Round', fontsize=12)
    plt.ylabel('Displacement', fontsize=12)
    plt.grid(True, linestyle='--', alpha=0.7)
    
    # Adjust layout and display
    plt.tight_layout()
    plt.savefig("disp_vs_turn.png", dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    main()
