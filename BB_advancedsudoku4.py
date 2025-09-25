# Braden Burgener
# CA4 - All Strategies (sudoku)
# Primary Algorithms Used - Divide and Conquer, Dynamic Programming
# Extra Credit - Greedy Algorithm (I completed the extra credit)

import random
import string
import copy
import math

# Get what symbols are in the domain given an NxN sudoku puzzle
# ex. 16x16 Domain={1,2,3,4,5,6,7,8,9,A,B,C,D,E,F,G}
def get_symbols(N):
    digits = [str(i) for i in range(1, min(N, 9) + 1)]
    if N > 9:
        letters = [chr(ord('A') + i) for i in range(N - 9)]
        return digits + letters
    return digits

# Generate an NxN puzzle of difficulty 0-2 (‘0’ is easy, ‘1’ is medium, and ‘2’ is hard)
def generate_puzzle(N, difficulty):
    # Generate valide full NxN sudoku solution
    block = int(N**0.5)
    symbols = get_symbols(N)
    # Base pattern fill
    base = [[None]*N for _ in range(N)]
    for r in range(N):
        for c in range(N):
            idx = (block*(r % block) + r // block + c) % N
            base[r][c] = idx
    # Shuffle rows/cols and symbol mapping
    def shuffle_band(lines, band_size):
        # shuffle within each band and shuffle bands
        bands = [lines[i:i+band_size] for i in range(0, len(lines), band_size)]
        for band in bands:
            random.shuffle(band)
        random.shuffle(bands)
        return [row for band in bands for row in band]

    # Shuffle row indices
    row_map = shuffle_band(list(range(N)), block)
    # Shuffle column indices similarly
    col_map = shuffle_band(list(range(N)), block)
    # Symbol permutation
    perm = symbols[:]
    random.shuffle(perm)
    # Build shuffled full solution
    full = [['0']*N for _ in range(N)]
    for r in range(N):
        for c in range(N):
            orig_idx = base[row_map[r]][col_map[c]]
            full[r][c] = perm[orig_idx]
    # Remove pieces of solution (set to 0)
    total = N*N
    if difficulty == 0:
        blanks = total // 4 # 25% removed
    elif difficulty == 1:
        blanks = total // 3 # 33% removed
    else:
        blanks = total // 2 # 50% removed
    positions = list(range(total))
    random.shuffle(positions)
    puzzle = copy.deepcopy(full)
    for pos in positions[:blanks]:
        r, c = divmod(pos, N)
        puzzle[r][c] = '0'
    return puzzle

# Solves NxN sudoku puzzle (S) using strategy C
def BB_advancedsudoku4(S, N, C):
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

    # Fill left-to-right, top-to-bottom, no backtracking
    def greedy(g):
        for i in range(N):
            for j in range(N):
                if g[i][j] == '0':
                    for val in symbols:
                        if is_valid(g, i, j, val):
                            g[i][j] = val
                            break
                    # If no solution can be found based on previous decisions -> get stuck (greedy = no backtracking - pick a path and commit)
                    if g[i][j] == '0':
                        print(f"Greedy stuck at cell ({i},{j})")
                        return g, False
        return g, True

    # Divide and Conquer using backtracking and recursion
    def dac(g):
        # Find empty cell
        loc = find_empty(g)
        # Base case when division of cells are filled
        if not loc:
            return True
        i, j = loc
        
        # Try each symbol of the domain by marking true if it is valid
        # If the solution is not valid, backtrack and try another symbol
        for val in symbols:
            if is_valid(g, i, j, val):
                g[i][j] = val
                # Divide the original problem into a smaller subproblem where g[i][j] is assumed to be solved where the value = val
                if dac(g):
                    return True
                g[i][j] = '0'
        return False

    # Dynamic Programming domain constraint tabulation
    def dp(g):
        # Map all possible values for each 0 value
        dom = {(i,j): set(symbols) if g[i][j]=='0' else {g[i][j]} 
               for i in range(N) for j in range(N)}
        # Eliminate overlapping domain constraints
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
        # if solved end
        if all(g[i][j] != '0' for i in range(N) for j in range(N)):
            return True
        # Use divide and conquer for remaining cells if domain constraints cant reduce
        return dac(g)

    # Check if a cell value is valid given its surrounding matrix
    def is_valid(g, r, c, v):
        # row/col check
        for x in range(N):
            if g[r][x] == v or g[x][c] == v:
                return False
        # box check
        br, bc = (r//b)*b, (c//b)*b
        for ii in range(br, br+b):
            for jj in range(bc, bc+b):
                if g[ii][jj] == v:
                    return False
        return True

    # Call correct function based on C value in BB_advancedsudoku4 function call
    if C == 'greedy':
        sol, ok = greedy(grid)
        return sol
    elif C == 'dac':
        dac(grid)
        return grid
    elif C == 'dp':
        dp(grid)
        return grid
    else:
        raise ValueError(f"'{C}' is not a valid strategy")


# Print matrix R (sudoku result)
def print_sudoku(R, size):
    div = math.sqrt(size)
    print("My awesome program solved your sudoku puzzle! Here is the answer:\n")
    for i,row in enumerate(R):
            line = ' '.join(row)
            if i % div == 0 and i > 1:
                print('-----+------+-----')
                #print('---+---')
            print(line)

# Run functions
def main():
    size = 4 # Size of the sudoku matrix
    approach = 'dp' # ‘greedy’ is for greedy approach, ‘dac’ is for divide and conquer approach, and ‘dp’ is for dynamic programming

    # Generate a sudoku puzzle
    S = generate_puzzle(size, difficulty=2)
    #S = [["3","2","4","0"],["0","1","3","2"],["0","0","2","0"],["2","4","0","3"]]
    #print_sudoku(S, size)
    # Run BB_sudoku on puzzle S
    R = BB_advancedsudoku4(S, N=size, C=approach)

    print_sudoku(R, size)

if __name__ == "__main__":
    main()