import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import os
import time

def scrape_matchups(url: str, year: int, week: int):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    game_blocks = soup.find_all("div", class_="game_summaries")

    games = []
    game_id = 1

    for block in game_blocks:
        # Skip stats tables
        tables = [
            t for t in block.find_all("table")
            if "stats" not in t.get("class", [])
        ]

        for table in tables:
            df = pd.read_html(StringIO(str(table)))[0]

            date = df.iloc[0, 0]
            team1 = df.iloc[1, 0]
            score1 = int(df.iloc[1, 1])
            team2 = df.iloc[2, 0]
            score2 = int(df.iloc[2, 1])

            if score1 > score2:
                winner = team1
            elif score2 > score1:
                winner = team2
            else:
                winner = "Tie"

            games.append({
                "id": f"{year}-{week}-{game_id}",
                "year": year,
                "week": week,
                "home-team": team2,      # FIX: home is the bottom row
                "home-score": score2,
                "away-team": team1,      # FIX: away is the top row
                "away-score": score1,
                "winner": winner,
                "date": date
            })
            game_id += 1

    return games


if __name__ == "__main__":
    all_games = []
    os.makedirs("nfl_csvs", exist_ok=True)

    for year in range(2000, 2017):  # 2018–2024
        year_games = []
        print(f"Scraping {year} season...")

        for week in range(1, 23):  # Weeks 1–22
            url = f"https://www.pro-football-reference.com/years/{year}/week_{week}.htm"
            print(f"  Week {week} ...", end=" ")

            try:
                week_games = scrape_matchups(url, year, week)
                year_games.extend(week_games)
                print(f"{len(week_games)} games")
            except Exception as e:
                print(f"skipped ({e})")

            # Throttle requests: ~1 every 3 seconds (20/minute safe)
            time.sleep(3)

        # Save per-year CSV
        df_year = pd.DataFrame(year_games)
        df_year.to_csv(f"nfl_csvs/nfl_{year}.csv", index=False)
        print(f"Saved nfl_csvs/nfl_{year}.csv ({len(df_year)} games)")

        all_games.extend(year_games)

    # Save one master CSV
    df_all = pd.DataFrame(all_games)
    df_all.to_csv("nfl_2018_2024.csv", index=False)
    print(f"Saved master_nfl_2000_2016.csv ({len(df_all)} total games)")
# note that the above scrapes the 2000 - 2016 seasons from the nfl 