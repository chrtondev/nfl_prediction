import pandas as pd
import os

# Parameters
HISTORY_FILE = "../nfl_elo_history_2018_2024.csv"
SCHEDULE_FILE = "schedule.csv"
ACTIVE_FILE = "nfl_elo_active.csv"
HOME_FIELD_ADV = 65

# Expected score function
def expected_score(rating_a, rating_b, home_adv=0, is_home=True):
    if is_home:
        ra = rating_a + home_adv
        rb = rating_b
    else:
        ra = rating_a
        rb = rating_b + home_adv
    return 1 / (1 + 10 ** ((rb - ra) / 400))


def init_active_file():
    """Initialize nfl_elo_active.csv with 2024 regression values."""
    df_hist = pd.read_csv(HISTORY_FILE)
    last_year = df_hist["year"].max()
    regressions = df_hist[(df_hist["year"] == last_year) & (df_hist["type"] == "regression")]

    if regressions.empty:
        raise ValueError(f"No regression found for {last_year} in {HISTORY_FILE}")

    rows = []
    for _, row in regressions.iterrows():
        rows.append({
            "year": 2025,
            "week": 0,
            "team": row["team"],
            "elo_before": row["elo_after"],
            "elo_after": None,     # nothing updated yet
            "expected_win": None,
            "type": "regression_start",
            "result": None
        })
    df_active = pd.DataFrame(rows)
    df_active.to_csv(ACTIVE_FILE, index=False)
    print(f"✅ Initialized {ACTIVE_FILE} with 2025 baselines from {last_year} regression")


def get_current_elos():
    """Load latest Elo ratings for each team from active file.
       Prefer elo_after if available, otherwise fallback to elo_before."""
    df_active = pd.read_csv(ACTIVE_FILE)

    # Get each team's most recent row
    latest = df_active.sort_values(by=["year", "week"]).groupby("team").tail(1)

    # Prefer elo_after if it's not NaN, else fallback to elo_before
    latest["current_elo"] = latest["elo_after"].combine_first(latest["elo_before"])

    return dict(zip(latest["team"], latest["current_elo"]))


def predict_week(week: int):
    """Predict all games in a given week and append to active file."""
    if not os.path.exists(ACTIVE_FILE):
        init_active_file()

    current_elos = get_current_elos()
    df_sched = pd.read_csv(SCHEDULE_FILE)
    week_games = df_sched[df_sched["week"] == week]

    if week_games.empty:
        print(f"No games found for Week {week} in {SCHEDULE_FILE}")
        return

    df_active = pd.read_csv(ACTIVE_FILE)

    print(f"\n📅 Week {week} Predictions\n{'-'*50}")
    rows = []
    for _, game in week_games.iterrows():
        home = game["home team"]
        away = game["away team"]

        if home not in current_elos or away not in current_elos:
            print(f"Skipping {home} vs {away} (missing Elo)")
            continue

        r_home = current_elos[home]
        r_away = current_elos[away]

        exp_home = expected_score(r_home, r_away, HOME_FIELD_ADV, True)
        exp_away = 1 - exp_home

        print(f"{home} ({r_home:.1f}) vs {away} ({r_away:.1f})")
        print(f"   {home} win chance: {exp_home*100:.2f}%")
        print(f"   {away} win chance: {exp_away*100:.2f}%\n")

        rows.append({
            "year": 2025,
            "week": week,
            "team": home,
            "elo_before": r_home,
            "elo_after": None,  # left blank until update.py processes result
            "expected_win": exp_home,
            "type": "prediction",
            "result": None
        })
        rows.append({
            "year": 2025,
            "week": week,
            "team": away,
            "elo_before": r_away,
            "elo_after": None,
            "expected_win": exp_away,
            "type": "prediction",
            "result": None
        })

    if rows:
        df_new = pd.DataFrame(rows)
        df_active = pd.concat([df_active, df_new], ignore_index=True)
        df_active.to_csv(ACTIVE_FILE, index=False)
        print(f"✅ Predictions for Week {week} saved to {ACTIVE_FILE}")


if __name__ == "__main__":
    try:
        week = int(input("Enter week number (1-18): "))
        predict_week(week)
    except ValueError:
        print("❌ Invalid input. Please enter a number between 1 and 18.")
