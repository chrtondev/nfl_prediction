import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_matchup_diff(csv_path="matchup_elo_diff_2018_2024.csv", output_dir="diff_plots"):
    df = pd.read_csv(csv_path)

    # Ensure sorted order
    df = df.sort_values(by=["team", "year"])

    os.makedirs(output_dir, exist_ok=True)

    for team in df["team"].unique():
        team_df = df[df["team"] == team]

        plt.figure(figsize=(10, 5))
        plt.plot(team_df["year"], team_df["avg_matchup_diff"], marker="o", label=team, color="blue")

        # Add horizontal reference line at -4.8
        plt.axhline(y=-4.8, color="red", linestyle="--", alpha=0.7, label="Ref: -4.8")

        plt.title(f"Avg Matchup Elo Difference: {team} (2018–2024)")
        plt.xlabel("Year")
        plt.ylabel("Avg Matchup Elo Difference")
        plt.grid(alpha=0.3, linestyle="--")
        plt.legend()

        # Save plot
        out_path = os.path.join(output_dir, f"{team.replace(' ', '_')}_diff.png")
        plt.tight_layout()
        plt.savefig(out_path, dpi=300)
        plt.close()

    print(f"✅ Saved matchup diff plots for all teams to {output_dir}/")


if __name__ == "__main__":
    plot_matchup_diff()
