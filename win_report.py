import pandas as pd
import matplotlib.pyplot as plt
import os

def team_expected_win_percentages(csv_path="nfl_elo_history_2018_2024.csv", output_dir="expected_win_reports"):
    df = pd.read_csv(csv_path)

    # Only consider game rows
    games = df[df["type"] == "game"].copy()

    # 1. Overall expected win % per team + games played
    overall = (
        games.groupby("team")
        .agg(overall_expected_win_pct=("expected_win", "mean"),
             games_played=("expected_win", "count"))
        .reset_index()
    )

    # 2. Year-by-year expected win % per team + games played
    yearly = (
        games.groupby(["year", "team"])
        .agg(yearly_expected_win_pct=("expected_win", "mean"),
             games_played=("expected_win", "count"))
        .reset_index()
    )

    # 3. League-wide yearly averages
    league_avg = (
        games.groupby("year")["expected_win"]
        .mean()
        .reset_index()
        .rename(columns={"expected_win": "league_avg_expected_win_pct"})
    )

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    overall.to_csv(os.path.join(output_dir, "team_overall_expected_win_pct.csv"), index=False)
    yearly.to_csv(os.path.join(output_dir, "team_yearly_expected_win_pct.csv"), index=False)
    league_avg.to_csv(os.path.join(output_dir, "league_yearly_expected_win_pct.csv"), index=False)

    print(f"✅ Saved outputs to {output_dir}/")

    # === Visualization: one graph per team ===
    team_dir = os.path.join(output_dir, "team_plots")
    os.makedirs(team_dir, exist_ok=True)

    for team in yearly["team"].unique():
        team_df = yearly[yearly["team"] == team]

        plt.figure(figsize=(8, 5))
        # Team line
        plt.plot(team_df["year"], team_df["yearly_expected_win_pct"],
                 marker="o", linewidth=2, color="blue", label=team)

        # League average line
        plt.plot(league_avg["year"], league_avg["league_avg_expected_win_pct"],
                 linestyle="--", color="gray", linewidth=2, label="League Avg")

        plt.title(f"{team} – Yearly Expected Win % (2018–2024)")
        plt.xlabel("Year")
        plt.ylabel("Expected Win %")
        plt.ylim(0.2, 0.8)
        plt.grid(alpha=0.3, linestyle="--")

        # Annotate games played
        for _, row in team_df.iterrows():
            plt.text(row["year"], row["yearly_expected_win_pct"] + 0.01, f"{int(row['games_played'])} gp",
                     ha="center", fontsize=8, color="gray")

        plt.legend()
        plt.tight_layout()
        plt.savefig(os.path.join(team_dir, f"{team.replace(' ', '_')}_expected_win_pct.png"), dpi=300)
        plt.close()

    print(f"📊 Saved individual team plots to {team_dir}/")

    return overall, yearly, league_avg

if __name__ == "__main__":
    overall, yearly, league_avg = team_expected_win_percentages()
    print("\n--- Overall Expected Win % (sample) ---")
    print(overall.head())
    print("\n--- Yearly Expected Win % (sample) ---")
    print(yearly.head())
    print("\n--- League Avg Expected Win % (sample) ---")
    print(league_avg.head())
