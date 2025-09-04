import pandas as pd

def generate_elo_summaries(csv_path="nfl_elo_history_2018_2024.csv"): # input
    df = pd.read_csv(csv_path)

    # Only consider actual games
    games = df[df["type"] == "game"].copy()

    # 1. Matchup Elo Differences
    diffs = []
    for _, row in games.iterrows():
        year, team, elo, game_id = row["year"], row["team"], row["elo_after"], row["id"]

        # opponent Elo = same game_id, different team
        opp_rows = games[(games["id"] == game_id) & (games["team"] != team)]
        if not opp_rows.empty:
            opp_elo = opp_rows["elo_after"].values[0]

            # Signed difference (positive = stronger than opponent, negative = weaker)
            diff = elo - opp_elo
            diffs.append((year, team, diff))

    matchup_df = pd.DataFrame(diffs, columns=["year", "team", "elo_diff"])
    matchup_summary = matchup_df.groupby(["year", "team"])["elo_diff"].mean().reset_index()
    matchup_summary.rename(columns={"elo_diff": "avg_matchup_diff"}, inplace=True)

    matchup_summary.to_csv("matchup_elo_diff_2018_2024.csv", index=False) # output 1


    # 2. Team Elo Profiles
    team_summary = (
        games.groupby(["year", "team"])["elo_after"]
        .agg(avg_elo="mean", max_elo="max", min_elo="min")
        .reset_index()
    )
    team_summary.to_csv("team_elo_profiles_2018_2024.csv", index=False) # output 2

if __name__ == "__main__":
    generate_elo_summaries()
