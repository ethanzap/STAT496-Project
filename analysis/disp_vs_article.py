import glob
import json
import matplotlib.pyplot as plt
import os
import numpy as np

def main():
    # 1. Get all output*.json files in the current directory
    files = glob.glob("output*.json")
    
    # 2. Filter out files that contain the character 'c' in their filename
    files = [f for f in files if 'c' not in os.path.basename(f)]
    
    if not files:
        print("No matching files found.")
        return

    # Data structure: { article_key: [ (filename, trajectory_points), ... ] }
    trajectories_by_key = {}
    
    for filepath in files:
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse JSON in {filepath}")
                continue
            
            # Group the trajectories by the 18 common keys
            for key, article_data in data.items():
                if key not in trajectories_by_key:
                    trajectories_by_key[key] = []
                    
                trajectory_dict = article_data.get("political_alignment_trajectory", {})
                if trajectory_dict:
                    # Sort sub-keys to ensure the 8 coordinate pairs are in chronological order
                    points = []
                    for step in sorted(trajectory_dict.keys(), key=int):
                        point = trajectory_dict[step]
                        if point is not None and len(point) == 2:
                            points.append(point)
                    
                    if len(points) > 1:
                        start_x, start_y = points[0]
                        normalized_points = [[x - start_x, y - start_y] for x, y in points]
                        trajectories_by_key[key].append((os.path.basename(filepath), normalized_points))

    # Create output directory for the plots
    out_dir = "key_trajectories_plots"
    os.makedirs(out_dir, exist_ok=True)

    # Generate a plot for each keys
    for key, trajectories in trajectories_by_key.items():
        if not trajectories:
            continue
            
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Assign a different color for each file's trajectory
        colors = plt.cm.tab10(np.linspace(0, 1, len(trajectories)))
        
        for (filename, points), color in zip(trajectories, colors):
            points_np = np.array(points)
            x_vals = points_np[:, 0]
            y_vals = points_np[:, 1]
            
            # Plot the main trajectory line
            ax.plot(x_vals, y_vals, marker='o', markersize=4, alpha=0.1, color=color)
            
            # Add directional arrows
            u_dir = np.diff(x_vals)
            v_dir = np.diff(y_vals)
            ax.quiver(x_vals[:-1], y_vals[:-1], u_dir, v_dir, angles='xy', scale_units='xy', scale=1, 
                      color=color, width=0.005, headwidth=3, alpha=0.1)
            
            # Add overall displacement vector
            disp_u = x_vals[-1] - x_vals[0]
            disp_v = y_vals[-1] - y_vals[0]
            ax.plot([x_vals[0], x_vals[-1]], [y_vals[0], y_vals[-1]], alpha=1.0, label=filename, color=color)
            ax.quiver(x_vals[0], y_vals[0], disp_u, disp_v, angles='xy', scale_units='xy', scale=1, 
                      color=color, width=0.005, headwidth=3, alpha=1.0)

            # Mark start point as a triangle and end point as a square
            ax.scatter(x_vals[0], y_vals[0], c=[color], s=60, marker='^', zorder=5, edgecolors='white')
            ax.scatter(x_vals[-1], y_vals[-1], c=[color], s=60, marker='s', zorder=5, edgecolors='white')

        ax.set_xlabel("Economic Axis")
        ax.set_ylabel("Social Axis")
        
        # Shorten title if the key is a long path string
        short_title = key.split('/')[-1] if '/' in key else key
        ax.set_title(f"Political Alignment Trajectories\n{short_title}")
        
        ax.grid(True, linestyle='--', alpha=0.5)
        ax.set_aspect('equal', adjustable='datalim')
        
        # Add legend outside the plot box
        ax.legend(title="Source Files", loc="center left", bbox_to_anchor=(1.02, 0.5), fontsize=8)
        
        # Sanitize filename for saving
        safe_key = key.replace("/", "_").replace("\\", "_").replace(" ", "_").replace(":", "_")
        out_path = os.path.join(out_dir, f"{safe_key}.png")
        
        plt.tight_layout()
        plt.savefig(out_path, dpi=200, bbox_inches="tight")
        plt.close()
        
    print(f"Generated {len(trajectories_by_key)} graphs in the '{out_dir}' directory.")

if __name__ == "__main__":
    main()
