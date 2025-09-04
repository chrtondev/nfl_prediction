import pandas as pd
import math

# Parameters
INITIAL_ELO = 1500
HOME_FIELD_ADV = 65
ALPHA = 0.3  # scaling factor for number-of-scores multiplier

# K-factors by week
def get_k_factor(week: int) -> int:
    if week <= 18:
        return 20  # regular season
    elif week == 19:
        return 25  # wildcard
    elif week == 20:
        return 30  # divisional
    elif week == 21:
        return 30  # conference
    elif week == 22:
        return 40  # super bowl
    else:
        return 20

# Expected win probability (with clamp logging)
def expected_score(rating_a, rating_b, home_advantage=0, is_home=True,
                   game_id=None, year=None, week=None, team_a=None, team_b=None):
    if is_home:
        ra = rating_a + home_advantage
        rb = rating_b
    else:
        ra = rating_a
        rb = rating_b + home_advantage

    raw_diff = (rb - ra) / 400

    if raw_diff > 10 or raw_diff < -10:
        print(f"[CLAMP] {game_id} {year} W{week}: Elo diff too large ({raw_diff:.2f}) "
              f"({team_a} {rating_a:.1f} vs {team_b} {rating_b:.1f}) -> clamped to ±10")

    diff = max(min(raw_diff, 10), -10)
    return 1 / (1 + 10 ** diff)

# Number-of-scores multiplier (capped)
def score_multiplier(score_diff, alpha=ALPHA, cap=1.75):
    n_scores = min(score_diff / 7, 3.5)
    if n_scores < 1:
        n_scores = 1
    return min(1 + alpha * (n_scores - 1), cap)

# Surprise adjustment (capped)
def surprise_factor(expected, cap=3.0):
    val = 2.2 / (0.001 + (expected * (1 - expected)))
    return min(val, cap)

# Elo update (with swing cap and logging)
def update_elo(rating_a, rating_b, score_a, score_b, is_home_a, k_factor,
               game_id=None, year=None, week=None, home_team=None, away_team=None):
    print(f"[GAME] {game_id} {year} W{week}: "
          f"{home_team} {rating_a:.1f} vs {away_team} {rating_b:.1f}, "
          f"score {score_a}-{score_b}, K={k_factor}")

    exp_a = expected_score(rating_a, rating_b, HOME_FIELD_ADV, is_home_a,
                           game_id, year, week, home_team, away_team)

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
    if abs(change_a) > 50:
        print(f"[CAP] {game_id} {year} W{week}: change {change_a:.1f} capped to ±50")
    change_a = max(min(change_a, 50), -50)

    change_b = -change_a

    new_a = rating_a + change_a
    new_b = rating_b + change_b

    print(f"[UPDATE] {game_id}: {home_team} -> {new_a:.1f}, {away_team} -> {new_b:.1f}, "
          f"mult={mult:.2f}, adj={adj:.2f}, exp_a={exp_a:.3f}")

    return new_a, new_b, exp_a

                                                                                                            # input/output
def compute_elo(csv_path="master_nfl_2018_2024_fixed_2.csv", output_path="nfl_elo_history_2018_2024.csv"): # using 2018 - 2024 seasons 
    df = pd.read_csv(csv_path)
    df = df.sort_values(by=["year", "week", "id"]).reset_index(drop=True)

    ratings = {}
    season_start_elos = {}
    history = []

    for _, row in df.iterrows():
        year, week = row["year"], row["week"]
        home, away = row["home-team"], row["away-team"]
        hs, as_ = row["home-score"], row["away-score"]
        game_id, date = row["id"], row["date"]

        # Ensure both teams exist with proper season baseline
        for team in [home, away]:
            if team not in ratings:
                ratings[team] = INITIAL_ELO

            if (year, team) not in season_start_elos:
                if (year - 1, team) in season_start_elos:
                    season_start_elos[(year, team)] = ratings[team]  # carry over last regressed rating
                else:
                    season_start_elos[(year, team)] = INITIAL_ELO

        r_home, r_away = ratings[home], ratings[away]
        k = get_k_factor(week)

        new_home, new_away, exp_home = update_elo(
            r_home, r_away, hs, as_, True, k,
            game_id, year, week, home, away
        )
        exp_away = 1 - exp_home

        ratings[home] = new_home
        ratings[away] = new_away

        # Record for home
        history.append({
            "id": game_id,
            "year": year,
            "week": week,
            "date": date,
            "team": home,
            "elo_before": r_home,
            "elo_after": new_home,
            "expected_win": exp_home,
            "season_start_elo": season_start_elos[(year, home)],
            "type": "game"
        })
        # Record for away
        history.append({
            "id": game_id,
            "year": year,
            "week": week,
            "date": date,
            "team": away,
            "elo_before": r_away,
            "elo_after": new_away,
            "expected_win": exp_away,
            "season_start_elo": season_start_elos[(year, away)],
            "type": "game"
        })

        # Apply regression after Super Bowl
        if week == df[df["year"] == year]["week"].max():
            regression_records = []
            for team, rating in ratings.items():
                new_rating = 0.75 * rating + 0.25 * INITIAL_ELO
                regression_records.append({
                    "id": f"{year}-regression",
                    "year": year,
                    "week": 23,
                    "date": f"offseason {year}",
                    "team": team,
                    "elo_before": rating,                     # end of season
                    "elo_after": new_rating,                  # regressed value
                    "expected_win": None,
                    "season_start_elo": season_start_elos[(year, team)],  # start of finished season
                    "next_season_start_elo": new_rating,      # start of next season
                    "type": "regression"
                })
                ratings[team] = new_rating
                season_start_elos[(year + 1, team)] = new_rating  # baseline for next season
            history.extend(regression_records)

    hist_df = pd.DataFrame(history)
    hist_df.to_csv(output_path, index=False)
    print(f"Saved Elo history to {output_path}")
    return hist_df


if __name__ == "__main__":
    compute_elo()
