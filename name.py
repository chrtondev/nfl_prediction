import pandas as pd

def normalize_team_names(csv_path="master_nfl_2000_2016.csv",
                         output_path="master_nfl_2000_2016_fixed.csv"): # note that this is doing the year 2000 - 2016 
    df = pd.read_csv(csv_path)

    # Mapping of old names to new names
    replacements = {
        "Washington Football Team": "Washington Commanders",
        "Washington Redskins": "Washington Commanders",
        "Oakland Raiders": "Las Vegas Raiders"
    }

    # Apply replacements to relevant columns
    for col in ["home-team", "away-team", "winner"]:
        df[col] = df[col].replace(replacements)

    df.to_csv(output_path, index=False)
    print(f"Saved fixed CSV to {output_path}")

if __name__ == "__main__":
    normalize_team_names()
