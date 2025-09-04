import pandas as pd
import os

# === CONFIG ===
year_col = "2024"

# Weights (finalized earlier)
weights = {
    "third_down_conversion_percentage": 1.0,
    "yards_per_game": 0.9,
    "fourth_downs_per_game": -1.0,
    
    "passing_touchdowns_per_game": 1.1,
    "average_team_passer_rating": 1.5,
    "interceptions_thrown_per_game": -1.8,
    "qb_sacked_per_game": -0.6,
    "rushing_touchdowns_per_game": 0.5,   # support in pass-heavy
    
    "rushing_yards_per_game": 1.0,
    "rushing_first_downs_per_game": 0.7,
    "rushing_touchdowns_per_game_run": 1.3, # run-heavy emphasis
    "passing_touchdowns_per_game_run": 0.5, # support in run-heavy
}

# Identity thresholds
RUN_HEAVY = 0.67
RUN_BIAS = 0.8
PASS_BIAS = 1.2
PASS_HEAVY = 1.5

# === LOAD CSVs ===
folder = "./scraped_csvs_2024"
csv_files = [
    # offensive csvs
    "average_team_passer_rating.csv",
    "points_per_game.csv",  # not used 
    "rushing_yards_per_game.csv",
    "fourth_downs_per_game.csv",
    "qb_sacked_per_game.csv",
    "third_down_conversion_percentage.csv",
    "interceptions_thrown_per_game.csv",
    "rushing_first_downs_per_game.csv",
    "yards_per_game.csv",
    "passing_touchdowns_per_game.csv",
    "rushing_touchdowns_per_game.csv",
]

dfs = []
for file in csv_files:
    df = pd.read_csv(os.path.join(folder, file))
    stat_name = os.path.splitext(file)[0]
    df = df[["Team", year_col]].rename(columns={year_col: stat_name})
    dfs.append(df)

# Merge all stats on Team
data = dfs[0]
for df in dfs[1:]:
    data = data.merge(df, on="Team")

# === NORMALIZE EACH STAT (Z-score) ===
for col in data.columns:
    if col != "Team":
        mean = data[col].mean()
        std = data[col].std()
        data[col + "_norm"] = (data[col] - mean) / std

# === CALCULATE RAW OSS ===
oss_scores = []

for _, row in data.iterrows():
    team = row["Team"]
    
    # Identity (approx since pass/rush attempts not provided)
    pass_bias_indicator = row["passing_touchdowns_per_game"]
    run_bias_indicator = row["rushing_yards_per_game"]
    identity_ratio = (pass_bias_indicator + 1) / (run_bias_indicator + 1)
    
    # Baseline
    baseline = (
        weights["third_down_conversion_percentage"] * row["third_down_conversion_percentage_norm"] +
        weights["yards_per_game"] * row["yards_per_game_norm"] +
        weights["fourth_downs_per_game"] * row["fourth_downs_per_game_norm"]
    )
    
    # Production based on identity
    if identity_ratio > PASS_BIAS:  # Pass leaning
        production = (
            weights["passing_touchdowns_per_game"] * row["passing_touchdowns_per_game_norm"] +
            weights["average_team_passer_rating"] * row["average_team_passer_rating_norm"] +
            weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"] +
            weights["qb_sacked_per_game"] * row["qb_sacked_per_game_norm"] +
            weights["rushing_touchdowns_per_game"] * row["rushing_touchdowns_per_game_norm"]
        )
    elif identity_ratio < RUN_BIAS:  # Run leaning
        production = (
            weights["rushing_yards_per_game"] * row["rushing_yards_per_game_norm"] +
            weights["rushing_first_downs_per_game"] * row["rushing_first_downs_per_game_norm"] +
            weights["rushing_touchdowns_per_game_run"] * row["rushing_touchdowns_per_game_norm"] +
            weights["passing_touchdowns_per_game_run"] * row["passing_touchdowns_per_game_norm"] +
            weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"]
        )
    else:  # Balanced
        prod_pass = (
            weights["passing_touchdowns_per_game"] * row["passing_touchdowns_per_game_norm"] +
            weights["average_team_passer_rating"] * row["average_team_passer_rating_norm"] +
            weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"] +
            weights["qb_sacked_per_game"] * row["qb_sacked_per_game_norm"] +
            weights["rushing_touchdowns_per_game"] * row["rushing_touchdowns_per_game_norm"]
        )
        prod_run = (
            weights["rushing_yards_per_game"] * row["rushing_yards_per_game_norm"] +
            weights["rushing_first_downs_per_game"] * row["rushing_first_downs_per_game_norm"] +
            weights["rushing_touchdowns_per_game_run"] * row["rushing_touchdowns_per_game_norm"] +
            weights["passing_touchdowns_per_game_run"] * row["passing_touchdowns_per_game_norm"] +
            weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"]
        )
        production = 0.5 * (prod_pass + prod_run)
    
    raw_oss = baseline + production
    oss_scores.append((team, raw_oss))

# Final dataframe
oss_df = pd.DataFrame(oss_scores, columns=["Team", "RawOSS"]).sort_values("RawOSS", ascending=False)

print(oss_df.to_string(index=False))
