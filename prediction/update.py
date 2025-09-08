import pandas as pd
import requests
from bs4 import BeautifulSoup
from io import StringIO
import time

# Parameters
ACTIVE_FILE = "nfl_elo_active.csv"
HOME_FIELD_ADV = 65

# === Elo functions ===
def expected_score(rating_a, rating_b, home_adv=0, is_home=True):
    if is_home:
        ra = rating_a + home_adv
        rb = rating_b
    else:
        ra = rating_a
        rb = rating_b + home_adv
    return 1 / (1 + 10 ** ((rb - ra) / 400))


def score_multiplier(score_diff, alpha=0.3, cap=1.75):
    n_scores = min(score_diff / 7, 3.5)
    if n_scores < 1:
        n_scores = 1
    return min(1 + alpha * (n_scores - 1), cap)


def surprise_factor(expected, cap=3.0):
    val = 2.2 / (0.001 + (expected * (1 - expected)))
    return min(val, cap)


def update_elo(rating_a, rating_b, score_a, score_b, is_home_a, k_factor=20):
    exp_a = expected_score(rating_a, rating_b, HOME_FIELD_ADV, is_home_a)

    if score_a > score_b:
        s_a, s_b = 1, 0
    elif score_a < score_b:
        s_a, s_b = 0, 1
    else:
        s_a, s_b = 0.5, 0.5

    diff = abs(score_a - score_b)
    mult = score_multiplier(diff)
    adj = surprise_factor(exp_a)

    change_a = k_factor * mult * adj * (s_a - exp_a)
    if abs(change_a) > 50:  # cap swings
        change_a = max(min(change_a, 50), -50)
    change_b = -change_a

    return rating_a + change_a, rating_b + change_b, exp_a


# === Scrape results from PFR ===
def scrape_week_results(year, week):
    url = f"https://www.pro-football-reference.com/years/{year}/week_{week}.htm"
    print(f"Scraping results for Week {week}...")
    resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    game_blocks = soup.find_all("div", class_="game_summaries")
    results = []

    for block in game_blocks:
        tables = [t for t in block.find_all("table") if "stats" not in t.get("class", [])]
    for table in tables:
        df = pd.read_html(StringIO(str(table)))[0]

        date = df.iloc[0, 0]
        away_team = df.iloc[1, 0]
        home_team = df.iloc[2, 0]

        # Safely parse scores
        try:
            away_score = int(df.iloc[1, 1])
            home_score = int(df.iloc[2, 1])
        except (ValueError, TypeError):
            print(f"⚠️ Skipping {away_team} at {home_team} — no final score yet.")
            continue

        results.append((home_team, home_score, away_team, away_score, date))
        time.sleep(2)
        
    return results


def update_week(year=2025, week=1):
    df_active = pd.read_csv(ACTIVE_FILE)
    results = scrape_week_results(year, week)
    rows = []

    for home, hs, away, as_, date in results:
        # Check if already updated
        already_done = df_active[
            (df_active["year"] == year) &
            (df_active["week"] == week) &
            (df_active["team"] == home) &
            (df_active["type"] == "game")
        ]
        if not already_done.empty:
            print(f"Skipping {home} vs {away}, already updated.")
            continue

        # Get latest Elo before this game
        latest_home = df_active[df_active["team"] == home].sort_values(by=["year", "week"]).iloc[-1]["elo_before"]
        latest_away = df_active[df_active["team"] == away].sort_values(by=["year", "week"]).iloc[-1]["elo_before"]

        # Update Elo
        new_home, new_away, exp_home = update_elo(latest_home, latest_away, hs, as_, True)

        # Record results
        rows.append({
            "year": year, "week": week, "team": home,
            "elo_before": latest_home, "elo_after": new_home,
            "expected_win": exp_home,
            "type": "game", "result": "W" if hs > as_ else ("L" if hs < as_ else "T")
        })
        rows.append({
            "year": year, "week": week, "team": away,
            "elo_before": latest_away, "elo_after": new_away,
            "expected_win": 1 - exp_home,
            "type": "game", "result": "W" if as_ > hs else ("L" if as_ < hs else "T")
        })

        print(f"{home} {hs} - {as_} {away} | New Elo: {home} {new_home:.1f}, {away} {new_away:.1f}")

    if rows:
        df_new = pd.DataFrame(rows)
        df_active = pd.concat([df_active, df_new], ignore_index=True)
        df_active.to_csv(ACTIVE_FILE, index=False)
        print(f"✅ Week {week} results saved to {ACTIVE_FILE}")


if __name__ == "__main__":
    try:
        week = int(input("Enter week number to update: "))
    except ValueError:
        print("❌ Invalid input. Please enter a valid week number.")
    else:
        update_week(2025, week)

