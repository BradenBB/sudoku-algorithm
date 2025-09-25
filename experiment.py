# sudoku_experiments.py
# --------------------------------------
# Self-contained script to:
#   1. Generate Sudoku puzzles (4×4, 9×9, 16×16) at easy/med/hard.
#   2. Solve them with three strategies: greedy, dac, dp.
#   3. Measure solve time and peak memory usage via tracemalloc.
#   4. Run a 4×4 greedy‐success experiment (1000 runs).
#   5. Measure success percentage vs puzzle size (4,9,16).
#   6. Save timing/memory/success results to CSV, print markdown tables, and plot graphs.
#
# Usage:
#   pip install pandas matplotlib
#   python sudoku_experiments.py

import time
import random
import copy
import tracemalloc
import pandas as pd
import matplotlib.pyplot as plt

# --- Helper: symbol domain ---

def get_symbols(N):
    """
    Return valid symbols for an N×N Sudoku:
      - '1'..'9' for N ≤ 9
      - then 'A','B',… for N > 9
    """
    digits = [str(i) for i in range(1, min(N, 9) + 1)]
    if N > 9:
        letters = [chr(ord('A') + i) for i in range(N - 9)]
        return digits + letters
    return digits

# --- Puzzle generator (pattern-based) ---

def generate_puzzle(N, difficulty):
    """
    Generate an N×N Sudoku puzzle without backtracking:
      1. Fill with a math pattern.
      2. Shuffle rows/cols and symbols.
      3. Remove blanks based on difficulty (0:25%, 1:33%, 2:50%).
    """
    b = int(N**0.5)
    symbols = get_symbols(N)

    # 1) base pattern
    base = [[(b*(r % b) + r//b + c) % N for c in range(N)] for r in range(N)]

    # 2) shuffle rows/cols in bands
    def shuffle_band(lines):
        bands = [lines[i:i+b] for i in range(0, N, b)]
        for band in bands:
            random.shuffle(band)
        random.shuffle(bands)
        return [x for band in bands for x in band]

    rows = shuffle_band(list(range(N)))
    cols = shuffle_band(list(range(N)))
    perm = symbols[:]
    random.shuffle(perm)

    full = [[perm[base[rows[r]][cols[c]]] for c in range(N)] for r in range(N)]

    # 3) blank out
    total = N*N
    blanks = {0: total//4, 1: total//3, 2: total//2}[difficulty]
    positions = list(range(total))
    random.shuffle(positions)
    puzzle = copy.deepcopy(full)
    for pos in positions[:blanks]:
        puzzle[pos//N][pos%N] = '0'
    return puzzle

# --- Solver: your exact implementations ---

def BB_advancedsudoku4(S, N, C):
    """
    Solve N×N Sudoku S with strategy C ('greedy','dac','dp').
    Returns the solved grid.
    """
    symbols = get_symbols(N)
    grid = copy.deepcopy(S)
    b = int(N**0.5)

    full_mask = (1 << N) - 1
    sym2bit = {sym: 1 << idx for idx, sym in enumerate(symbols)}
    bit2sym = {1 << idx: sym for idx, sym in enumerate(symbols)}

    def find_empty(g):
        for i in range(N):
            for j in range(N):
                if g[i][j] == '0':
                    return i, j
        return None

    def greedy(g):
        for i in range(N):
            for j in range(N):
                if g[i][j] == '0':
                    for val in symbols:
                        if is_valid(g, i, j, val):
                            g[i][j] = val
                            break
                    if g[i][j] == '0':
                        # stuck
                        return g, False
        return g, True

    def dac(g):
        loc = find_empty(g)
        if not loc:
            return True
        i, j = loc
        for val in symbols:
            if is_valid(g, i, j, val):
                g[i][j] = val
                if dac(g):
                    return True
                g[i][j] = '0'
        return False

    def dp(g):
        dom = {
            (i,j): set(symbols) if g[i][j]=='0' else {g[i][j]}
            for i in range(N) for j in range(N)
        }
        changed = True
        while changed:
            changed = False
            for (i,j), dset in dom.items():
                if len(dset) == 1:
                    v = next(iter(dset))
                    for k in range(N):
                        if (i,k)!=(i,j) and v in dom[(i,k)]:
                            dom[(i,k)].discard(v); changed=True
                        if (k,j)!=(i,j) and v in dom[(k,j)]:
                            dom[(k,j)].discard(v); changed=True
                    br, bc = (i//b)*b, (j//b)*b
                    for ii in range(br, br+b):
                        for jj in range(bc, bc+b):
                            if (ii,jj)!=(i,j) and v in dom[(ii,jj)]:
                                dom[(ii,jj)].discard(v); changed=True
        for (i,j), dset in dom.items():
            if not dset:
                return False
            if len(dset)==1 and grid[i][j]=='0':
                g[i][j] = next(iter(dset))
        if all(g[i][j] != '0' for i in range(N) for j in range(N)):
            return True
        return dac(g)

    def is_valid(g, r, c, v):
        for x in range(N):
            if g[r][x]==v or g[x][c]==v:
                return False
        br, bc = (r//b)*b, (c//b)*b
        for ii in range(br, br+b):
            for jj in range(bc, bc+b):
                if g[ii][jj]==v:
                    return False
        return True

    if C == 'greedy':
        sol, _ = greedy(grid)
    elif C == 'dac':
        dac(grid)
        sol = grid
    elif C == 'dp':
        dp(grid)
        sol = grid
    else:
        raise ValueError(f"'{C}' is not valid")
    return sol

# --- Measurement wrapper ---

def measure(puzzle, N, strat):
    """
    Returns (solve_time_seconds, peak_memory_bytes)
    """
    tracemalloc.start()
    t0 = time.perf_counter()
    _ = BB_advancedsudoku4(puzzle, N, strat)
    t1 = time.perf_counter()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return t1 - t0, peak

# --- Main experiments ---

def run_experiments():
    repeats = 5
    strategies = ['greedy','dac','dp']

    # 1) 9×9 by difficulty
    rows_diff = []
    for diff in [0,1,2]:
        for strat in strategies:
            times, mems = [], []
            for _ in range(repeats):
                p = generate_puzzle(9, diff)
                t, m = measure(p, 9, strat)
                times.append(t); mems.append(m)
            rows_diff.append({
                'difficulty': diff,
                'strategy': strat,
                'avg_time_s': sum(times)/repeats,
                'avg_peak_mem_KiB': sum(mems)/repeats/1024
            })
    df_diff = pd.DataFrame(rows_diff)
    df_diff.to_csv('9x9_diff_all_strategies.csv', index=False)
    print("\n### 9×9 Difficulty Results ###\n")
    print(df_diff.to_markdown(index=False))

    # 2) Easy puzzles for sizes 4,9,16
    rows_size = []
    for N in [4,9,16]:
        for strat in strategies:
            times, mems = [], []
            for _ in range(repeats):
                p = generate_puzzle(N, 0)
                t, m = measure(p, N, strat)
                times.append(t); mems.append(m)
            rows_size.append({
                'size': N,
                'strategy': strat,
                'avg_time_s': sum(times)/repeats,
                'avg_peak_mem_KiB': sum(mems)/repeats/1024
            })
    df_size = pd.DataFrame(rows_size)
    df_size.to_csv('size_easy_all_strategies.csv', index=False)
    print("\n### Puzzle Size Results (Easy) ###\n")
    print(df_size.to_markdown(index=False))

    # 3) 4×4 Greedy success rate (1000 runs)
    runs = 1000
    success_4 = 0
    for _ in range(runs):
        p = generate_puzzle(4, 0)
        sol = BB_advancedsudoku4(p, 4, 'greedy')
        if all(sol[i][j] != '0' for i in range(4) for j in range(4)):
            success_4 += 1
    print(f"\nGreedy success on 4×4 (easy) over {runs} runs: {success_4}/{runs} = {success_4/runs*100:.1f}%\n")

    # 4) Success percentage vs puzzle size (4,9,16)
    rows_succ = []
    runs_succ = 500
    for N in [4,9,16]:
        for strat in strategies:
            succ = 0
            for _ in range(runs_succ):
                p = generate_puzzle(N, 0)
                sol = BB_advancedsudoku4(p, N, strat)
                if all(sol[i][j] != '0' for i in range(N) for j in range(N)):
                    succ += 1
            rows_succ.append({
                'size': N,
                'strategy': strat,
                'success_pct': succ / runs_succ * 100
            })
    df_succ = pd.DataFrame(rows_succ)
    df_succ.to_csv('success_pct_by_size.csv', index=False)
    print("\n### Success % by Puzzle Size ###\n")
    print(df_succ.to_markdown(index=False))

    # --- Plots ---
    # 9×9 time & memory
    plt.figure()
    for strat in strategies:
        sub = df_diff[df_diff['strategy']==strat]
        plt.plot(sub['difficulty'], sub['avg_time_s'], 'o-', label=strat)
    plt.xlabel('Difficulty'); plt.ylabel('Avg Time (s)')
    plt.title('9×9 Solve Time by Difficulty'); plt.legend(); plt.grid(); plt.show()

    plt.figure()
    for strat in strategies:
        sub = df_diff[df_diff['strategy']==strat]
        plt.plot(sub['difficulty'], sub['avg_peak_mem_KiB'], 'o-', label=strat)
    plt.xlabel('Difficulty'); plt.ylabel('Avg Peak Memory (KiB)')
    plt.title('9×9 Memory by Difficulty'); plt.legend(); plt.grid(); plt.show()

    # Size time & memory
    plt.figure()
    for strat in strategies:
        sub = df_size[df_size['strategy']==strat]
        plt.plot(sub['size'], sub['avg_time_s'], 'o-', label=strat)
    plt.xlabel('Puzzle Size'); plt.ylabel('Avg Time (s)')
    plt.title('Solve Time vs Puzzle Size'); plt.legend(); plt.grid(); plt.show()

    plt.figure()
    for strat in strategies:
        sub = df_size[df_size['strategy']==strat]
        plt.plot(sub['size'], sub['avg_peak_mem_KiB'], 'o-', label=strat)
    plt.xlabel('Puzzle Size'); plt.ylabel('Avg Peak Memory (KiB)')
    plt.title('Memory vs Puzzle Size'); plt.legend(); plt.grid(); plt.show()

    # Success % vs size
    plt.figure()
    for strat in strategies:
        sub = df_succ[df_succ['strategy']==strat]
        plt.plot(sub['size'], sub['success_pct'], 'o-', label=strat)
    plt.xlabel('Puzzle Size'); plt.ylabel('Success %')
    plt.title('Solver Success Rate vs Puzzle Size')
    plt.ylim(0, 105); plt.legend(); plt.grid(); plt.show()

    print("\nCSV files generated:\n"
          "9x9_diff_all_strategies.csv\n"
          "size_easy_all_strategies.csv\n"
          "success_pct_by_size.csv\n")

if __name__ == "__main__":
    run_experiments()
