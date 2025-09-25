# 
#
# 

"""
FL_sudoku4 and FL_advancedsudoku4

Primary strategy: Divide & Conquer (backtracking)  # main rubric
Extra credit strategies: Greedy (no backtracking), Dynamic Programming (constraint propagation)

Functions:
  - read_puzzle(file_path, N)
  - write_puzzle(grid, file_path)
  - generate_full_solution(N): returns a filled grid via D&C
  - generate_puzzle(N, difficulty): blanks cells based on difficulty
  - FL_advancedsudoku4(S, N, C): solves NxN sudoku using C in {"greedy","dac","dp"}
  - FL_sudoku4(S, D, C): wrapper for N=9, prints difficulty

Assumes S is a list of lists (grid) with '0' for blanks and strings for filled cells.
Author: Braden Burgener
"""
import random
import string
import copy
import sys

# --- File I/O ---
def read_puzzle(file_path, N):
    """Read a puzzle from a text file into an NxN grid (strings)."""
    grid = []
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip().split()
            if not line:
                continue
            if len(line) != N:
                raise ValueError(f"Expected {N} entries per row, got {len(line)}")
            grid.append(line)
    if len(grid) != N:
        raise ValueError(f"Expected {N} rows, got {len(grid)}")
    return grid


def write_puzzle(grid, file_path):
    """Write an NxN grid to a text file."""
    with open(file_path, 'w') as f:
        for row in grid:
            f.write(' '.join(row) + '\n')

# --- Helper to get domain symbols ---
def get_symbols(N):
    digits = list(map(str, range(1, min(N, 10) + 1)))
    if N > 9:
        letters = list(string.ascii_uppercase[:N - 9])
        return digits + letters
    return digits

# --- Puzzle generation ---
def generate_full_solution(N):
    """Generate a full NxN sudoku solution via backtracking."""
    symbols = get_symbols(N)
    grid = [['0'] * N for _ in range(N)]
    def is_valid(grid, r, c, val):
        # row/col
        for i in range(N):
            if grid[r][i] == val or grid[i][c] == val:
                return False
        # sub-box
        b = int(N**0.5)
        br, bc = (r//b)*b, (c//b)*b
        for i in range(br, br+b):
            for j in range(bc, bc+b):
                if grid[i][j] == val:
                    return False
        return True

    def fill_cell(idx=0):
        if idx == N*N:
            return True
        r, c = divmod(idx, N)
        random.shuffle(symbols)
        for val in symbols:
            if is_valid(grid, r, c, val):
                grid[r][c] = val
                if fill_cell(idx+1):
                    return True
                grid[r][c] = '0'
        return False
    fill_cell()
    return grid


def generate_puzzle(N, difficulty):
    """Generate a puzzle by removing cells from a full solution.
    difficulty in {0:easy,1:medium,2:hard} determines removal count."""
    full = generate_full_solution(N)
    total = N*N
    # set blanks count by difficulty
    if difficulty == 0:
        blanks = total // 4
    elif difficulty == 1:
        blanks = total // 3
    else:
        blanks = total // 2
    puzzle = copy.deepcopy(full)
    positions = list(range(total))
    random.shuffle(positions)
    for pos in positions[:blanks]:
        r, c = divmod(pos, N)
        puzzle[r][c] = '0'
    return puzzle

# --- Solver strategies ---

def BB_advancedsudoku4(S, N, C):
    """Solve NxN Sudoku using strategy C: 'greedy', 'dac', or 'dp'."""
    symbols = get_symbols(N)
    grid = copy.deepcopy(S)
    b = int(N**0.5)

    def find_empty(g):
        for i in range(N):
            for j in range(N):
                if g[i][j] == '0':
                    return i, j
        return None

    # Greedy: fill left-to-right, top-to-bottom, no backtracking
    def solve_greedy(g):
        for i in range(N):
            for j in range(N):
                if g[i][j] == '0':
                    for val in symbols:
                        if is_valid(g, i, j, val):
                            g[i][j] = val
                            break
                    if g[i][j] == '0':
                        print(f"Greedy stuck at cell ({i},{j})")
                        return g, False
        return g, True

    # Divide & Conquer: backtracking recursion (primary)
    def solve_dac(g):
        loc = find_empty(g)
        if not loc:
            return True
        i, j = loc
        for val in symbols:
            if is_valid(g, i, j, val):
                g[i][j] = val
                if solve_dac(g):
                    return True
                g[i][j] = '0'
        return False

    # DP: constraint propagation with fallback to recursion
    def solve_dp(g):
        # domains: dict (i,j)->set of possible symbols
        dom = {(i,j): set(symbols) if g[i][j]=='0' else {g[i][j]} 
               for i in range(N) for j in range(N)}
        changed = True
        while changed:
            changed = False
            for (i,j),dset in dom.items():
                if len(dset) == 1:
                    val = next(iter(dset))
                    # eliminate this from peers
                    for k in range(N):
                        if (i,k)!= (i,j) and val in dom[(i,k)]:
                            dom[(i,k)].discard(val); changed=True
                        if (k,j)!= (i,j) and val in dom[(k,j)]:
                            dom[(k,j)].discard(val); changed=True
                    # box
                    br, bc = (i//b)*b, (j//b)*b
                    for ii in range(br, br+b):
                        for jj in range(bc, bc+b):
                            if (ii,jj)!=(i,j) and val in dom[(ii,jj)]:
                                dom[(ii,jj)].discard(val); changed=True
        # build back to grid
        for (i,j),dset in dom.items():
            if not dset:
                return False
            if len(dset)==1:
                g[i][j] = next(iter(dset))
        # if solved
        if all(g[i][j] != '0' for i in range(N) for j in range(N)):
            return True
        # fallback: use DAC on remaining
        return solve_dac(g)

    # validity checker
    def is_valid(g, r, c, v):
        # row/col
        for x in range(N):
            if g[r][x] == v or g[x][c] == v:
                return False
        # box
        br, bc = (r//b)*b, (c//b)*b
        for ii in range(br, br+b):
            for jj in range(bc, bc+b):
                if g[ii][jj] == v:
                    return False
        return True

    # dispatch
    if C == 'greedy':
        sol, ok = solve_greedy(grid)
        return sol
    elif C == 'dac':
        solve_dac(grid)
        return grid
    elif C == 'dp':
        solve_dp(grid)
        return grid
    else:
        raise ValueError(f"'{C}' is not a valid strategy")


def BB_sudoku4(S, D, C):
    # Ensure S is of size 9x9
    if len(S) != 9 or len(S[0]) != 9:
        raise ValueError("BB_sudoku4 only supports 9x9 puzzles.")
    print(f"Solving a difficulty {D} Sudoku (0=easy,1=med,2=hard) using {C}...")
    solution = BB_advancedsudoku4(S, 9, C)
    
    return solution

# Run functions
def main():
    difficulty = 0 # ‘0’ is easy, ‘1’ is medium, and ‘2’ is hard
    approach = 'dp' # ‘greedy’ is for greedy approach, ‘dac’ is for divide and conquer approach, and ‘dp’ is for dynamic programming

    # Generate a sadoku puzzle
    # sadoku = generate_puzzle(9, difficulty=2)
    # write_puzzle(sadoku, 'puzzle9x9.txt')
    # S = read_puzzle('puzzle9x9.txt', 9)
    S = generate_puzzle(9, difficulty=2)
    
    R = BB_sudoku4(S, D=difficulty, C=approach)

    print("My awesome program solved your sudoku puzzle! Here is the answer:\n")
    for i,row in enumerate(R):
            line = ' '.join(row)
            if i in (3,6):
                print('-----+------+-----')
            print(line)

if __name__ == "__main__":
    main()