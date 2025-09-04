import pandas as pd
import math

# scaling constant (like Elo's 400)
TSS_SCALE = 150  

def tss_win_prob(tss_a, tss_b):
    """Logistic function to compute win probability from TSS difference"""
    return 1 / (1 + 10 ** (-(tss_a - tss_b) / TSS_SCALE))

# Explicit mapping from schedule/active team names → team_strength_scores.csv names
TEAM_MAP = {
    "Arizona Cardinals": "Arizona",
    "Atlanta Falcons": "Atlanta",
    "Baltimore Ravens": "Baltimore",
    "Buffalo Bills": "Buffalo",
    "Carolina Panthers": "Carolina",
    "Chicago Bears": "Chicago",
    "Cincinnati Bengals": "Cincinnati",
    "Cleveland Browns": "Cleveland",
    "Dallas Cowboys": "Dallas",
    "Denver Broncos": "Denver",
    "Detroit Lions": "Detroit",
    "Green Bay Packers": "Green Bay",
    "Houston Texans": "Houston",
    "Indianapolis Colts": "Indianapolis",
    "Jacksonville Jaguars": "Jacksonville",
    "Kansas City Chiefs": "Kansas City",
    "Las Vegas Raiders": "Las Vegas",
    "Los Angeles Chargers": "LA Chargers",
    "Los Angeles Rams": "LA Rams",
    "Miami Dolphins": "Miami",
    "Minnesota Vikings": "Minnesota",
    "New England Patriots": "New England",
    "New Orleans Saints": "New Orleans",
    "New York Giants": "NY Giants",
    "New York Jets": "NY Jets",
    "Philadelphia Eagles": "Philadelphia",
    "Pittsburgh Steelers": "Pittsburgh",
    "San Francisco 49ers": "San Francisco",
    "Seattle Seahawks": "Seattle",
    "Tampa Bay Buccaneers": "Tampa Bay",
    "Tennessee Titans": "Tennessee",
    "Washington Commanders": "Washington"
}

def get_city_name(team_name: str) -> str:
    """Map full team name to the short form used in team_strength_scores.csv"""
    return TEAM_MAP.get(team_name, team_name)

def add_tss_to_active(week, 
                      active_file="../prediction/nfl_elo_active.csv",
                      tss_file="scraped_csvs_2024/team_strength_scores.csv",
                      schedule_file="../prediction/schedule.csv",
                      output_file="../prediction/nfl_elo_active.csv"):
    # Load files
    df_active = pd.read_csv(active_file)
    df_tss = pd.read_csv(tss_file)
    df_sched = pd.read_csv(schedule_file)

    # Normalize TSS "Team"
    df_tss["Team"] = df_tss["Team"].str.strip()

    # Make sure columns exist
    for col in ["tss_win_prob", "tss_edge", "total_edge"]:
        if col not in df_active.columns:
            df_active[col] = None

    # Filter schedule to chosen week
    week_sched = df_sched[df_sched["week"] == week]
    if week_sched.empty:
        print(f"❌ No schedule found for week {week}")
        return

    # For each game in the schedule
    for _, game in week_sched.iterrows():
        home = game["home team"]
        away = game["away team"]

        city_home = get_city_name(home)
        city_away = get_city_name(away)

        try:
            tss_home = df_tss.loc[df_tss["Team"] == city_home, "TSS"].iloc[0]
            tss_away = df_tss.loc[df_tss["Team"] == city_away, "TSS"].iloc[0]
        except IndexError:
            print(f"⚠️ Missing TSS for {home} ({city_home}) or {away} ({city_away}), skipping")
            continue

        # Compute TSS win probs
        prob_home = tss_win_prob(tss_home, tss_away)
        prob_away = 1 - prob_home

        edge_home = prob_home - 0.5
        edge_away = -edge_home

        # Lookup Elo expected win from active file
        try:
            exp_home = df_active.loc[(df_active["year"] == 2025) & (df_active["week"] == week) & (df_active["team"] == home), "expected_win"].iloc[0]
            exp_away = df_active.loc[(df_active["year"] == 2025) & (df_active["week"] == week) & (df_active["team"] == away), "expected_win"].iloc[0]
        except IndexError:
            print(f"⚠️ Missing Elo expected win for {home} or {away}, skipping")
            continue

        # Compute total edge = average of Elo edge and TSS edge
        total_home = ((exp_home - 0.5) + edge_home) / 2
        total_away = ((exp_away - 0.5) + edge_away) / 2

        # Update active file rows
        df_active.loc[(df_active["year"] == 2025) & (df_active["week"] == week) & (df_active["team"] == home),
                      ["tss_win_prob", "tss_edge", "total_edge"]] = [prob_home, edge_home, total_home]
        df_active.loc[(df_active["year"] == 2025) & (df_active["week"] == week) & (df_active["team"] == away),
                      ["tss_win_prob", "tss_edge", "total_edge"]] = [prob_away, edge_away, total_away]

        print(f"{home} vs {away}: Elo ExpWin {exp_home:.1%}/{exp_away:.1%}, "
              f"TSS {prob_home:.1%}/{prob_away:.1%}, "
              f"Total Edge {total_home:+.1%}/{total_away:+.1%}")

    # Save updates
    df_active.to_csv(output_file, index=False)
    print(f"✅ Updated {output_file} with TSS + total_edge data for Week {week}")


if __name__ == "__main__":
    try:
        week = int(input("Enter week number: "))
        add_tss_to_active(week)
    except ValueError:
        print("❌ Invalid input. Please enter a week number.")
