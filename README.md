# Option C — Dynamic Routing VRPTW (Benchmark-ready)

This project solves the **Vehicle Routing Problem with Time Windows (VRPTW)** in **Python** and adds a **dynamic re-routing** component for:
- an urgent new customer request,
- a traffic disruption zone that increases travel time.



## Repository structure

- `code/` → Python source code only
- `data/` → place `C101.txt`, `R101.txt`, `RC101.txt` here
- `figures/` → exported figures
- `maps/` → interactive HTML maps
- `rapport_ieee.pdf` → report
- `slides_presentation.pptx` → slides

## Main methods

### 1) Baseline
Greedy nearest-feasible-neighbor dispatch rule.

### 2) OR-Tools
Main optimization layer for VRPTW with:
- capacity constraints,
- time-window constraints,
- guided local search.

### 3) Simulated Annealing
Comparison metaheuristic with:
- swap,
- insert,
- 2-opt,
- exponential cooling,
- strong penalties for lateness and capacity violations.

## Benchmark policy

The project targets the required benchmark families:
- `C1` → `C101.txt`
- `R1` → `R101.txt`
- `RC1` → `RC101.txt`

Solomon instances are standard VRPTW benchmark problems, and the 100-customer cases are the canonical versions used in many comparisons. Travel time equals Euclidean distance in these instances.

## How to run

1. Place `C101.txt`, `R101.txt`, and `RC101.txt` inside `data/`
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   cd code
   python main.py
   ```

## Notes

- For a quick demo, set `customer_limit=25` in `main.py`.
