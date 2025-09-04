import requests
from bs4 import BeautifulSoup
import pandas as pd
from io import StringIO
import time

def scrape_schedule(year=2025, weeks=18, output_path="schedule.csv"):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
    }

    games = []

    for week in range(1, weeks + 1):
        url = f"https://www.pro-football-reference.com/years/{year}/week_{week}.htm"
        print(f"Scraping Week {week}: {url}")

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        game_blocks = soup.find_all("div", class_="game_summaries")

        for block in game_blocks:
            tables = [t for t in block.find_all("table") if "stats" not in t.get("class", [])]

            for table in tables:
                df = pd.read_html(StringIO(str(table)))[0]

                # Row 0 col 0 = date, Row 1 = away team, Row 2 = home team
                date = df.iloc[0, 0]
                away_team = df.iloc[1, 0]
                home_team = df.iloc[2, 0]

                games.append({
                    "week": week,
                    "date": date,
                    "home team": home_team,
                    "away team": away_team
                })

        # polite scraping delay
        time.sleep(3)

    # Save all weeks into one CSV
    df_games = pd.DataFrame(games)
    df_games.to_csv(output_path, index=False)
    print(f"✅ Saved schedule to {output_path} ({len(df_games)} games)")

if __name__ == "__main__":
    scrape_schedule()
