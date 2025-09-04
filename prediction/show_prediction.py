import pandas as pd
import os

def show_predictions(week, 
                     schedule_file="schedule.csv",
                     active_file="nfl_elo_active.csv",
                     output_dir="week_reports"):
    # Load files
    df_sched = pd.read_csv(schedule_file)
    df_active = pd.read_csv(active_file)

    # Filter schedule to chosen week
    week_sched = df_sched[df_sched["week"] == week]
    if week_sched.empty:
        print(f"❌ No schedule found for week {week}")
        return

    # Collect rows for CSV export
    report_rows = []

    print(f"\n==================== Week {week} Predictions ====================")
    for _, game in week_sched.iterrows():
        home = game["home team"]
        away = game["away team"]

        try:
            row_home = df_active[(df_active["week"] == week) & (df_active["team"] == home)].iloc[-1]
            row_away = df_active[(df_active["week"] == week) & (df_active["team"] == away)].iloc[-1]
        except IndexError:
            print(f"⚠️ Missing data for {home} vs {away}, skipping")
            continue

        print("--------------------------------------------------")
        print(f"{home} vs {away}")
        print("--------------------------------------------------")
        print(f"{home}: Elo={row_home['elo_before']:.1f}, "
              f"ExpWin={row_home['expected_win']:.1%}, "
              f"TSS Prob={row_home.get('tss_win_prob', float('nan')):.1%}, "
              f"TSS Edge={row_home.get('tss_edge', float('nan')):+.1%}, "
              f"Total Edge={row_home.get('total_edge', float('nan')):+.1%}")
        print(f"{away}: Elo={row_away['elo_before']:.1f}, "
              f"ExpWin={row_away['expected_win']:.1%}, "
              f"TSS Prob={row_away.get('tss_win_prob', float('nan')):.1%}, "
              f"TSS Edge={row_away.get('tss_edge', float('nan')):+.1%}, "
              f"Total Edge={row_away.get('total_edge', float('nan')):+.1%}")
        print("")

        # Append rows for export
        report_rows.append({
            "week": week,
            "matchup": f"{home} vs {away}",
            "team": home,
            "elo_before": row_home["elo_before"],
            "expected_win": row_home["expected_win"],
            "tss_win_prob": row_home.get("tss_win_prob", None),
            "tss_edge": row_home.get("tss_edge", None),
            "total_edge": row_home.get("total_edge", None),
        })
        report_rows.append({
            "week": week,
            "matchup": f"{home} vs {away}",
            "team": away,
            "elo_before": row_away["elo_before"],
            "expected_win": row_away["expected_win"],
            "tss_win_prob": row_away.get("tss_win_prob", None),
            "tss_edge": row_away.get("tss_edge", None),
            "total_edge": row_away.get("total_edge", None),
        })

    print("==================================================\n")

    # Save CSV
    if report_rows:
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"week_{week}_predictions.csv")
        pd.DataFrame(report_rows).to_csv(output_file, index=False)
        print(f"✅ Exported predictions to {output_file}")


if __name__ == "__main__":
    try:
        week = int(input("Enter week number to show predictions: "))
        show_predictions(week)
    except ValueError:
        print("❌ Invalid input. Please enter a valid week number.")
