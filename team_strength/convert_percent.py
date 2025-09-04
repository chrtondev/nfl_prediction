import pandas as pd

def convert_percentages(csv_path, output_path):
    df = pd.read_csv(csv_path)

    # Loop through all columns except Rank and Team
    for col in df.columns:
        if col not in ["Rank", "Team"]:
            # Convert percentage strings to decimals
            df[col] = df[col].replace('%','', regex=True)  # strip %
            df[col] = pd.to_numeric(df[col], errors="coerce") / 100.0

    # Save cleaned CSV
    df.to_csv(output_path, index=False)
    print(f"✅ Converted percentages and saved to {output_path}")

    return df



if __name__ == "__main__":
    # Example usage
    convert_percentages("opponent_red_zone_scoring_percentage_td_only.csv", "output.csv")
