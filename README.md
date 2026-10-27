# Fuzzy QoS control in oneM2M: paper presentation

Beamer deck and per-speaker notes for *Fuzzy-Logic-Based QoS Control in oneM2M:
Adaptive Edge-to-Cloud Traffic Offloading* (Zyane & Et-Tousy, FiCloud 2026).

| Part | Speaker | Topic | Slides |
|---|---|---|---|
| 01 | Raj | Introduction, motivation, research gap | 1–9 |
| 02 | Manoj | oneM2M, architecture (Fig. 1–2), MAPE-K | 10–17 |
| 03 | Ashutosh | Fuzzy controller, worked example, testbed + configuration | 18–29 |
| 04 | John | Results, kept deliberately simple | 30–37 |
| 05 | Ayush | Baselines, Table IV, cost check, re-simulation, critique, conclusion | 38–47 |

Part 04 is short and plain on purpose. The harder results material moved out of it:
testbed and controller settings went to Part 03; Fig. 4, Table IV, the cost breakdown
and the AWS pricing went to Part 05.

## Files

- `deck.pdf`: the slides (16:9). Each speaker's part has its own accent colour.
- `notes/notes_0N_<name>.pdf`: speaker notes. A cheat-sheet cover page (job, opening and
  hand-off lines, numbers to know), then every slide as a thumbnail with a script and
  likely questions. John's notes are a near-verbatim script with "redirect" lines for hard questions.
- `scripts/flc.py`: our re-implementation of the paper's 27-rule controller
  (`python3 scripts/flc.py` prints the worked example: CPU 70 %, RTT 5 s, 650 msg/s gives α = 0.76).
- `scripts/make_figs.py`: draws everything in `figs/gen/` (membership functions,
  control surface, the design principles, the closed-loop re-simulation, and the result charts redrawn from Table III).
- `figs/paper/`: figures extracted from the paper.

## Build

Needs LuaLaTeX (TeX Live with the TeX Gyre fonts), Python 3 with matplotlib and numpy.

```bash
make
```

`make` regenerates the figures, compiles the deck twice, then the five notes PDFs
(the notes pull slide thumbnails from `deck.pdf` through `deck.slidemap`).
