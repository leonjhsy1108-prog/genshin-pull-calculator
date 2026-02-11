# Genshin Pull Calculator (EV + Probability)

Two small **Tkinter GUI** tools for estimating gacha outcomes in **Genshin Impact**:

- **Expected Value (EV) Calculator**: estimates the *average* number of pulls (and primogems) needed for a target.
- **Probability Calculator (Monte Carlo)**: given a fixed pull budget, estimates the probability you reach your target.

> Disclaimer: This project is **not affiliated with HoYoverse**. It’s for educational / personal use.  
> Any gacha model is an approximation; always treat results as estimates, not guarantees.

---

## What’s included

### 1) EV calculator — expected pulls & primogems
File: `genshin_expected_pull_calculator.py`

- Computes the expected number of **5★ hits** needed for:
  - Character banner target copies
  - Weapon banner target copies
- Converts expected 5★ hits → expected pulls using your provided **5★ timing CDFs**
- Converts pulls → primogems using `160 primogems = 1 pull`

**Notes (EV version):**
- This script computes expected pulls using the *unconditional* expected pulls per 5★ from the CDFs.
- It **does not** currently ask for / condition on current pity.

---

### 2) Probability calculator — chance to finish within a pull budget
File: `genshin_probability_calculator.py`

- Takes a **pull budget** and estimates your chance to reach the target using Monte Carlo simulation.
- Uses your provided **CDFs** to sample “pulls until next 5★”.
- Supports **current pity** (character & weapon) and the “guaranteed” state.
- Reports:
  - Estimated success probability
  - Approximate 95% uncertainty half-width based on simulation standard error

**Spending strategy (Probability version):**
- The simulation spends pulls **Characters first → then Weapons** (from the same pull budget).

---

## Game rules modeled 

### Character banner (5★ featured)
- Base chance the 5★ is the featured banner character: **55%**
- If you miss the featured character, the **next 5★ is guaranteed featured**
- “Completed double-cost streak” rule:
  - The streak counts **consecutive banner characters you already obtained** that each required **2× 5★** (miss once → then guaranteed).
  - If you reach a streak of **3**, the next banner character is forced on the **first 5★** (featured guaranteed regardless of the 55% roll).

✅ **Important input guidance (streak vs guaranteed):**
- The streak **only increases after you obtain the banner character via a guaranteed (double-cost) completion**.
- If you just missed and are currently guaranteed but haven’t obtained the banner character yet, that **does not** increase the completed streak.

Example:
- You completed two double-cost banner characters in a row (streak = 2),
- then you miss again and are now guaranteed,
- but you haven’t gotten the banner character yet.

Enter:
- **Character guaranteed = Yes**
- **Completed double-cost streak = 2** (NOT 3)

---

### Weapon banner (desired weapon)
- Two banner weapons exist; desired weapon chance per 5★: **37.5%**
- If the 5★ is not the desired one, the **next 5★ is guaranteed desired**
- No “3-streak” rule applies to weapons in this project.

---

## Requirements

- Python **3.10+** recommended
- Tkinter (bundled with most Python installations)

No external libraries required.

---

## How to run

Run the program
```
python genshin_expected_pull_calculator.py
python genshin_probability_calculator.py
```

A small window will open with all inputs available at once.

---

## Outputs

### EV Calculator
- **Expected total pulls**
- **Expected total primogems** (pulls × 160)

### Probability Calculator
- **Estimated probability of success**
- **Uncertainty (approx. 95% CI half-width)**, derived from Monte Carlo standard error

---

# Notes

- This tool does not validate in-game feasibility

- It focuses purely on turn math and advance mechanics

- Intended as a planning and theorycrafting aid

# License

- This project is provided for personal and educational use.
  
- Not affiliated with or endorsed by HoYoverse.


