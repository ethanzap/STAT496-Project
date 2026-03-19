import json
import matplotlib.pyplot as plt
import os
import numpy as np
from matplotlib.collections import LineCollection
from argparse import ArgumentParser

def get_args():
    parser = ArgumentParser()
    parser.add_argument("--input_file", type=str, default="output.json")
    parser.add_argument("--output_dir", type=str, default="plots")
    return parser.parse_args()

def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_output_dir(output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


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
    if u == 0 and v == 0:
        return
    x = np.linspace(x_bounds[0], x_bounds[1], 20)
    y = np.linspace(y_bounds[0], y_bounds[1], 20)
    X, Y = np.meshgrid(x, y)
    U = np.full_like(X, u)
    V = np.full_like(Y, v)
    
    ax.quiver(X, Y, U, V, color=color, alpha=alpha, width=0.003)


def plot_single_article(article_name, trajectory, output_dir):
    trajectory = np.array(trajectory)
    x_vals = trajectory[:, 0]
    y_vals = trajectory[:, 1]

    fig, ax = plt.subplots(figsize=(8, 8))

    x_min, x_max = x_vals.min(), x_vals.max()
    y_min, y_max = y_vals.min(), y_vals.max()
    x_pad = max(0.5, (x_max - x_min) * 0.2)
    y_pad = max(0.5, (y_max - y_min) * 0.2)
    xlims = (x_min - x_pad, x_max + x_pad)
    ylims = (y_min - y_pad, y_max + y_pad)

    if len(trajectory) >= 2:
        disp = trajectory[-1] - trajectory[0]
        plot_background_field(ax, xlims, ylims, disp[0], disp[1], 'gray', alpha=0.2)

    points = np.array([x_vals, y_vals]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    cmap = plt.get_cmap('viridis')
    norm = plt.Normalize(0, len(x_vals) - 1)
    
    lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=3, alpha=0.8)
    lc.set_array(np.arange(len(x_vals) - 1))
    ax.add_collection(lc)

    u_dir = np.diff(x_vals)
    v_dir = np.diff(y_vals)
    
    ax.quiver(x_vals[:-1], y_vals[:-1], u_dir, v_dir, np.arange(len(u_dir)), 
              cmap=cmap, norm=norm, angles='xy', scale_units='xy', scale=1, 
              width=0.012, headwidth=4, alpha=0.9)

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
    out_path = os.path.join(output_dir, f"{safe_name}.png")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {out_path}")


def plot_combined(all_trajectories, output_dir):
    fig, ax = plt.subplots(figsize=(10, 10))

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

        if len(trajectory) >= 2:
            disp = trajectory[-1] - trajectory[0]
            plot_background_field(ax, xlims, ylims, disp[0], disp[1], color, alpha=0.1)

        ax.plot(x_vals, y_vals, marker='o', markersize=4, alpha=0.7, label=article_name, color=color)

        u_dir = np.diff(x_vals)
        v_dir = np.diff(y_vals)
        ax.quiver(x_vals[:-1], y_vals[:-1], u_dir, v_dir, angles='xy', scale_units='xy', scale=1, color=color, width=0.005, headwidth=3, alpha=0.8)

        ax.scatter(x_vals[0], y_vals[0], c=[color], s=60, marker='^', zorder=5, edgecolors='white')
        ax.scatter(x_vals[-1], y_vals[-1], c=[color], s=60, marker='s', zorder=5, edgecolors='white')

    ax.set_xlim(xlims)
    ax.set_ylim(ylims)

    ax.set_xlabel("Economic Axis (Left ⟵ → Right)")
    ax.set_ylabel("Social Axis (Libertarian ⟵ → Authoritarian)")
    ax.set_title("Combined Political Alignment Trajectories")

    ax.set_aspect('equal', adjustable='box')
    ax.grid(True, linestyle='--', alpha=0.3)

    ax.legend(
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        fontsize=8
    )

    out_path = os.path.join(output_dir, "all_articles_combined.png")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {out_path}")


def main(args):
    ensure_output_dir(args.output_dir)

    data = load_data(args.input_file)

    all_trajectories = {}

    for article_name, article_data in data.items():

        if "political_alignment_trajectory" not in article_data:
            continue

        trajectory = extract_trajectory(article_data)

        if trajectory is None:
            print(f"Skipping (invalid): {article_name}")
            continue

        plot_single_article(article_name, trajectory, args.output_dir)
        all_trajectories[article_name] = trajectory

    if all_trajectories:
        plot_combined(all_trajectories, args.output_dir)
    else:
        print("No valid trajectories found.")


if __name__ == "__main__":
    args = get_args()
    main(args)
