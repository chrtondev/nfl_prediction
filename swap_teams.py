import pandas as pd

df = pd.read_csv("master_nfl_2018_2024_fixed.csv")

# Swap team columns
df["home-team"], df["away-team"] = df["away-team"], df["home-team"]

# Swap score columns
df["home-score"], df["away-score"] = df["away-score"], df["home-score"]

# Save fixed version
df.to_csv("master_nfl_2018_2024_fixed_2.csv", index=False)
print("✅ Saved fixed CSV: master_nfl_2018_2024_fixed_2.csv")
