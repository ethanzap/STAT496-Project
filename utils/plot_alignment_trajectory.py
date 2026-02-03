import json
import matplotlib.pyplot as plt
import os
import csv


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


def draw_arrows(x_vals, y_vals):
    """
    Draw directional arrows between consecutive points
    """
    for i in range(len(x_vals) - 1):
        dx = x_vals[i + 1] - x_vals[i]
        dy = y_vals[i + 1] - y_vals[i]

        plt.arrow(
            x_vals[i],
            y_vals[i],
            dx,
            dy,
            length_includes_head=True,
            head_width=0.12,
            head_length=0.15,
            alpha=0.7
        )


def plot_single_article(article_name, trajectory):
    x_vals = [p[0] for p in trajectory]
    y_vals = [p[1] for p in trajectory]

    plt.figure(figsize=(7, 7))

    plt.plot(x_vals, y_vals, marker='o')
    draw_arrows(x_vals, y_vals)

    for i, (x, y) in enumerate(zip(x_vals, y_vals)):
        plt.text(x, y, str(i), fontsize=9)

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.xlabel("Economic Axis (Left ⟵ → Right)")
    plt.ylabel("Social Axis (Libertarian ⟵ → Authoritarian)")
    plt.title(f"Political Alignment Trajectory\n{article_name}")

    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)

    safe_name = sanitize_filename(article_name)
    out_path = os.path.join(OUTPUT_DIR, f"{safe_name}.png")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"Saved: {out_path}")


def plot_combined(all_trajectories):
    plt.figure(figsize=(9, 9))

    for article_name, trajectory in all_trajectories.items():
        x_vals = [p[0] for p in trajectory]
        y_vals = [p[1] for p in trajectory]

        plt.plot(x_vals, y_vals, marker='o', alpha=0.75, label=article_name)
        draw_arrows(x_vals, y_vals)

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.xlabel("Economic Axis (Left ⟵ → Right)")
    plt.ylabel("Social Axis (Libertarian ⟵ → Authoritarian)")
    plt.title("Combined Political Alignment Trajectories")

    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)

    # Legend outside plot (prevents overlap clutter)
    plt.legend(
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
