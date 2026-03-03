import json
import matplotlib.pyplot as plt
import os
import csv
import numpy as np
from matplotlib.collections import LineCollection


INPUT_FILE = "output.json"
OUTPUT_DIR = "plots"
CSV_OUTPUT = "trajectories_export.csv"


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_output_dir():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)


def sanitize_filename(name):
    return name.replace("/", "_").replace("\\", "_").replace(" ", "_")


def extract_trajectory(article_data):
    raw_traj = article_data["political_alignment_trajectory"]

    if not isinstance(raw_traj, dict):
        return None

    trajectory = []

    for k in sorted(raw_traj.keys(), key=int):
        point = raw_traj[k]
        if point is not None and len(point) == 2:
            trajectory.append(point)

    if len(trajectory) < 2:
        return None

    return trajectory


def plot_background_field(ax, x_bounds, y_bounds, u, v, color, alpha=0.1):
    """
    Plots a background vector field representing the overall displacement.
    """
    if u == 0 and v == 0:
        return

    x = np.linspace(x_bounds[0], x_bounds[1], 20)
    y = np.linspace(y_bounds[0], y_bounds[1], 20)
    X, Y = np.meshgrid(x, y)
    U = np.full_like(X, u)
    V = np.full_like(Y, v)
    
    ax.quiver(X, Y, U, V, color=color, alpha=alpha, width=0.003)


def plot_single_article(article_name, trajectory):
    trajectory = np.array(trajectory)
    x_vals = trajectory[:, 0]
    y_vals = trajectory[:, 1]

    fig, ax = plt.subplots(figsize=(8, 8))

    # Determine bounds with padding
    x_min, x_max = x_vals.min(), x_vals.max()
    y_min, y_max = y_vals.min(), y_vals.max()
    x_pad = max(0.5, (x_max - x_min) * 0.2)
    y_pad = max(0.5, (y_max - y_min) * 0.2)
    xlims = (x_min - x_pad, x_max + x_pad)
    ylims = (y_min - y_pad, y_max + y_pad)

    # Background vector field (Overall displacement)
    if len(trajectory) >= 2:
        disp = trajectory[-1] - trajectory[0]
        plot_background_field(ax, xlims, ylims, disp[0], disp[1], 'gray', alpha=0.2)

    # Gradient line
    points = np.array([x_vals, y_vals]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    # Create a colormap for the steps
    cmap = plt.get_cmap('viridis')
    norm = plt.Normalize(0, len(x_vals) - 1)
    
    lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=3, alpha=0.8)
    lc.set_array(np.arange(len(x_vals) - 1))
    ax.add_collection(lc)

    # Directional arrows on trajectory
    u_dir = np.diff(x_vals)
    v_dir = np.diff(y_vals)
    
    # Color arrows based on step index to match line gradient
    ax.quiver(x_vals[:-1], y_vals[:-1], u_dir, v_dir, np.arange(len(u_dir)), 
              cmap=cmap, norm=norm, angles='xy', scale_units='xy', scale=1, 
              width=0.012, headwidth=4, alpha=0.9)

    # Start and End markers
    ax.scatter(x_vals[0], y_vals[0], c='green', s=100, label='Start', zorder=5, edgecolors='white')
    ax.scatter(x_vals[-1], y_vals[-1], c='red', s=100, label='End', zorder=5, edgecolors='white')

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    ax.set_xlabel("Economic Axis (Left ⟵ → Right)")
    ax.set_ylabel("Social Axis (Libertarian ⟵ → Authoritarian)")
    ax.set_title(f"Political Alignment Trajectory\n{article_name}")

    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', alpha=0.3)
    ax.legend()

    safe_name = sanitize_filename(article_name)
    out_path = os.path.join(OUTPUT_DIR, f"{safe_name}.png")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {out_path}")


def plot_combined(all_trajectories):
    fig, ax = plt.subplots(figsize=(10, 10))

    # Collect all points for bounds
    all_x = []
    all_y = []
    traj_list = []
    for t in all_trajectories.values():
        t_np = np.array(t)
        all_x.extend(t_np[:, 0])
        all_y.extend(t_np[:, 1])
        traj_list.append(t_np)

    x_min, x_max = min(all_x), max(all_x)
    y_min, y_max = min(all_y), max(all_y)
    x_pad = max(0.5, (x_max - x_min) * 0.1)
    y_pad = max(0.5, (y_max - y_min) * 0.1)
    xlims = (x_min - x_pad, x_max + x_pad)
    ylims = (y_min - y_pad, y_max + y_pad)

    colors = plt.cm.tab10(np.linspace(0, 1, len(all_trajectories)))

    for (article_name, trajectory), color in zip(all_trajectories.items(), colors):
        trajectory = np.array(trajectory)
        x_vals = trajectory[:, 0]
        y_vals = trajectory[:, 1]

        # Background vector field for this article
        if len(trajectory) >= 2:
            disp = trajectory[-1] - trajectory[0]
            plot_background_field(ax, xlims, ylims, disp[0], disp[1], color, alpha=0.1)

        ax.plot(x_vals, y_vals, marker='o', markersize=4, alpha=0.7, label=article_name, color=color)

        # Arrows
        u_dir = np.diff(x_vals)
        v_dir = np.diff(y_vals)
        ax.quiver(x_vals[:-1], y_vals[:-1], u_dir, v_dir, angles='xy', scale_units='xy', scale=1, color=color, width=0.005, headwidth=3, alpha=0.8)

        # Start/End markers
        ax.scatter(x_vals[0], y_vals[0], c=[color], s=60, marker='^', zorder=5, edgecolors='white')
        ax.scatter(x_vals[-1], y_vals[-1], c=[color], s=60, marker='s', zorder=5, edgecolors='white')

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    ax.set_xlabel("Economic Axis (Left ⟵ → Right)")
    ax.set_ylabel("Social Axis (Libertarian ⟵ → Authoritarian)")
    ax.set_title("Combined Political Alignment Trajectories")

    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', alpha=0.3)

    # Legend outside plot (prevents overlap clutter)
    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=8
    )

    out_path = os.path.join(OUTPUT_DIR, "all_articles_combined.png")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {out_path}")


def export_csv(all_trajectories):
    out_path = os.path.join(OUTPUT_DIR, CSV_OUTPUT)

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Header
        writer.writerow(["article", "stage", "x_economic", "y_social"])

        for article_name, trajectory in all_trajectories.items():
            for stage, (x, y) in enumerate(trajectory):
                writer.writerow([article_name, stage, x, y])

    print(f"Saved: {out_path}")


def main():
    ensure_output_dir()

    data = load_data(INPUT_FILE)

    all_trajectories = {}

    for article_name, article_data in data.items():

        if "political_alignment_trajectory" not in article_data:
            continue

        trajectory = extract_trajectory(article_data)

        if trajectory is None:
            print(f"Skipping (invalid): {article_name}")
            continue

        plot_single_article(article_name, trajectory)
        all_trajectories[article_name] = trajectory

    if all_trajectories:
        plot_combined(all_trajectories)
        export_csv(all_trajectories)
    else:
        print("No valid trajectories found.")


if __name__ == "__main__":
    main()
