# This is to make the directory make a bit of sense for further work.

### nfl_csvs/
- a directory of each season from 2018 - 2024 NFL matchup, score, and home and away.
    sorted by weeks. 

### team_elo_plots/
- a folder of all created line graphs. shows elo per week from 2018 - 2024, output from 
    elo_plot.py

### master_nfl_2018_2024_fixed.csv
- a csv file for every single years season into one csv. (nfl_csvs/ combined)

### nfl_elo_history.csv
- using the (master_nfl_2018_2024_fixed.csv) this has the elo before the game, elo after the game
    and then season start elo. There is also the a expected win percentage for each team per week
    and year. Both teams are shown so both win percentages are recorded.

### matchup_elo_dif.csv
- shows the avg difference in elo with elo

### team_elo_profiles.py
- shows the avg elo, max elo, and min elo

### calc_elo.py
- will calculate the elo for each team per game, uses the master_nfl_2018_2024_fixed.csv in order 
    to get the season matchup and winner, alongside the score.

### get_games.py
- used to get the games from 2018 - 2024 from the site,
    "https://www.pro-football-reference.com/years/{year}/week_{week}.htm", the url had variables
    defined so scraping was easier and could be done batched

### name.py
- data cleaning file that changed the name of the teams that had name or location changes
    throughout the years

### elo_plot.py
- creates visual plots for for each team the tracks the elo each week from 2019 - 2024, In the 
    graph a mark for start of season regression is there (dot) and there is a horizontal line
    marking the leauge average elo.

### elo_profile.py
- a script that gives the avg elo difference for each team each year 2018 - 2024, also gives team
    elo profiles that gives avg, max, min

### win_report.py
- win report takes the expected win percentage through 2018 - 2024 calculates the expected win %
    over games played, gives year wide league averages, and creates a csv's for the overall EWP
    from 2018 - 2024 and the year by year EWP for each team. Also, gives a visual plot for each
    team year by year EWP.

### get_sched.py
- this scrapes the site pro-football-reference in order to get the schedule. Main utilization is
    to get the current year and total weeks to get the regular season schedule, saved as
    schedule.csv

### diff_plot.py
- uses the matchup_elo_diff_2018_2024.csv file in order to plot the difference across the years
    with a horizontal league average indicator.

### swap_teams.py
- this was used to fix the home and away team, because it was initially wrongly labled

### prediction/predict.py
- 

## NEW FILES TO DEFINE
- prediction/predict.py
- prediction/update.py
- team_strength/calc_dss.py
- team_strength/calc_oss.py
- team_strength/calc_tss_edge.py
- team_stregth/calc_tss.py
- team_strength/convert_percent.py
- team_strength/scrape_tables.py
- prediction/week_reports/
- prediction/show_prediction.py
- team_strength/add_tss_active.py
- team_strength/scraped_csvs/


## NEEDS
- After week 1 in NFL change the URLS and year to be scraped after week 1 games completed. in the
    OSS, DSS, and TSS calculations.
- 

