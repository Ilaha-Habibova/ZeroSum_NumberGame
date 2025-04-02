# ZeroSum_NumberGame
At the beginning of the game, the number chosen by the human-player(in the range from 8 to 18) is given. Both players have 0 points. Players take turns by multiplying the current number by 2, 3 or 4. If the multiplication results in an even number, then 1 point is deducted from the opponent's score, and if it is an odd number, then 1 point is added to the player's own score . The game ends as soon as a number greater than or equal to 1200 is reached. The player with the highest score wins the game. If the number of points is equal, then the result is a draw. 

## Python file:
- <a href="https://github.com/Ilaha-Habibova/ZeroSum_NumberGame/blob/main/ZeroSum_NumberGame.py">The complete code</a>

# 🏗️ Implementation:
 _1)_ The game was built in Python using object-oriented programming (OOP) principles. The primary data structure for representing each node in our game tree is the GameState class. Each instance of this class stores:
- The current number.
- The scores of both players (human and computer).
- The player whose turn it is.
- A reference to the parent node (previous game state).
- A list of child nodes (possible next moves).
- The depth of the node, starting from 0 for the root node.

The parent node is stored as a reference to the previous game state, allowing us to track the progression of states. Child nodes are stored in a list, which holds all possible next moves. Each time a move is made, a new `GameState` object is created and appended to the children list of the current state. This structure effectively forms a game tree through object references and lists.

Additionally, the `GameState` class includes:
- A heuristic evaluation function (`get_score`), which consists of 2 factors: score difference between human and computer and how close we are to terminal state-1200.
- A terminal check function (`is_terminal`) that determines if the game has reached the end condition (the number is 1200 or greater).

_2)_ `GameHistory` class  was also implemented to store game results. 
Each game result is stored as a dictionary, and all results are written to a `game_history.dat` file also, which includes the game result,the initial number,nodes visited,average time per move by the computer,algorithm used,the starting player,timestamp of the game.
A list of dictionaries is used to store multiple game results efficiently.

_3)_ Tuples are used for returning multiple values from functions (e.g., `return best_move, best_score`). Tuples were chosen because:
- They are immutable, preventing unintended modifications.
- They are memory-efficient compared to lists.

_4)_  2 game tree search algorithms were used for computer move selection:
- Minimax
- Alpha-beta pruning

> # Minimax algorithm
> Minimax algorithm is simple algorithm. It divides the graph into min and max leves. Then it assigns heuristic measures to terminal nodes of sub-graph at our specified depth limit-3. This heuristic measure  only represents the best state which can be reached after 
> making 3 moves from the current state.Minimax algorithm explores all possible nodes in game tree. Therefore it takes more time and use more memory.

Code:

![image](https://github.com/user-attachments/assets/ae436d7b-2465-4d19-acf5-b2f062bd6756)
> Explanation:
> 
> The Minimax function takes current state, depth (3 in our case) and boolen value which indicates whether it is a maximizing node (computer’s turn) or minimizing node (human’s turn). The function counts number of visited nodes for statistics. If we have reached the 
> maximum search depth or terminal state, we stop recursion and get heuristic evaluation of the current node via `get_score()` function. We initialize best score to -infinity for computer to maximize, and +infinity for human to minimize. We loop through all possible 
> moves and generate a new game state via apply_move which is explained before. Then it recursiely call minimax on the new state by reducing the depth and switching the turns(` _ ` are used for discarding the move choices, because we only care about the score here). 
> Later, it checks if current move is better than our previous best move option,update our best move and score,then return best multiplier and its score.

<br>

> # Alpha-beta pruning:
> Alpha-beta pruning is more improved version of Minimax algorithm. Because it doesn’t consider moves which doesn’t have any effect or benefit to the final decision. Although results of Minimax and Alpha-beta pruning is same for move selection, alpha-beta pruning is 
> more efficient in search of state space graph. We observed this in our game experiments also:
> 
> Average time per move by computer are nearly always less in Alpha beta pruning than Minimax algorithms.
> 
> The reason for that is in each experiment, computer visited significantly fewer nodes in Alpha beta algorithm. We achieved this because of `if beta <= alpha: break` in our code for Alpha beta algorithm.

Code:

![image](https://github.com/user-attachments/assets/2a0917d2-9e98-493f-8a20-f6382db110eb)
> Explanation:
> 
> Definition of Alpha-beta is similar to Minimax function, but 2 more parameters-_alpha_ (best value for maximizing player) and _beta_( best value for minimizing player) were introduced. Therefore,the function updates value of alpha to maximum and best score found,while value of beta to minimum and best score found.If beta is less or equal to alpha(same case for alpha and beta cut-off),we don’t explore this branch.
> You can see GameStatistics window,the number of visited nodes for Alpha-beta is significantly lower than Minimax:

![image](https://github.com/user-attachments/assets/e9bb9614-414b-41af-b7a2-808ef43e117e)

>So,the computer makes moves by generating the game tree via `apply_move` function,evaluating terminal nodes with the heuristic `get_score` function, propagating scores up using Minimax or Alpha-beta algorithms.

<br><br>
## Author: [@Ilaha_Habibova](https://github.com/Ilaha-Habibova)
<br>

## © Copyright :

All Rights Reserved.  
Unauthorized use, reproduction, modification, or distribution of this project, in whole or in part is strictly prohibited. Proper reference must be given if any part of this project is used.  








