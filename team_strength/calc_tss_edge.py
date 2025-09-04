# calc_tss_edge.py
import pandas as pd
import math
import argparse

# scaling constant for TSS sensitivity (like Elo's 400)
TSS_SCALE = 150  

def tss_win_prob(tss_a, tss_b):
    """Logistic function to compute win probability from TSS difference"""
    return 1 / (1 + 10 ** (-(tss_a - tss_b) / TSS_SCALE))

def main():
    parser = argparse.ArgumentParser(description="Head-to-head matchup probabilities using TSS (OSS + DSS)")
    parser.add_argument("team_a", type=str, help="Team A name")
    parser.add_argument("team_b", type=str, help="Team B name")
    parser.add_argument("--tss_file", type=str, default="./scraped_csvs_2024/team_strength_scores.csv", help="CSV with OSS/DSS/TSS results")
    args = parser.parse_args()

    # load TSS data
    df = pd.read_csv(args.tss_file)

    # lookup teams
    try:
        row_a = df[df["Team"] == args.team_a].iloc[0]
        row_b = df[df["Team"] == args.team_b].iloc[0]
    except IndexError:
        print("❌ Error: One or both teams not found. Check spelling.")
        return

    # compute win probabilities
    tss_prob_a = tss_win_prob(row_a["TSS"], row_b["TSS"])
    tss_prob_b = 1 - tss_prob_a

    # edge vs 50/50 baseline
    edge_a = tss_prob_a - 0.5
    edge_b = -edge_a

    # output
    print("\n==================== Matchup ====================")
    print(f"{args.team_a} vs {args.team_b}")
    print("------------------------------------------------")
    print(f"{args.team_a}: RawOSS={row_a['RawOSS']:.3f}, RawDSS={row_a['RawDSS']:.3f}, TSS={row_a['TSS']:.3f}")
    print(f"{args.team_b}: RawOSS={row_b['RawOSS']:.3f}, RawDSS={row_b['RawDSS']:.3f}, TSS={row_b['TSS']:.3f}")
    print("------------------------------------------------")
    print(f"TSS Win Prob: {args.team_a} {tss_prob_a:.1%} | {args.team_b} {tss_prob_b:.1%}")
    print(f"Edge (vs 50/50): {args.team_a} {edge_a:+.1%} | {args.team_b} {edge_b:+.1%}")
    print("================================================\n")

if __name__ == "__main__":
    main()