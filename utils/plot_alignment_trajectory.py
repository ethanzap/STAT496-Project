import json
import matplotlib.pyplot as plt
import os


INPUT_FILE = "output.json"
OUTPUT_DIR = "plots"


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


def plot_single_article(article_name, trajectory):
    x_vals = [p[0] for p in trajectory]
    y_vals = [p[1] for p in trajectory]

    plt.figure(figsize=(7, 7))

    plt.plot(x_vals, y_vals, marker='o')

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
    plt.figure(figsize=(8, 8))

    for article_name, trajectory in all_trajectories.items():
        x_vals = [p[0] for p in trajectory]
        y_vals = [p[1] for p in trajectory]

        plt.plot(x_vals, y_vals, marker='o', alpha=0.7)

    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    plt.xlabel("Economic Axis (Left ⟵ → Right)")
    plt.ylabel("Social Axis (Libertarian ⟵ → Authoritarian)")
    plt.title("Combined Political Alignment Trajectories")

    plt.gca().set_aspect('equal', adjustable='box')
    plt.grid(True)

    out_path = os.path.join(OUTPUT_DIR, "all_articles_combined.png")

    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close()

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
    else:
        print("No valid trajectories found.")


if __name__ == "__main__":
    main()
