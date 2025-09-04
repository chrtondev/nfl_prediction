import pandas as pd
import os

# === CONFIG ===
year_col = "2024"

# Finalized Weights
weights = {
    "qb_sacked_per_game": 0.95,
    "opponent_interceptions_thrown_per_game": 1.3,
    "opponent_fumbles_per_game": 1.0,
    "takeaways_bonus": 0.5,  # we'll approximate as combo of INT + Fumbles
    
    "opponent_touchdowns_per_game": -1.6,
    "opponent_yards_per_game": -1.1,
    "opponent_red_zone_scoring_percentage_td_only": -1.4,
    "opponent_fourth_downs_per_game": 0.6
}

# === LOAD CSVs ===
folder = "./scraped_csvs_2024"
csv_files = [
    "qb_sacked_per_game.csv",
    "opponent_interceptions_thrown_per_game.csv",
    "opponent_fumbles_per_game.csv",
    "opponent_touchdowns_per_game.csv",
    "opponent_yards_per_game.csv",
    "opponent_red_zone_scoring_percentage_td_only.csv",
    "opponent_fourth_downs_per_game.csv"
]

dfs = []
for file in csv_files:
    df = pd.read_csv(os.path.join(folder, file))
    stat_name = os.path.splitext(file)[0]
    df = df[["Team", year_col]].rename(columns={year_col: stat_name})
    dfs.append(df)

# Merge on Team
data = dfs[0]
for df in dfs[1:]:
    data = data.merge(df, on="Team")

# === NORMALIZE EACH STAT (Z-score) ===
for col in data.columns:
    if col != "Team":
        mean = data[col].mean()
        std = data[col].std()
        data[col + "_norm"] = (data[col] - mean) / std

# === CALCULATE RAW DSS ===
dss_scores = []

for _, row in data.iterrows():
    team = row["Team"]

    # X-Factor (disruption)
    disruption = (
        weights["qb_sacked_per_game"] * row["qb_sacked_per_game_norm"] +
        weights["opponent_interceptions_thrown_per_game"] * row["opponent_interceptions_thrown_per_game_norm"] +
        weights["opponent_fumbles_per_game"] * row["opponent_fumbles_per_game_norm"]
    )
    
    # Small bonus for overall ball disruption (approx using INT + Fumbles together)
    disruption += weights["takeaways_bonus"] * (
        row["opponent_interceptions_thrown_per_game_norm"] + row["opponent_fumbles_per_game_norm"]
    ) / 2

    # Resilience (prevent points/yards)
    resilience = (
        weights["opponent_touchdowns_per_game"] * row["opponent_touchdowns_per_game_norm"] +
        weights["opponent_yards_per_game"] * row["opponent_yards_per_game_norm"] +
        weights["opponent_red_zone_scoring_percentage_td_only"] * row["opponent_red_zone_scoring_percentage_td_only_norm"] +
        weights["opponent_fourth_downs_per_game"] * row["opponent_fourth_downs_per_game_norm"]
    )

    raw_dss = disruption + resilience
    dss_scores.append((team, disruption, resilience, raw_dss))

# Final dataframe
dss_df = pd.DataFrame(dss_scores, columns=["Team", "Disruption", "Resilience", "RawDSS"]).sort_values("RawDSS", ascending=False)

print(dss_df.to_string(index=False))
