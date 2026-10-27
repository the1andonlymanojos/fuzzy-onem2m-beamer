"""Reimplementation of the paper's fuzzy logic controller (Sec. III-E, Table I).

Inputs:  x1 = CPU (%), x2 = RTT (ms), x3 = traffic rate (msg/s)
Output:  alpha in [0, 1], the share of traffic offloaded to the cloud.

Run `python3 scripts/flc.py` to print a worked example and the rule table.
`make_figs.py` imports this module to draw the generated figures.
"""

T_MAX = 10_000.0  # ms (10 s)
R_MAX = 1_000.0   # msg/s

# Output singletons, Sec. III-E
OUT = {"VL": 0.0, "L": 0.2, "M": 0.5, "H": 0.8, "VH": 1.0}


def trap(x, a, b, c, d):
    """Trapezoid of eq. (1); a == b or c == d degenerates that side to a step."""
    left = 1.0 if b == a else (x - a) / (b - a)
    right = 1.0 if d == c else (d - x) / (d - c)
    if x < a or x > d:
        return 0.0
    return max(min(left, 1.0, right), 0.0)


def _three_terms(top):
    """L / M / H over [0, top], breakpoints at 20/40/60/80 % of the range (eqs. 3-11)."""
    p = [top * f for f in (0.0, 0.2, 0.4, 0.6, 0.8, 1.0)]
    return {
        "L": lambda x: trap(x, p[0], p[0], p[1], p[2]),
        "M": lambda x: trap(x, p[1], p[2], p[3], p[4]),
        "H": lambda x: trap(x, p[3], p[4], p[5], p[5]),
    }


MF_CPU = _three_terms(100.0)
MF_RTT = _three_terms(T_MAX)
MF_TR = _three_terms(R_MAX)

# Table I, rules 1..27 in order (CPU, RTT, Traffic) -> alpha term
RULES = [
    ("L", "L", "L", "VL"), ("L", "L", "M", "VL"), ("L", "L", "H", "L"),
    ("L", "M", "L", "VL"), ("L", "M", "M", "L"), ("L", "M", "H", "M"),
    ("L", "H", "L", "L"), ("L", "H", "M", "M"), ("L", "H", "H", "H"),
    ("M", "L", "L", "L"), ("M", "L", "M", "L"), ("M", "L", "H", "M"),
    ("M", "M", "L", "L"), ("M", "M", "M", "M"), ("M", "M", "H", "H"),
    ("M", "H", "L", "M"), ("M", "H", "M", "H"), ("M", "H", "H", "VH"),
    ("H", "L", "L", "M"), ("H", "L", "M", "H"), ("H", "L", "H", "VH"),
    ("H", "M", "L", "H"), ("H", "M", "M", "VH"), ("H", "M", "H", "VH"),
    ("H", "H", "L", "VH"), ("H", "H", "M", "VH"), ("H", "H", "H", "VH"),
]


def fuzzify(cpu, rtt, tr):
    return (
        {k: f(cpu) for k, f in MF_CPU.items()},
        {k: f(rtt) for k, f in MF_RTT.items()},
        {k: f(tr) for k, f in MF_TR.items()},
    )


def infer(cpu, rtt, tr, trace=False):
    """Mamdani min-max inference over the singletons, then centroid (eq. 13)."""
    mc, mr, mt = fuzzify(cpu, rtt, tr)
    agg = {k: 0.0 for k in OUT}
    fired = []
    for i, (a, b, c, d) in enumerate(RULES, 1):
        w = min(mc[a], mr[b], mt[c])          # Zadeh AND, eq. (12)
        if w > 0:
            fired.append((i, a, b, c, d, w))
        agg[d] = max(agg[d], w)               # max aggregation per output term
    den = sum(agg.values())
    alpha = sum(OUT[k] * agg[k] for k in OUT) / den if den else 0.0
    if trace:
        return alpha, (mc, mr, mt), fired, agg
    return alpha


if __name__ == "__main__":
    for name, x in [("calm", (25, 2000, 150)), ("example", (70, 5000, 650)), ("peak", (85, 8500, 1000))]:
        a, mus, fired, agg = infer(*x, trace=True)
        print(f"{name}: CPU={x[0]}%  RTT={x[1] / 1000:g}s  traffic={x[2]} msg/s")
        for lbl, m in zip(("CPU", "RTT", "Tr "), mus):
            print("   ", lbl, {k: round(v, 2) for k, v in m.items() if v})
        for i, a_, b, c, d, w in fired:
            print(f"    rule {i:2d}: {a_} {b} {c} -> {d:2s}  w={w:.2f}")
        print("    aggregated:", {k: round(v, 2) for k, v in agg.items() if v})
        print(f"    alpha = {a:.3f}\n")
