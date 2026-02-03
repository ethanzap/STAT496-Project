import json
import matplotlib.pyplot as plt


INPUT_FILE = "output.json"


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def plot_article_trajectory(article_name, trajectory):
    """
    trajectory: list of [x, y] points in chronological order
    """

    # Separate coordinates
    x_vals = [point[0] for point in trajectory]
    y_vals = [point[1] for point in trajectory]

    plt.figure(figsize=(7, 7))

    # Plot path
    plt.plot(x_vals, y_vals, marker='o')

    # Label each stage
    for i, (x, y) in enumerate(zip(x_vals, y_vals)):
        plt.text(x, y, f"{i}", fontsize=9, ha='right', va='bottom')

    # Axis labels
    plt.xlabel("Economic Axis (Left  ⟵  →  Right)")
    plt.ylabel("Social Axis (Libertarian  ⟵  →  Authoritarian)")

    # Reference lines at origin
    plt.axhline(0, linewidth=0.8)
    plt.axvline(0, linewidth=0.8)

    # Title
    plt.title(f"Political Alignment Trajectory\n{article_name}")

    # Equal scaling for political compass style
    plt.gca().set_aspect('equal', adjustable='box')

    # Grid for readability
    plt.grid(True)

    plt.show()


def main():
    data = load_data(INPUT_FILE)

    for article_name, article_data in data.items():

        if "political_alignment_trajectory" not in article_data:
            print(f"Skipping {article_name} (no trajectory found)")
            continue

        raw_traj = article_data["political_alignment_trajectory"]

        if not isinstance(raw_traj, dict):
            print(f"Invalid trajectory format for {article_name}")
            continue
        
        # Sort by chronological key and filter nulls
        trajectory = []
        
        for k in sorted(raw_traj.keys(), key=int):
            point = raw_traj[k]
            if point is not None and len(point) == 2:
                trajectory.append(point)
        
        if len(trajectory) < 2:
            print(f"Not enough valid points for {article_name}")
            continue


        print(f"Plotting: {article_name}")
        plot_article_trajectory(article_name, trajectory)


if __name__ == "__main__":
    main()
