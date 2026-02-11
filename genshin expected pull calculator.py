import tkinter as tk
from tkinter import ttk, messagebox
from functools import lru_cache

PRIMOS_PER_PULL = 160

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

def expected_5star_from_cdf(cdf):
    E, prev = 0.0, 0.0
    for k in range(1, max(cdf) + 1):
        E += 1.0 - prev
        prev = cdf[k]
    return E

def expected_featured_5stars_needed_character(m, p, streak):
    q = 1 - p
    streak = max(0, min(streak, 3))

    @lru_cache(None)
    def E(left, s):
        if left <= 0:
            return 0.0
        if s == 3:
            return 1.0 + E(left - 1, 0)
        return (
            p * (1.0 + E(left - 1, 0)) +
            q * (2.0 + E(left - 1, min(3, s + 1)))
        )

    return E(m, streak)

def expected_featured_5stars_needed_weapon(m, p, guaranteed):
    if m <= 0:
        return 0.0
    per_copy = 2.0 - p
    return 1.0 + (m - 1) * per_copy if guaranteed else m * per_copy

def expected_total_pulls_and_primos(char_copies, weapon_copies, char_guaranteed, char_streak, weapon_guaranteed):
    P_CHAR = 0.55
    P_WEAPON = 0.375

    E5_char = expected_5star_from_cdf(CHAR_CDF)
    E5_weapon = expected_5star_from_cdf(WEAPON_CDF)

    if char_streak == 3:
        char_guaranteed = False

    if char_copies <= 0:
        char_5s = 0.0
    elif char_guaranteed:
        char_5s = 1.0 + expected_featured_5stars_needed_character(
            char_copies - 1, P_CHAR, min(3, char_streak + 1)
        )
    else:
        char_5s = expected_featured_5stars_needed_character(char_copies, P_CHAR, char_streak)

    weapon_5s = expected_featured_5stars_needed_weapon(
        weapon_copies, P_WEAPON, weapon_guaranteed
    )

    pulls = char_5s * E5_char + weapon_5s * E5_weapon
    return pulls, pulls * PRIMOS_PER_PULL

class EVGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Genshin EV Calculator")
        self.geometry("780x400")

        self.char_copies = tk.IntVar(value=1)
        self.weapon_copies = tk.IntVar(value=0)
        self.char_guaranteed = tk.BooleanVar(value=False)
        self.weapon_guaranteed = tk.BooleanVar(value=False)
        self.char_streak = tk.IntVar(value=0)

        self.out_pulls = tk.StringVar()
        self.out_primos = tk.StringVar()
        self._build()

    def _build(self):
        pad = {"padx": 10, "pady": 8}
        ttk.Label(self, text="Expected Pulls", font=("Segoe UI", 16, "bold")).pack(pady=14)

        frm = ttk.Frame(self)
        frm.pack(fill="both", expand=True, padx=14, pady=10)
        left, right = ttk.Frame(frm), ttk.Frame(frm)
        left.pack(side="left", expand=True, fill="both")
        right.pack(side="right", expand=True, fill="both")

        ttk.Label(left, text="Targets", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", **pad)
        ttk.Label(left, text="Desired character copies:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=50, textvariable=self.char_copies, width=12).grid(row=1, column=1, **pad)

        ttk.Label(left, text="Desired weapon copies:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=50, textvariable=self.weapon_copies, width=12).grid(row=2, column=1, **pad)

        ttk.Separator(left, orient="horizontal").grid(row=3, column=0, columnspan=2, sticky="ew", pady=12)

        ttk.Label(left, text="Banner state", font=("Segoe UI", 12, "bold")).grid(row=4, column=0, sticky="w", **pad)

        ttk.Checkbutton(left, text="Character guaranteed featured", variable=self.char_guaranteed)\
            .grid(row=5, column=0, columnspan=2, sticky="w", **pad)

        ttk.Label(left, text="Completed double-cost streak:").grid(row=6, column=0, sticky="w", **pad)
        ttk.Spinbox(left, from_=0, to=3, textvariable=self.char_streak, width=12)\
            .grid(row=6, column=1, **pad)

        ttk.Checkbutton(left, text="Weapon guaranteed desired", variable=self.weapon_guaranteed)\
            .grid(row=7, column=0, columnspan=2, sticky="w", **pad)

        ttk.Button(left, text="Calculate", command=self.calculate)\
            .grid(row=8, column=0, columnspan=2, sticky="ew", padx=10, pady=14)

        ttk.Button(left, text="Help: how to enter streak", command=self.help)\
            .grid(row=9, column=0, columnspan=2, sticky="ew", padx=10, pady=6)

        ttk.Label(right, text="Results", font=("Segoe UI", 12, "bold")).grid(row=0, column=0, sticky="w", **pad)
        ttk.Label(right, text="Expected total pulls:").grid(row=1, column=0, sticky="w", **pad)
        ttk.Label(right, textvariable=self.out_pulls, font=("Segoe UI", 11, "bold")).grid(row=1, column=1, **pad)

        ttk.Label(right, text="Expected total primogems:").grid(row=2, column=0, sticky="w", **pad)
        ttk.Label(right, textvariable=self.out_primos, font=("Segoe UI", 11, "bold")).grid(row=2, column=1, **pad)

        ttk.Label(
            right,
            text=("This tool reports the expected number of pulls (an average). "
                  "It does not guarantee you will reach your target within that many pulls."),
            wraplength=320,
            justify="left"
        ).grid(row=3, column=0, columnspan=2, padx=10, pady=18)

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

    def calculate(self):
        try:
            pulls, primos = expected_total_pulls_and_primos(
                self.char_copies.get(),
                self.weapon_copies.get(),
                self.char_guaranteed.get(),
                self.char_streak.get(),
                self.weapon_guaranteed.get()
            )
            self.out_pulls.set(f"{pulls:,.2f}")
            self.out_primos.set(f"{primos:,.0f}")
        except Exception as e:
            messagebox.showerror("Input error", str(e))

if __name__ == "__main__":
    EVGUI().mainloop()
