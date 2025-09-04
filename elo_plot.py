import pandas as pd
import matplotlib.pyplot as plt
import os

def plot_team_elo(df, team_name, output_dir="team_elo_plots_2018_2024"): # change dir name here 
    team_df = df[df["team"] == team_name].copy()
    team_df = team_df.sort_values(by=["year", "week", "id"])

    min_year = df["year"].min()
    team_df["season_week"] = (team_df["year"] - min_year) * 23 + team_df["week"].astype(str).astype(int, errors="ignore")

    plt.figure(figsize=(14, 6))
    plt.plot(team_df["season_week"], team_df["elo_after"], color="blue", linewidth=2, label=team_name)

    # Mark regression points
    regressions = team_df[team_df["type"] == "regression"]
    plt.scatter(regressions["season_week"], regressions["elo_after"],
                color="red", s=40, zorder=5, label="Regression")

    # Add vertical season separators
    for year in sorted(team_df["year"].unique()):
        x = (year - min_year) * 23 + 1
        plt.axvline(x=x, color="gray", linestyle="--", alpha=0.5)
        plt.text(x, team_df["elo_after"].min() - 20, str(year), rotation=90,
                 va="bottom", ha="right", fontsize=8)

    # Add horizontal reference line at 1502
    plt.axhline(y=1502, color="red", linestyle="--", alpha=0.5, label="1502 Reference")

    plt.title(f"Elo Rating History: {team_name} ({df['year'].min()}–{df['year'].max()})")
    plt.xlabel("Timeline (season weeks)")
    plt.ylabel("Elo Rating")
    plt.ylim(1000, 2000)
    plt.grid(alpha=0.3, linestyle="--")
    plt.legend()

    plt.tight_layout()
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f"{team_name.replace(' ', '_')}_elo.png"), dpi=300)
    plt.close()


def plot_all_teams(csv_path="nfl_elo_history_2018_2024.csv", output_dir="team_elo_plots_2018_2024"): # change the dir name and file (csv) that is needed to do the years
    df = pd.read_csv(csv_path)

    for team in df["team"].unique():
        print(f"Generating plot for {team}...")
        plot_team_elo(df, team, output_dir=output_dir)

    print(f"Saved all team Elo plots to {output_dir}/")


if __name__ == "__main__":
    plot_all_teams()
