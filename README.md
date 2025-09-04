# NFL TEAM ELO

### This project will give NFL Teams an ELO score from the year 2018 - 2024.

- This is meant to see what happens if you do. Does a team maintain the given score through the
years; or does a staff change, player injury ,or any of the other many things that can happen 
completly change the "skill" of the team.

- This can almost be a ELO score representing the skill of the GM/Owner. Do their decisions have a
majopr effect on the team reflecting in the ELO Score?

- This is going to grow and change through the NFL Season. Very dynamic let's learn!

---

# NFL Elo Model Formulas 

## 1. **Expected Score (Win Probability)**

**Function:**

$$
P(A) = \frac{1}{1 + 10^{\frac{(R_B - R_A + H)}{400}}}
$$

**Where:**

* $P(A)$: Expected probability that team **A** wins.
* $R_A$: Elo rating of team **A**.
* $R_B$: Elo rating of opponent team **B**.
* $H$: Home field advantage adjustment (added to home team’s rating).

**Purpose:**
Calculates the *pre-game probability* of winning, based on Elo ratings and home field edge.

---

## 2. **Margin-of-Victory (MOV) Multiplier**

**Function:**

$$
M = 1 + \alpha \cdot (\min(\tfrac{\Delta}{7}, 3.5) - 1)
$$

**Where:**

* $M$: MOV multiplier (capped).
* $\Delta$: Score difference (absolute value of points).
* $7$: One score = 7 points (touchdown + XP).
* $3.5$: Max cap of 3.5 scores (to limit garbage time blowouts).
* $\alpha$: Scaling factor (default = 0.3).

**Purpose:**
Rewards wins by larger margins, but prevents runaway effects from extreme blowouts.

---

## 3. **Surprise Factor (Upset Adjustment)**

**Function:**

$$
S = \min\left(\frac{2.2}{0.001 + P(A)(1 - P(A))}, \; cap \right)
$$

**Where:**

* $S$: Surprise factor multiplier.
* $P(A)$: Expected win probability of team **A**.
* $cap$: Maximum value (default = 3.0).

**Purpose:**
Upsets (when a low-probability team wins) are weighted more heavily. Capped to prevent absurd jumps.

---

## 4. **Elo Update Rule**

**Function:**

$$
R'_A = R_A + \Delta R
$$

$$
\Delta R = \min\Big(\max\big(K \cdot M \cdot S \cdot (O_A - P(A)), \; -50\big), \; +50\big)
$$

**Where:**

* $R'_A$: New Elo rating of team **A**.
* $R_A$: Old Elo rating of team **A**.
* $\Delta R$: Elo change for the game.
* $K$: Base K-factor (varies by season stage).
* $M$: Margin-of-victory multiplier.
* $S$: Surprise factor.
* $O_A$: Actual result of team **A** (1 = win, 0 = loss, 0.5 = tie).
* $P(A)$: Expected win probability.
* Cap: Elo swing per game limited to ±50.

**Purpose:**
Adjusts ratings after each game. More points gained for surprising upsets, strong wins, or playoff games.

---

## 5. **Season Regression**

**Function:**

$$
R' = 0.75 \cdot R + 0.25 \cdot 1500
$$

**Where:**

* $R$: End-of-season Elo rating.
* $R'$: Regressed Elo rating (used as baseline next season).
* $1500$: League mean Elo.

**Purpose:**
Prevents ratings from drifting too far over multiple years. Ensures new season begins with compressed distribution.

---

## 6. **K-Factor Schedule**

**Values Used:**

* Regular Season (Weeks 1–18): $K = 20$
* Wildcard (Week 19): $K = 25$
* Divisional (Week 20): $K = 30$
* Conference (Week 21): $K = 30$
* Super Bowl (Week 22): $K = 40$

**Purpose:**
Higher-stakes games are weighted more heavily, reflecting greater information about team strength.





