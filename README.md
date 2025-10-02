# Analysis of All Strategies

## Goals
The main goal of this assignment was to utilize my understanding of greedy, divide & conquer, and dynamic programming algorithms to solve sudoku puzzles[cite: 3]. For my main project, I created a divide & conquer and dynamic programming solution[cite: 4]. For the extra credit, I also created a greedy algorithm[cite: 5].

***

## Computer Specifications
* **Computer Model**: Custom Build [cite: 7]
* **OS**: Windows 11 [cite: 8]
* **Software Information**: Python 3.11 – VSCode [cite: 9]
* **CPU**: AMD Ryzen 7 7800X3D 8-Cores 16-Logical Processors @ 5.00 GHz [cite: 10]
* **Memory**: 32 GB RAM [cite: 11]

***

## Algorithms

### Greedy
My first algorithm was a greedy algorithm that processes inputs by assuming the local optimal solution is the best for each location within the sudoku table (left to right + top to bottom)[cite: 14]. It iterates through each grid location and assigns the lowest possible valid number[cite: 15]. Because it's a greedy algorithm, it commits to decisions without backtracking, which often results in an inability to complete the puzzle because an early choice makes later spaces impossible to fill[cite: 16]. The time complexity is $O(N^3)$, where N is the side length of the grid, because it loops through $N \times N$ spaces and performs up to $3N$ checks for each[cite: 17, 18]. The space complexity is $O(N^2)$ for the $N \times N$ grid[cite: 19].

### Divide & Conquer
My divide & conquer approach recursively divides the problem into N subproblems, solving one at a time and backtracking when no values work for a given path[cite: 21].

![Visual of Divide & Conquer](figure1.png)
*Figure 1: Visual of Divide & Conquer [cite: 22]*

In the worst-case scenario, the time complexity is $O(N!)$, where N is the number of blank spaces[cite: 23]. This occurs because each of the N blank spaces can branch into N new trees, which then branch N-1 times, and so on[cite: 24, 25]. The space complexity is $O(N^2)$ because the memory required scales with the size of the $N \times N$ matrix that must be stored[cite: 26, 27].

### Dynamic Programming
My dynamic programming approach first determines the domain of all possible valid values for each empty cell[cite: 29]. It then stores these overlapping subproblems, iteratively filling in cells that have only one possibility and using that information to eliminate possibilities from other related cells[cite: 29, 30]. The worst-case time complexity is $O(N^4)$[cite: 33]. This is derived from updating domains for $N^2$ locations, where each removal requires updating the row, column, and block, an $O(N)$ operation[cite: 31, 32]. The worst-case space complexity is $O(N^3)$, as it requires storing N possible elements for each of the $N^2$ cells[cite: 34, 35].

***

## Program
The program consists of a high-level function `BB_sudoku4` which simply calls `BB_advancedsudoku4` with a fixed grid size of N=9[cite: 37]. The `BB_advancedsudoku4` function takes an input puzzle, its size, and the chosen solution method[cite: 39]. It then passes the puzzle to the selected algorithm (Greedy, Divide & Conquer, or Dynamic Programming) and returns the solved 2D list[cite: 40]. The program also includes helper functions to generate and print puzzles[cite: 41].

![Block Diagram](figure2.png)
*Figure 2: Block Diagram [cite: 42]*

### Pseudocode:
```
FUNCTION BB_advancedsudoku4(S, N, C):
    Symbols <- get_symbols_in_domain(N)
    Grid <- deep copy of S
    B <- sqrt(N)
    
    FUNCTION find_empty(g):
        FOR each row i from 0 to N-1:
            FOR each col j from 0 to N-1:
                IF g[i][j]=='0': return (i,j)
        Return none

    FUNCTION is_valid(g, r, c, v):
        FOR k from 0 to N-1
            IF value is not valid: return False
        Return True

    FUNCTION greedy(g):
        FOR each blank cell (i,j):
            Assign first valid symbol
        If nothing fits: return (g, False)
        Return (g, True)

    FUNCTION dac(g):
        Pos <- find_empty(g)
        IF pos is None: return True
        FOR each symbol v in symbols:
            IF is_valid: set g[pos]=v, recurse, undo if failed
        Return False

    FUNCTION dp(g):
        Init dom[(i,j)] = symbols or given element
        While domain doesn’t change
            FOR each domain of size 1, remove value from domain in row/col/block
        Write values we know
        IF grid is solved: return True
        ELSE: return dac(g)

    SWITCH C:
        Pick correct method of solving
    Return R

FUNCTION BB_sudoku4(S, D, C):
    BB_advancedsudoku4(S, N=9, C)
    Return R
```
*[cite: 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80]*

***

## Experiment 1
In this experiment, I compared the time and memory usage of each algorithm on a 9x9 grid as the puzzle difficulty (number of blank spaces) increased[cite: 82, 83].

![Time vs Difficulty](figure3.png)
*Figure 3: Time vs Difficulty [cite: 84]*

The dynamic programming (dp) approach's runtime remains constant because it doesn't depend on the number of blank spaces[cite: 85, 86]. The greedy algorithm appears to get faster with harder puzzles, but this is only because it fails and gives up sooner[cite: 87, 88]. The divide & conquer (dac) algorithm's time increases with difficulty, which is expected as its complexity is directly related to the number of blank spaces to solve[cite: 89].

![Memory vs Difficulty](figure4.png)
*Figure 4: Memory vs Difficulty [cite: 92]*

As predicted by their space complexities, the greedy and dac algorithms scale at a rate of $O(N^2)$[cite: 94]. The dp algorithm's memory usage increases much faster, reflecting its $O(N^3)$ space complexity, which is due to storing a domain of possible values for each cell[cite: 95, 96].

***

## Experiment 2
This experiment measured how solve time and memory usage changed as the puzzle size (N) increased, using "easy" puzzles (25% of cells removed) for all tests[cite: 98, 99].

![Time vs Puzzle Size](figure5.png)
*Figure 5: Time vs Puzzle Size [cite: 100]*

The greedy algorithm's time stayed constant because it failed more often as the size increased[cite: 101, 102]. The dac algorithm's time increased with the number of blank spaces, as expected[cite: 103]. The dp approach's runtime scaled proportionally to $O(N^4)$[cite: 103].

![Memory vs Puzzle Size](figure6.png)
*Figure 6: Memory vs Puzzle Size [cite: 104]*

Again, the memory usage for greedy and dac scaled at $O(N^2)$[cite: 105]. The dp algorithm required significantly more memory, scaling at $O(N^3)$ because it stores up to N possible values for each of the $N \times N$ cells[cite: 106, 107].

***

## Experiment 3
This experiment tested the success rate of each algorithm over 1000 runs on easy puzzles of sizes N=4, 9, and 16[cite: 109, 110].

![Success Rate vs Puzzle Size](figure7.png)
*Figure 7: Success Rate vs Puzzle Size [cite: 111]*

The divide & conquer and dynamic programming approaches both achieved a 100% success rate[cite: 112]. The greedy algorithm's performance plummeted as puzzle size increased, starting at 98.2% for N=4 and dropping to just 4.8% for N=16[cite: 113]. With a larger domain of possible numbers, the greedy algorithm is more likely to make an early incorrect choice it cannot backtrack from, causing it to fail[cite: 115, 116, 117].

***

## Conclusion
The experiments showed that while greedy and divide & conquer algorithms perform well on very small Sudoku grids, their effectiveness quickly diminishes[cite: 119]. The greedy algorithm's accuracy drops sharply as grid size increases[cite: 120]. The divide & conquer algorithm's $O(N!)$ time complexity makes it too slow for larger puzzles or those with many blank spaces[cite: 121].

Although the dynamic programming approach appeared slower and more memory-intensive in many tests, the results demonstrate that it is the far superior method for larger, more complex problems[cite: 122]. Its ability to always find a solution makes it more reliable than the greedy approach, and its predictable time complexity makes it more scalable than the divide & conquer method[cite: 123].