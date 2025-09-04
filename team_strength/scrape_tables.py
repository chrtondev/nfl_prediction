import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import time
import re

def clean_filename(name: str) -> str:
    """Convert a title into a safe CSV filename."""
    name = name.lower()
    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_") + ".csv"

def scrape_table(url, output_csv=None, table_id=None):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/115.0 Safari/537.36"
        )
    }

    print(f"Scraping {url} ...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    # Auto-generate filename from page title if none given
    if not output_csv:
        title = soup.find("title").get_text(strip=True)
        output_csv = clean_filename(title)

    # Find table by ID or default to the first one
    if table_id:
        table = soup.find("table", {"id": table_id})
    else:
        table = soup.find("table")  # just take the first table

    if table is None:
        print(f"❌ No table found at {url}")
        return

    # Extract headers
    thead = table.find("thead")
    if thead:
        headers = [th.get_text(strip=True) for th in thead.find_all("th")]
    else:
        headers = []

    # Extract rows
    tbody = table.find("tbody")
    rows = []
    if tbody:
        trs = tbody.find_all("tr")
    else:
        trs = table.find_all("tr")

    for tr in trs:
        row = [td.get_text(strip=True) for td in tr.find_all(["td", "th"])]
        if row:
            rows.append(row)

    # If no headers, infer from first row
    if not headers and rows:
        headers = [f"col{i+1}" for i in range(len(rows[0]))]

    # Convert to DataFrame
    df = pd.DataFrame(rows, columns=headers)

    # Ensure folder exists
    os.makedirs("scraped_csvs_2024", exist_ok=True)
    output_path = os.path.join("scraped_csvs_2024", output_csv)

    # Save CSV
    df.to_csv(output_path, index=False)
    print(f"✅ Saved table to {output_path} ({len(df)} rows)")

    return df

    '''
        "https://www.teamrankings.com/nfl/stat/points-per-game",
        "https://www.teamrankings.com/nfl/stat/rushing-yards-per-game",
        "https://www.teamrankings.com/nfl/stat/fourth-downs-per-game",
        "https://www.teamrankings.com/nfl/stat/third-down-conversion-pct",
        "https://www.teamrankings.com/nfl/stat/yards-per-game",
        "https://www.teamrankings.com/nfl/stat/passing-touchdowns-per-game",
        "https://www.teamrankings.com/nfl/stat/average-team-passer-rating",
        "https://www.teamrankings.com/nfl/stat/interceptions-thrown-per-game",
        "https://www.teamrankings.com/nfl/stat/qb-sacked-per-game",
        "https://www.teamrankings.com/nfl/stat/rushing-touchdowns-per-game",
        "https://www.teamrankings.com/nfl/stat/rushing-first-downs-per-game"
        '''

if __name__ == "__main__":
    urls_to_scrape = [

        # defensive csvs
        "https://www.teamrankings.com/nfl/stat/rushing-first-downs-per-game",
        "https://www.teamrankings.com/nfl/stat/opponent-fumbles-per-game",
        "https://www.teamrankings.com/nfl/stat/takeaways-per-game",
        "https://www.teamrankings.com/nfl/stat/interceptions-per-game",
        "https://www.teamrankings.com/nfl/stat/opponent-touchdowns-per-game",
        "https://www.teamrankings.com/nfl/stat/opponent-yards-per-game",
        "https://www.teamrankings.com/nfl/stat/opponent-red-zone-scoring-pct",
        "https://www.teamrankings.com/nfl/stat/opponent-fourth-downs-per-game"
        
    ]

    for url in urls_to_scrape:
        try:
            scrape_table(url)
            time.sleep(3)  # polite delay
        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
