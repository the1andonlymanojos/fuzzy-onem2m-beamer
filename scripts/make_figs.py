"""Draws every generated figure in figs/gen/ from flc.py and the paper's Table III.

    python3 scripts/make_figs.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager
import numpy as np

sys.path.insert(0, os.path.dirname(__file__))
import flc  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "figs", "gen")
os.makedirs(OUT, exist_ok=True)

# Series colours, fixed per entity across every chart (validated for CVD).
BLUE, ORANGE, TEAL = "#1E6FB5", "#DB6720", "#2E9C7A"
FLC_C, BASE_C, NORMAL_C = BLUE, ORANGE, TEAL
INK, MUTED, GRID = "#1a2a3b", "#5b6773", "#d9d6cf"
SEQ = ["#9cc3e6", "#4a8fcc", "#14507f"]  # L / M / H, one hue light -> dark

if any("TeX Gyre Heros" in f.name for f in font_manager.fontManager.ttflist):
    plt.rcParams["font.family"] = "TeX Gyre Heros"
plt.rcParams.update({
    "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": MUTED,
    "ytick.color": MUTED, "text.color": INK, "axes.spines.top": False,
    "axes.spines.right": False, "axes.grid": True, "grid.color": GRID,
    "grid.linewidth": 0.6, "axes.axisbelow": True, "font.size": 11,
    "lines.linewidth": 2, "savefig.transparent": True, "pdf.fonttype": 3,
})


def save(fig, name):
    fig.savefig(os.path.join(OUT, name), bbox_inches="tight")
    plt.close(fig)


def mf_panel(ax, mfs, top, unit, label, scale=1.0, marker=None):
    xs = np.linspace(0, top, 600)
    for (term, f), col in zip(mfs.items(), SEQ):
        ys = [f(x) for x in xs]
        ax.plot(xs / scale, ys, color=col)
        peak = xs[int(np.argmax(ys))] if term != "M" else top / 2
        ax.text(min(max(peak, top * 0.08), top * 0.92) / scale, 1.06, term,
                ha="center", color=INK, fontsize=11, fontweight="bold")
    if marker is not None:
        ax.axvline(marker / scale, color=ORANGE, lw=1.6, ls="--")
        for f, col in zip(mfs.values(), SEQ):
            v = f(marker)
            if v > 0:
                ax.plot([marker / scale], [v], "o", ms=8, color=col, mec="white", mew=2)
                ax.text(marker / scale + top * 0.025 / scale, v - 0.05, f"{v:.2f}", fontsize=10, color=INK)
    ax.set_ylim(0, 1.18)
    ax.set_yticks([0, 0.5, 1])
    ax.set_xlim(0, top / scale)
    ax.set_xlabel(f"{label} ({unit})")
    ax.grid(axis="x", visible=False)


def fig_mf(marker=None, name="mf_inputs.pdf"):
    fig, axs = plt.subplots(1, 3, figsize=(11, 2.8))
    m = marker or (None, None, None)
    mf_panel(axs[0], flc.MF_CPU, 100, "%", "CPU  $x_1$", marker=m[0])
    mf_panel(axs[1], flc.MF_RTT, flc.T_MAX, "s", "RTT  $x_2$", scale=1000, marker=m[1])
    mf_panel(axs[2], flc.MF_TR, flc.R_MAX, "msg/s", "Traffic  $x_3$", marker=m[2])
    axs[0].set_ylabel("membership $\\mu$")
    fig.tight_layout()
    save(fig, name)


def fig_output():
    fig, ax = plt.subplots(figsize=(5.5, 2.4))
    for (term, v) in flc.OUT.items():
        ax.vlines(v, 0, 1, color=BLUE, lw=3)
        ax.plot([v], [1], "o", color=BLUE, ms=9, mec="white", mew=2)
        ax.text(v, 1.1, f"{term}\n{v:g}", ha="center", va="bottom", fontweight="bold", linespacing=1.3)
    ax.set_xlim(-0.08, 1.08)
    ax.set_ylim(0, 1.5)
    ax.set_xticks([])
    ax.set_yticks([0, 1])
    ax.set_xlabel("$\\alpha$ = share of traffic sent to the cloud", labelpad=6)
    ax.grid(False)
    save(fig, "mf_output.pdf")


def fig_surface():
    cpu = np.linspace(0, 100, 121)
    rtt = np.linspace(0, flc.T_MAX, 121)
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.6), sharey=True)
    for ax, tr, lbl in zip(axs, (100, 500, 900), ("low", "medium", "high")):
        Z = np.array([[flc.infer(c, r, tr) for c in cpu] for r in rtt])
        im = ax.imshow(Z, origin="lower", extent=(0, 100, 0, 10), aspect="auto",
                       cmap="Blues", vmin=0, vmax=1)
        cs = ax.contour(cpu, rtt / 1000, Z, levels=[0.2, 0.5, 0.8], colors="white", linewidths=1)
        ax.clabel(cs, fmt="%.1f", fontsize=9)
        ax.set_title(f"traffic {lbl} ({tr} msg/s)", fontsize=11)
        ax.set_xlabel("CPU (%)")
        ax.grid(False)
    axs[0].set_ylabel("RTT (s)")
    cb = fig.colorbar(im, ax=axs, fraction=0.025, pad=0.02)
    cb.set_label("$\\alpha$ (offload share)")
    save(fig, "control_surface.pdf")


def fig_slices():
    """One input sweeps 0 -> max while the other two sit at 'Low'. Principle (ii)."""
    t = np.linspace(0, 1, 300)
    fig, ax = plt.subplots(figsize=(6.2, 3.3))
    ax.plot(t * 100, [flc.infer(x * 100, 1000, 100) for x in t], color=BLUE, label="CPU alone")
    # RTT alone and traffic alone give the same curve (rules 7 and 3 are both L)
    ax.plot(t * 100, [flc.infer(10, x * flc.T_MAX, 100) for x in t], color=ORANGE, ls="--", label="RTT alone, or traffic alone")
    ax.plot(t * 100, [flc.infer(x * 100, x * flc.T_MAX, x * flc.R_MAX) for x in t], color=INK, lw=2.5,
            label="all three together")
    ax.axhline(0.5, color=MUTED, lw=1, ls="-.")
    ax.text(2, 0.53, "M level (0.5)", color=MUTED, fontsize=9)
    ax.set_ylim(-0.03, 1.05)
    ax.set_xlabel("stressed input, % of its range")
    ax.set_ylabel("$\\alpha$")
    ax.legend(frameon=False, fontsize=9, loc="upper left", bbox_to_anchor=(0.0, 0.95))
    save(fig, "alpha_slices.pdf")


def simulate():
    """Illustrative closed-loop run (ours, not the paper's data): load ramps up, holds, ramps down."""
    rng = np.random.default_rng(7)
    dt, T = 5, 600
    ts = np.arange(0, T, dt)
    load = np.interp(ts, [0, 120, 240, 420, 540, 600], [150, 150, 950, 950, 250, 250])
    load = load * (1 + 0.08 * rng.standard_normal(len(ts)))

    state = {}

    def plant(a, r):
        # first-order lag: queues drain and fill over a few cycles, not instantly
        local = (1 - a) * r
        tgt = np.array([12 + 0.075 * local, 1500 + 7.5 * local])
        cur = state.get("x", tgt)
        cur = cur + 0.3 * (tgt - cur)
        state["x"] = cur
        cpu = cur[0] + 2 * rng.standard_normal()
        rtt = cur[1] + 200 * rng.standard_normal()
        return float(np.clip(cpu, 0, 100)), float(np.clip(rtt, 0, flc.T_MAX))

    res = {}
    # static threshold: 100 % to cloud above 70 % CPU, back below 50 %
    a, out = 0.0, []
    state.clear()
    for r in load:
        cpu, rtt = plant(a, r)
        a = 1.0 if cpu > 70 else (0.0 if cpu < 50 else a)
        out.append(a)
    res["static"] = np.array(out)
    # FLC with EMA (beta = 0.6) and hysteresis |d alpha| >= 0.05
    a, out, ema = 0.0, [], None
    state.clear()
    for r in load:
        cpu, rtt = plant(a, r)
        x = np.array([cpu, rtt, r])
        ema = x if ema is None else 0.6 * x + 0.4 * ema
        new = flc.infer(*ema)
        if abs(new - a) >= 0.05:
            a = new
        out.append(a)
    res["flc"] = np.array(out)
    return ts, load, res


def fig_sim():
    ts, load, res = simulate()
    fig, (ax0, ax1) = plt.subplots(2, 1, figsize=(8, 4.4), sharex=True, gridspec_kw={"height_ratios": [1, 2]})
    ax0.fill_between(ts, load, color=GRID, lw=0)
    ax0.plot(ts, load, color=MUTED, lw=1.2)
    ax0.set_ylabel("msg/s")
    ax0.set_title("incoming traffic (synthetic)", fontsize=10, loc="left", color=MUTED)
    ax1.step(ts, res["static"], where="post", color=BASE_C, lw=1.8, label="static threshold (70 / 50 % CPU)")
    ax1.plot(ts, res["flc"], color=FLC_C, lw=2.4, label="fuzzy controller")
    ax1.set_ylabel("$\\alpha$ (cloud share)")
    ax1.set_xlabel("time (s)")
    ax1.set_ylim(-0.05, 1.12)
    ax1.legend(frameon=False, fontsize=9, loc="upper left", ncol=2)
    fig.tight_layout()
    save(fig, "sim_static_vs_flc.pdf")


# Table III of the paper
SCEN = ["Normal", "Overloaded", "MAPE-K + FLC"]
SCEN_C = [NORMAL_C, BASE_C, FLC_C]
METRICS = [("Avg. RTT (s)", [3.25, 8.50, 3.75], "lower is better"),
           ("Success rate (%)", [95.0, 77.5, 92.5], "higher is better"),
           ("Avg. CPU (%)", [42.5, 82.5, 45.0], "lower is better")]


def fig_results():
    fig, axs = plt.subplots(1, 3, figsize=(11, 3.4))
    for ax, (name, vals, hint) in zip(axs, METRICS):
        bars = ax.bar(SCEN, vals, color=SCEN_C, width=0.62, edgecolor="white", linewidth=2)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v * 1.02, f"{v:g}", ha="center", va="bottom",
                    fontsize=12, fontweight="bold")
        ax.set_title(f"{name}\n", fontsize=12, fontweight="bold")
        ax.text(0.5, 1.02, hint, transform=ax.transAxes, ha="center", fontsize=9, color=MUTED)
        ax.set_ylim(0, max(vals) * 1.2)
        ax.grid(axis="x", visible=False)
        ax.tick_params(axis="x", labelsize=9)
    fig.tight_layout()
    save(fig, "results_bars.pdf")


def fig_cost():
    regimes = ["Light", "Medium", "Heavy", "Peak"]
    base = [0.5417] * 4
    fuzzy = [0.5417, 0.3575, 0.5583, 0.3033]
    x = np.arange(4)
    w = 0.36
    fig, ax = plt.subplots(figsize=(7, 3.3))
    ax.bar(x - w / 2 - 0.01, base, w, color=BASE_C, label="no management", edgecolor="white", linewidth=2)
    ax.bar(x + w / 2 + 0.01, fuzzy, w, color=FLC_C, label="fuzzy controller", edgecolor="white", linewidth=2)
    for i, (b, f) in enumerate(zip(base, fuzzy)):
        d = (f - b) / b * 100
        txt = "same" if abs(d) < 0.5 else f"{d:+.0f}%"
        ax.text(i + w / 2, f + 0.012, txt, ha="center", fontsize=10, fontweight="bold")
    ax.set_xticks(x, regimes)
    ax.set_ylabel("USD per hour")
    ax.set_ylim(0, 0.68)
    ax.grid(axis="x", visible=False)
    ax.legend(frameon=False, fontsize=9, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.12))
    save(fig, "cost_regimes.pdf")


if __name__ == "__main__":
    fig_mf()
    fig_mf(marker=(70, 5000, 650), name="mf_example.pdf")
    fig_output()
    fig_surface()
    fig_slices()
    fig_sim()
    fig_results()
    fig_cost()
    print("wrote", sorted(os.listdir(OUT)))
