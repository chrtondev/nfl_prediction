import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_elo_trends(csv_file, output_dir="elo_charts"):
    """
    For each team, plot Elo trend over the season (Week 0 onward).
    Also generates a collective chart of all teams.
    """
    # Load CSV
    df = pd.read_csv(csv_file)

    # Ensure Elo values: use elo_before for Week 0, then elo_after otherwise
    df['elo'] = df['elo_after'].fillna(df['elo_before'])

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Individual team plots
    for team, group in df.groupby("team"):
        plt.figure(figsize=(8, 5))
        plt.plot(group['week'], group['elo'], marker="o", label=team)
        plt.title(f"{team} Elo Change Over Season")
        plt.xlabel("Week")
        plt.ylabel("Elo")
        plt.grid(True, linestyle="--", alpha=0.6)
        plt.legend()
        fname = f"{team.replace(' ', '_').lower()}_ec.png"
        plt.savefig(os.path.join(output_dir, fname), bbox_inches="tight")
        plt.close()

    # Collective plot
    plt.figure(figsize=(12, 8))
    for team, group in df.groupby("team"):
        plt.plot(group['week'], group['elo'], label=team, alpha=0.7)
    plt.title("All Teams Elo Change Over Season")
    plt.xlabel("Week")
    plt.ylabel("Elo")
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize="small")
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "all_teams_ec.png"))
    plt.close()

if __name__ == "__main__":
    # Example usage
    plot_elo_trends("../prediction/nfl_elo_active.csv")
