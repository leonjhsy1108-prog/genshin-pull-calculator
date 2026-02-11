import tkinter as tk
from tkinter import ttk, messagebox
import random
import math


CHAR_CDF_LIST = [
    0.006, 0.0119639999, 0.017892216, 0.0237848627, 0.0296421535, 0.0354643006,
    0.0412515148, 0.0470040057, 0.0527219816, 0.0584056497, 0.0640552158,
    0.0696708845, 0.0752528592, 0.0808013421, 0.086316534, 0.0917986348,
    0.097247843, 0.102664356, 0.1080483698, 0.1134000796, 0.1187196791,
    0.124007361, 0.1292633169, 0.134487737, 0.1396808106, 0.1448427257,
    0.1499736693, 0.1550738273, 0.1601433844, 0.1651825241, 0.1701914289,
    0.1751702803, 0.1801192587, 0.1850385431, 0.1899283118, 0.194788742,
    0.1996200095, 0.2044222895, 0.2091957557, 0.2139405812, 0.2186569377,
    0.2233449961, 0.2280049261, 0.2326368965, 0.2372410752, 0.2418176287,
    0.2463667229, 0.2508885226, 0.2553831915, 0.2598508923, 0.264291787,
    0.2687060362, 0.2730938, 0.2774552372, 0.2817905058, 0.2860997628,
    0.2903831642, 0.2946408652, 0.29887302, 0.3030797819, 0.3072613032,
    0.3114177354, 0.315549229, 0.3196559336, 0.323737998, 0.32779557,
    0.3318287966, 0.3358378238, 0.3398227969, 0.3437838601, 0.3477211569,
    0.35163483, 0.355525021, 0.3980603696, 0.473904763, 0.5717584771,
    0.6771058917, 0.7759114888, 0.8579278839, 0.9184506053, 0.9580836111,
    0.9809699594, 0.992502164, 0.9974957227, 0.999313828, 0.9998531592,
    0.9999773865, 0.9999978743, 0.9999999277,
]
CHAR_CDF_LIST.append(1.0)  

WEAPON_CDF_LIST = [
    0.007, 0.013951, 0.0208533429, 0.0277073695, 0.034513418, 0.041271824,
    0.0479829213, 0.0546470408, 0.0612645115, 0.06783566, 0.0743608103,
    0.0808402847, 0.0872744027, 0.0936634818, 0.1000078375, 0.1063077826,
    0.1125636281, 0.1187756827, 0.124944253, 0.1310696432, 0.1371521557,
    0.1431920906, 0.149189746, 0.1551454177, 0.1610593998, 0.166931984,
    0.1727634601, 0.1785541159, 0.1843042371, 0.1900141074, 0.1956840087,
    0.2013142206, 0.2069050211, 0.2124566859, 0.2179694891, 0.2234437027,
    0.2288795968, 0.2342774396, 0.2396374975, 0.244960035, 0.2502453148,
    0.2554935976, 0.2607051424, 0.2658802064, 0.271019045, 0.2761219116,
    0.2811890583, 0.2862207349, 0.2912171897, 0.2961786694, 0.3011054187,
    0.3059976808, 0.310855697, 0.3156797071, 0.3204699492, 0.3252266595,
    0.3299500729, 0.3346404224, 0.3392979394, 0.3439228539, 0.3485153939,
    0.3530757861, 0.4028889506, 0.4906642749, 0.6011901272, 0.7156485607,
    0.8171620245, 0.89523384, 0.9473026215, 0.9771820351, 0.9917170787,
    0.997573104, 0.9994588022, 0.9998982548, 0.9999844329, 0.999998163,
    0.9999998475, 0.9999999926, 0.9999999999, 1.0
]

def list_to_cdf_dict(lst):
    return {i + 1: float(v) for i, v in enumerate(lst)}

CHAR_CDF = list_to_cdf_dict(CHAR_CDF_LIST)     
WEAPON_CDF = list_to_cdf_dict(WEAPON_CDF_LIST) 

def pmf_from_cdf(cdf_by_k: dict[int, float]) -> list[float]:
    K = max(cdf_by_k)
    pmf = []
    prev = 0.0
    for k in range(1, K + 1):
        p = cdf_by_k[k] - prev
        pmf.append(max(0.0, p))
        prev = cdf_by_k[k]
    s = sum(pmf)
    if s <= 0:
        raise ValueError("Invalid CDF.")
    return [x / s for x in pmf]  

CHAR_PMF = pmf_from_cdf(CHAR_CDF)
WEAPON_PMF = pmf_from_cdf(WEAPON_CDF)

def conditional_remaining_pmf(pmf: list[float], pity: int) -> list[float]:
    K = len(pmf)
    pity = max(0, min(int(pity), K - 1))
    tail = pmf[pity:]  
    s = sum(tail)
    if s <= 0:
        return [1.0]
    return [x / s for x in tail]  

def sample_from_pmf(pmf: list[float]) -> int:
    r = random.random()
    cum = 0.0
    for i, p in enumerate(pmf, start=1):
        cum += p
        if r <= cum:
            return i
    return len(pmf)

def simulate_probability(
    pulls_budget: int,
    char_copies_needed: int,
    weapon_copies_needed: int,
    char_pity: int,
    weapon_pity: int,
    char_guaranteed: bool,
    weapon_guaranteed: bool,
    char_completed_streak: int,
    trials: int,
    seed: int | None = None
) -> tuple[float, float]:
    if seed is not None:
        random.seed(seed)

    P_CHAR = 0.55
    P_WEAPON = 0.375

    pulls_budget = int(pulls_budget)
    trials = int(trials)

    s0 = max(0, min(int(char_completed_streak), 3))
    if s0 == 3:
        char_guaranteed = False  

    char_first = conditional_remaining_pmf(CHAR_PMF, char_pity)
    weap_first = conditional_remaining_pmf(WEAPON_PMF, weapon_pity)

    succ = 0
    for _ in range(trials):
        pulls_left = pulls_budget

        c_need = int(char_copies_needed)
        c_streak = s0
        c_guar = bool(char_guaranteed)
        char_next_pmf = char_first

        while c_need > 0 and pulls_left > 0:
            forced = (c_streak == 3)

            rem = sample_from_pmf(char_next_pmf)
            if rem > pulls_left:
                pulls_left = 0
                break
            pulls_left -= rem

            if forced:
                c_need -= 1
                c_streak = 0
                c_guar = False
            elif c_guar:
                c_need -= 1
                c_streak = min(3, c_streak + 1)
                c_guar = False
            else:
                if random.random() < P_CHAR:
                    c_need -= 1
                    c_streak = 0
                else:
                    c_guar = True

            char_next_pmf = CHAR_PMF

        w_need = int(weapon_copies_needed)
        w_guar = bool(weapon_guaranteed)
        weap_next_pmf = weap_first

        while w_need > 0 and pulls_left > 0:
            rem = sample_from_pmf(weap_next_pmf)
            if rem > pulls_left:
                pulls_left = 0
                break
            pulls_left -= rem

            if w_guar:
                w_need -= 1
                w_guar = False
            else:
                if random.random() < P_WEAPON:
                    w_need -= 1
                else:
                    w_guar = True

            weap_next_pmf = WEAPON_PMF

        if c_need <= 0 and w_need <= 0:
            succ += 1

    p_hat = succ / float(trials)
    se = math.sqrt(p_hat * (1 - p_hat) / float(trials)) if trials > 0 else 0.0
    return p_hat, se

class ProbGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Genshin Probability Calculator (Given Pull Budget)")
        self.geometry("920x520")

        self.pulls_budget = tk.IntVar(value=0)
        self.char_copies = tk.IntVar(value=1)
        self.weapon_copies = tk.IntVar(value=0)

        self.char_pity = tk.IntVar(value=0)
        self.weapon_pity = tk.IntVar(value=0)

        self.char_guaranteed = tk.BooleanVar(value=False)
        self.weapon_guaranteed = tk.BooleanVar(value=False)

        self.char_streak = tk.IntVar(value=0)  

        self.trials = tk.IntVar(value=50000)

        self.out_prob = tk.StringVar(value="")
        self.out_ci = tk.StringVar(value="")

        self._build()

    def _build(self):
        pad = {"padx": 10, "pady": 6}
        ttk.Label(self, text="Probability of Success (Monte Carlo)", font=("Segoe UI", 16, "bold")).pack(pady=10)

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=10, pady=10)

        left = ttk.Frame(frm)
        left.pack(side="left", fill="both", expand=True)

        right = ttk.Frame(frm)
        right.pack(side="right", fill="both", expand=True)

        ttk.Label(left, text="Pull Budget + Targets", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", **pad)

        ttk.Label(left, text="Total pulls you can spend:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Entry(left, textvariable=self.pulls_budget, width=14).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(left, text="Desired character copies:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=50, textvariable=self.char_copies, width=12).grid(row=2, column=1, sticky="w", **pad)

        ttk.Label(left, text="Desired weapon copies:").grid(row=3, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=50, textvariable=self.weapon_copies, width=12).grid(row=3, column=1, sticky="w", **pad)

        ttk.Separator(left, orient="horizontal").grid(row=4, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Label(left, text="Banner states", font=("Segoe UI", 12, "bold")).grid(row=5, column=0, sticky="w", **pad)

        ttk.Label(left, text="Character pity (0–89):").grid(row=6, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=89, textvariable=self.char_pity, width=12).grid(row=6, column=1, sticky="w", **pad)

        ttk.Checkbutton(left, text="Character currently guaranteed",
                        variable=self.char_guaranteed).grid(row=7, column=0, columnspan=2, sticky="w", **pad)

        ttk.Label(left, text="Completed double-cost banner streak (0–3):").grid(row=8, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=3, textvariable=self.char_streak, width=12).grid(row=8, column=1, sticky="w", **pad)

        ttk.Label(left, text="Weapon pity (0–79):").grid(row=9, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=79, textvariable=self.weapon_pity, width=12).grid(row=9, column=1, sticky="w", **pad)

        ttk.Checkbutton(left, text="Weapon currently guaranteed",
                        variable=self.weapon_guaranteed).grid(row=10, column=0, columnspan=2, sticky="w", **pad)

        ttk.Separator(left, orient="horizontal").grid(row=11, column=0, columnspan=2, sticky="ew", padx=10, pady=10)

        ttk.Label(left, text="Simulation settings", font=("Segoe UI", 12, "bold")).grid(row=12, column=0, sticky="w", **pad)
        ttk.Label(left, text="Trials:").grid(row=13, column=0, sticky="w", **pad)
        ttk.Entry(left, textvariable=self.trials, width=14).grid(row=13, column=1, sticky="w", **pad)

        ttk.Button(left, text="Estimate Probability", command=self.run).grid(
            row=14, column=0, columnspan=2, sticky="ew", padx=10, pady=14
        )
        ttk.Button(left, text="Help: how to enter streak", command=self.help).grid(
            row=15, column=0, columnspan=2, sticky="ew", padx=10, pady=6
        )

        ttk.Label(right, text="Results", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", **pad)

        ttk.Label(right, text="Estimated success probability:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Label(right, textvariable=self.out_prob, font=("Segoe UI", 11, "bold")).grid(row=1, column=1, sticky="w", **pad)

        ttk.Label(right, text="Uncertainty (approx 95% half-width):").grid(row=2, column=0, sticky="w", **pad)
        ttk.Label(right, textvariable=self.out_ci, font=("Segoe UI", 10)).grid(row=2, column=1, sticky="w", **pad)

    def help(self):
        guide = (
            "Completed double-cost banner streak (0–3)\n\n"
            "Count consecutive banner characters you ALREADY OBTAINED where each required 2×5★\n"
            "(miss once, then guaranteed).\n\n"
            "Do NOT count a miss that happened but you haven't obtained the banner yet.\n\n"
            "Example:\n"
            "You completed two double-cost banner characters in a row, then miss again now,\n"
            "so you are currently guaranteed but haven't gotten the banner yet:\n"
            "Guaranteed=YES, Streak=2."
        )
        messagebox.showinfo("Help", guide)

    def run(self):
        try:
            budget = int(self.pulls_budget.get())
            if budget < 0:
                raise ValueError("Pull budget cannot be negative.")

            c = int(self.char_copies.get())
            w = int(self.weapon_copies.get())
            if c < 0 or w < 0:
                raise ValueError("Desired copies cannot be negative.")

            cp = int(self.char_pity.get())
            wp = int(self.weapon_pity.get())
            if not (0 <= cp <= 89):
                raise ValueError("Character pity must be 0–89.")
            if not (0 <= wp <= 79):
                raise ValueError("Weapon pity must be 0–79.")

            cg = bool(self.char_guaranteed.get())
            wg = bool(self.weapon_guaranteed.get())

            s = int(self.char_streak.get())
            if not (0 <= s <= 3):
                raise ValueError("Streak must be 0–3.")

            t = int(self.trials.get())
            if t <= 0 or t > 1_000_000:
                raise ValueError("Trials must be between 1 and 1,000,000.")

            p_hat, se = simulate_probability(
                pulls_budget=budget,
                char_copies_needed=c,
                weapon_copies_needed=w,
                char_pity=cp,
                weapon_pity=wp,
                char_guaranteed=cg,
                weapon_guaranteed=wg,
                char_completed_streak=s,
                trials=t,
                seed=None
            )

            ci = 1.96 * se
            self.out_prob.set(f"{100*p_hat:.2f}%")
            self.out_ci.set(f"±{100*ci:.2f}%  (trials={t:,d})")

        except Exception as e:
            messagebox.showerror("Input error", str(e))

if __name__ == "__main__":
    app = ProbGUI()
    app.mainloop()
