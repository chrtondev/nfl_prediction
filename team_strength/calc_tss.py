# calc_tss.py
import pandas as pd
import os

YEAR_COL = "2024"
FOLDER = "./scraped_csvs_2024"   # folder where CSVs are stored

# =======================
# Weights
# =======================

oss_weights = {
    "third_down_conversion_percentage": 1.0,
    "yards_per_game": 0.9,
    "fourth_downs_per_game": -1.0,
    
    "passing_touchdowns_per_game": 1.1,
    "average_team_passer_rating": 1.5,
    "interceptions_thrown_per_game": -1.8,
    "qb_sacked_per_game": -0.6,
    "rushing_touchdowns_per_game": 0.5,
    
    "rushing_yards_per_game": 1.0,
    "rushing_first_downs_per_game": 0.7,
    "rushing_touchdowns_per_game_run": 1.3,
    "passing_touchdowns_per_game_run": 0.5,
}

dss_weights = {
    "qb_sacked_per_game": 0.95,
    "opponent_interceptions_thrown_per_game": 1.3,
    "opponent_fumbles_per_game": 1.0,
    "takeaways_bonus": 0.5,

    "opponent_touchdowns_per_game": -1.6,
    "opponent_yards_per_game": -1.1,
    "opponent_red_zone_scoring_percentage_td_only": -1.4,
    "opponent_fourth_downs_per_game": 0.6,
}

# =======================
# Helper: Load & Merge CSVs
# =======================

def load_csvs(file_list, folder=FOLDER):
    dfs = []
    for file in file_list:
        path = os.path.join(folder, file)
        df = pd.read_csv(path)
        stat_name = os.path.splitext(file)[0]
        df = df[["Team", YEAR_COL]].rename(columns={YEAR_COL: stat_name})
        dfs.append(df)
    data = dfs[0]
    for df in dfs[1:]:
        data = data.merge(df, on="Team")
    return data

def normalize(df):
    for col in df.columns:
        if col != "Team":
            mean = df[col].mean()
            std = df[col].std()
            df[col + "_norm"] = (df[col] - mean) / std
    return df

# =======================
# Offensive Strength Score
# =======================

def calc_oss(data):
    oss_scores = []
    for _, row in data.iterrows():
        team = row["Team"]

        # Identity proxy (no attempts CSVs available)
        pass_bias_indicator = row["passing_touchdowns_per_game"]
        run_bias_indicator = row["rushing_yards_per_game"]
        identity_ratio = (pass_bias_indicator + 1) / (run_bias_indicator + 1)

        baseline = (
            oss_weights["third_down_conversion_percentage"] * row["third_down_conversion_percentage_norm"] +
            oss_weights["yards_per_game"] * row["yards_per_game_norm"] +
            oss_weights["fourth_downs_per_game"] * row["fourth_downs_per_game_norm"]
        )

        if identity_ratio > 1.2:  # pass-leaning
            production = (
                oss_weights["passing_touchdowns_per_game"] * row["passing_touchdowns_per_game_norm"] +
                oss_weights["average_team_passer_rating"] * row["average_team_passer_rating_norm"] +
                oss_weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"] +
                oss_weights["qb_sacked_per_game"] * row["qb_sacked_per_game_norm"] +
                oss_weights["rushing_touchdowns_per_game"] * row["rushing_touchdowns_per_game_norm"]
            )
        elif identity_ratio < 0.8:  # run-leaning
            production = (
                oss_weights["rushing_yards_per_game"] * row["rushing_yards_per_game_norm"] +
                oss_weights["rushing_first_downs_per_game"] * row["rushing_first_downs_per_game_norm"] +
                oss_weights["rushing_touchdowns_per_game_run"] * row["rushing_touchdowns_per_game_norm"] +
                oss_weights["passing_touchdowns_per_game_run"] * row["passing_touchdowns_per_game_norm"] +
                oss_weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"]
            )
        else:  # balanced
            prod_pass = (
                oss_weights["passing_touchdowns_per_game"] * row["passing_touchdowns_per_game_norm"] +
                oss_weights["average_team_passer_rating"] * row["average_team_passer_rating_norm"] +
                oss_weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"] +
                oss_weights["qb_sacked_per_game"] * row["qb_sacked_per_game_norm"] +
                oss_weights["rushing_touchdowns_per_game"] * row["rushing_touchdowns_per_game_norm"]
            )
            prod_run = (
                oss_weights["rushing_yards_per_game"] * row["rushing_yards_per_game_norm"] +
                oss_weights["rushing_first_downs_per_game"] * row["rushing_first_downs_per_game_norm"] +
                oss_weights["rushing_touchdowns_per_game_run"] * row["rushing_touchdowns_per_game_norm"] +
                oss_weights["passing_touchdowns_per_game_run"] * row["passing_touchdowns_per_game_norm"] +
                oss_weights["interceptions_thrown_per_game"] * row["interceptions_thrown_per_game_norm"]
            )
            production = 0.5 * (prod_pass + prod_run)

        raw_oss = baseline + production
        oss_scores.append((team, raw_oss))

    return pd.DataFrame(oss_scores, columns=["Team", "RawOSS"])

# =======================
# Defensive Strength Score
# =======================

def calc_dss(data):
    dss_scores = []
    for _, row in data.iterrows():
        team = row["Team"]

        disruption = (
            dss_weights["qb_sacked_per_game"] * row["qb_sacked_per_game_norm"] +
            dss_weights["opponent_interceptions_thrown_per_game"] * row["opponent_interceptions_thrown_per_game_norm"] +
            dss_weights["opponent_fumbles_per_game"] * row["opponent_fumbles_per_game_norm"]
        )
        disruption += dss_weights["takeaways_bonus"] * (
            row["opponent_interceptions_thrown_per_game_norm"] + row["opponent_fumbles_per_game_norm"]
        ) / 2

        resilience = (
            dss_weights["opponent_touchdowns_per_game"] * row["opponent_touchdowns_per_game_norm"] +
            dss_weights["opponent_yards_per_game"] * row["opponent_yards_per_game_norm"] +
            dss_weights["opponent_red_zone_scoring_percentage_td_only"] * row["opponent_red_zone_scoring_percentage_td_only_norm"] +
            dss_weights["opponent_fourth_downs_per_game"] * row["opponent_fourth_downs_per_game_norm"]
        )

        raw_dss = disruption + resilience
        dss_scores.append((team, disruption, resilience, raw_dss))

    return pd.DataFrame(dss_scores, columns=["Team", "Disruption", "Resilience", "RawDSS"])

# =======================
# Main Runner
# =======================

def main():
    # Offensive files
    oss_files = [
        "average_team_passer_rating.csv",
        "rushing_yards_per_game.csv",
        "fourth_downs_per_game.csv",
        "qb_sacked_per_game.csv",
        "third_down_conversion_percentage.csv",
        "interceptions_thrown_per_game.csv",
        "rushing_first_downs_per_game.csv",
        "yards_per_game.csv",
        "passing_touchdowns_per_game.csv",
        "rushing_touchdowns_per_game.csv"
    ]
    oss_data = load_csvs(oss_files, folder=FOLDER)
    oss_data = normalize(oss_data)
    oss_df = calc_oss(oss_data)

    # Defensive files
    dss_files = [
        "qb_sacked_per_game.csv",
        "opponent_interceptions_thrown_per_game.csv",
        "opponent_fumbles_per_game.csv",
        "opponent_touchdowns_per_game.csv",
        "opponent_yards_per_game.csv",
        "opponent_red_zone_scoring_percentage_td_only.csv",
        "opponent_fourth_downs_per_game.csv"
    ]
    dss_data = load_csvs(dss_files, folder=FOLDER)
    dss_data = normalize(dss_data)
    dss_df = calc_dss(dss_data)

    # Merge OSS + DSS
    merged = oss_df.merge(dss_df, on="Team")
    merged["TSS"] = merged["RawOSS"] + merged["RawDSS"]

    # Save results
    out_path = os.path.join(FOLDER, "team_strength_scores.csv")
    merged.to_csv(out_path, index=False)
    print(f"✅ Results saved to {out_path}")
    print(merged.sort_values("TSS", ascending=False).to_string(index=False))

if __name__ == "__main__":
    main()
