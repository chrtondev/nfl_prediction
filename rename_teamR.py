import os

# folder where your files are stored
folder = "./team_strength/scraped_csvs_2025"

prefix = "nfl_football_stats_nfl_team_"
suffix = "_teamrankings_com.csv"

for filename in os.listdir(folder):
    if filename.startswith(prefix) and filename.endswith(suffix):
        # remove prefix and suffix
        core_name = filename[len(prefix):-len(suffix)]
        new_name = f"{core_name}.csv"
        
        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)
        os.rename(old_path, new_path)
        print(f"Renamed: {filename} -> {new_name}")
