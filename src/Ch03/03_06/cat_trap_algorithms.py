"""
03_06 - Challenge: Write your own evaluation function!!! 
        
        Go to line 216 for the challenge!

Cat Trap Algorithms

This is the relevant code for the LinkedIn Learning Course 
AI Algorithms for Game Design with Python, by Eduardo Corpeño.

For the GUI, this code uses the Cat Trap UI VSCode extension
included in the extensions folder.
"""

import random
import copy
import time
import numpy as np

# Constants
CAT_TILE = 6
BLOCKED_TILE = 1
EMPTY_TILE = 0
LAST_CALL_MS = 0.5
VERBOSE = True
TIMEOUT = [-1, -1]

class CatTrapGame:
    """
    Represents a Cat Trap game state. Includes methods for managing game state
    and selecting moves for the cat using different AI algorithms.
    """

    size = 0
    start_time = time.time()
    deadline = time.time()
    terminated = False
    max_depth = float('inf')
    reached_max_depth = False
    
    def __init__(self, size):
        self.cat = [size // 2] * 2
        self.hexgrid = np.full((size, size), EMPTY_TILE)
        self.hexgrid[tuple(self.cat)] = CAT_TILE
        CatTrapGame.size = size

    def initialize_random_hexgrid(self):
        """Randomly initialize blocked hexgrid."""
        tiles = CatTrapGame.size ** 2
        num_blocks = random.randint(round(0.067 * tiles), round(0.13 * tiles))
        count = 0
        self.hexgrid[tuple(self.cat)] = CAT_TILE

        while count < num_blocks:
            r = random.randint(0, CatTrapGame.size - 1)
            c = random.randint(0, CatTrapGame.size - 1)
            if self.hexgrid[r, c] == EMPTY_TILE:
                self.hexgrid[r, c] = BLOCKED_TILE
                count += 1    
        if VERBOSE:
            print('\n======= NEW GAME =======')
            self.print_hexgrid()

    def set_hexgrid(self, hexgrid):
        """Copy incoming hexgrid."""
        self.hexgrid = hexgrid
        self.cat = list(np.argwhere(self.hexgrid == CAT_TILE)[0])  # Find the cat
        if VERBOSE:
            print('\n======= NEW GAME =======')
            self.print_hexgrid()
   
    def block_tile(self, coord):
        self.hexgrid[tuple(coord)] = BLOCKED_TILE

    def unblock_tile(self, coord):
        self.hexgrid[tuple(coord)] = EMPTY_TILE

    def place_cat(self, coord):
        self.hexgrid[tuple(coord)] = CAT_TILE
        self.cat = coord

    def move_cat(self, coord):
        self.hexgrid[tuple(self.cat)] = EMPTY_TILE  # Clear previous cat position
        self.place_cat(coord)
    
    def get_cat_moves(self):
        """
        Get a list of valid moves for the cat.
        """
        hexgrid = self.hexgrid
        r, c = self.cat
        n = CatTrapGame.size
        col_offset = r % 2  # Offset for columns based on row parity
        moves = []

        # Directions with column adjustments
        directions = {
            'E': (0, 1),
            'W': (0, -1),
            'NE': (-1, col_offset),
            'NW': (-1, -1 + col_offset),
            'SE': (1, col_offset),
            'SW': (1, -1 + col_offset),
        }

        for dr, dc in directions.values():
            tr, tc = r + dr, c + dc  # Calculate target row and column
            if 0 <= tr < n and 0 <= tc < n and hexgrid[tr, tc] == EMPTY_TILE:
                moves.append([tr, tc])

        return moves

    def apply_move(self, move, cat_turn):
        """
        Apply a move to the game state.
        """
        if self.hexgrid[tuple(move)] != EMPTY_TILE:
            action_str = "move cat to" if cat_turn else "block"
            self.print_hexgrid()
            print('\n=====================================')
            print(f'Attempting to {action_str} {move} = {self.hexgrid[tuple(move)]}')
            print('Invalid Move! Check your code.')
            print('=====================================\n')

        if cat_turn:
            self.move_cat(move)
        else:
            self.hexgrid[tuple(move)] = BLOCKED_TILE

    def time_left(self):
        """
        Calculate the time remaining before the deadline.
        """
        return (CatTrapGame.deadline - time.time()) * 1000
    
    def print_hexgrid(self):
        """
        Print the current state of the game board using special characters.
        """
        tile_map = {
            EMPTY_TILE: ' ⬡',   # Alternative: '-'
            BLOCKED_TILE: ' ⬢', # Alternative: 'X'
            CAT_TILE: '🐈'      # Alternative: 'C'
        }
        for r in range(CatTrapGame.size):
            # Add a leading space for odd rows for staggered effect
            prefix = ' ' if r % 2 != 0 else ''
            row_display = ' '.join(tile_map[cell] for cell in self.hexgrid[r])
            print(prefix + row_display)
        return

    def evaluation(self, cat_turn):
        """
        Evaluation function. 
        Options: 'moves', 'straight_exit', 'custom'.
        """
        evaluation_function = 'custom'

        if evaluation_function == 'moves':
            return self.eval_moves(cat_turn)
        elif evaluation_function == 'straight_exit':
            return self.eval_straight_exit(cat_turn)
        elif evaluation_function == 'custom':
            return self.eval_custom(cat_turn)
        return 0

    def eval_moves(self, cat_turn):
        """
        Evaluate based on the number of valid moves available for the cat.
        """
        cat_moves = self.get_cat_moves()
        return len(cat_moves) if cat_turn else len(cat_moves) - 1

    def get_target_position(self, scout, direction):
        """
        Get the target position based on the specified direction.
        """
        r, c = scout
        col_offset = r % 2  # Offset for columns based on row parity
        
        if direction == 'E':
            return [r, c + 1]
        elif direction == 'W':
            return [r, c - 1]
        elif direction == 'NE':
            return [r - 1, c + col_offset]
        elif direction == 'NW':
            return [r - 1, c - 1 + col_offset]
        elif direction == 'SE':
            return [r + 1, c + col_offset]
        elif direction == 'SW':
            return [r + 1, c - 1 + col_offset]
        return [r, c]

    def eval_straight_exit(self, cat_turn):
        """
        Evaluate the cat's access to the nearest board edge along straight paths.
        """
        distances = []
        directions =  ['E', 'W', 'NE', 'NW', 'SE', 'SW']
        n = CatTrapGame.size
        for dir in directions:
            distance = 0
            r, c = self.cat
            while not (r < 0 or r >= n or c < 0 or c >= n):
                if self.hexgrid[r, c] == BLOCKED_TILE:
                    distance += n # Increase cost for blocked paths
                    break
                distance += 1
                r, c = self.get_target_position([r, c], dir)
            distances.append(distance)

        distances.sort() # Ascending order, so distances[0] is the best
        return CatTrapGame.size - (distances[0] if cat_turn else distances[1])

    def eval_custom(self, cat_turn):
        """
        03_06 - Challenge: Write your own evaluation function 

        Your task is to implement an evaluation function you think may provide 
        a good assessment of how well the game is going for the cat at a 
        specific game state where the depth-limited search algorithm must stop.

        Make sure to take care of the following considerations:
        1) Remove the placeholder code immediately below these instructions.
        2) Read through the skeleton code provided below.
        3) Fill in the blanks following the instructions in the "TODO:" comments.
        4) If you're stuck, you may ask in the course's Q&A or consult the
           solution in the next folder to unblock yourself without spoiling too
           much of the fun.
        """
        # TODO: Remove the following line to enable your evaluation function.
        return 2 if cat_turn else 1

        # Skeleton Code - Custom Evaluation Function
        # HINT: Below is a guide to help you implement your own evaluation
        # logic. You can use or modify this as you see fit.
        # Be creative. These are only suggestions.

        # Initialize a score variable
        score = 0

        # TODO: Count the number of valid moves for the cat.
        # HINT: Use `self.get_cat_moves()` to get the list of moves.
        #       Or use the existing eval_moves() method above.
        move_score = 0  # Replace 0 with the number of valid moves.

        # TODO: Evaluate the proximity of the cat to the board's edge.
        # HINT: Use `self.cat` to calculate the distance.
        #       Or use the existing eval_straight_exit() method above.
        proximity_score = 0  # Replace 0 with your calculation logic.

        # TODO: Incorporate penalties or rewards for specific conditions.
        # Example: Penalize if the cat is not making progress or if it's
        #          not the cat's turn.
        penalty = 0  # Replace with logic for penalties.

        # TODO: Combine all the metrics into the final score.
        # Example: score = move_score + proximity_score - penalty
        # Modify this as you prefer.
        score = move_score + proximity_score - penalty

        return score

    # ===================== Intelligent Agents =====================
    """
    Intelligent Agents for the Cat Trap game. These agents examine the game 
    state, and return the new position of the cat (a move).
    Two special return values for failure may be returned (timeout or trapped).

    Parameters:
      - random_cat: A random move for the cat.
      - minimax: Use the Minimax algorithm.
      - alpha_beta: Use Alpha-Beta Pruning.
      - depth_limited: Use Depth-Limited Search.
      - max_depth: Maximum depth to explore for Depth-Limited Search.
      - iterative_deepening: Use Iterative Deepening.
      - allotted_time: Maximum time in seconds for the cat to respond.

    If no algorithm is selected, the cat gives up (as if trapped).
    """

    def select_cat_move(self, random_cat, minimax, alpha_beta, depth_limited,
                        max_depth, iterative_deepening, allotted_time):
        """Select a move for the cat based on the chosen algorithm."""
        CatTrapGame.start_time = time.time()
        CatTrapGame.deadline = CatTrapGame.start_time + allotted_time
        CatTrapGame.terminated = False
        CatTrapGame.max_depth = float('inf') 
        CatTrapGame.reached_max_depth = False 
        move = self.cat

        if VERBOSE:
            print('\n======= NEW MOVE =======')

        if random_cat:
            move = self.random_cat_move() 
        elif minimax:
            # Select a move using the Minimax algorithm.
            move = self.alpha_beta() if alpha_beta else self.minimax()   
        elif depth_limited:
            # Select a move using Depth-Limited Search.
            CatTrapGame.max_depth = max_depth
            move = self.alpha_beta() if alpha_beta else self.minimax()
        elif iterative_deepening:
            # Select a move using the Iterative Deepening algorithm.
            move = self.iterative_deepening(alpha_beta)

        elapsed_time = (time.time() - CatTrapGame.start_time) * 1000
        if VERBOSE:
            print(f'Elapsed time: {elapsed_time:.3f}ms ')
            print(f'New cat coordinates: {move}')
            temp = copy.deepcopy(self)
            if move != TIMEOUT:
                temp.move_cat(move)
            temp.print_hexgrid()
        return move

    def random_cat_move(self):
        """Randomly select a move for the cat."""
        moves = self.get_cat_moves()
        if moves:
            return random.choice(moves)
        return self.cat

    def max_value(self, depth):
        """
        Calculate the maximum value for the current game in the Minimax algorithm.
        """
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return TIMEOUT, 0
        
        legal_moves = self.get_cat_moves() # Possible directions: E, W, NE, NW, SE, SW
        if not legal_moves:
            max_turns = 2 * (CatTrapGame.size ** 2)
            utility = (max_turns - depth) * (-500) # Utility for cat's defeat 
            return self.cat, utility
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.cat, self.evaluation(cat_turn = True)
        
        best_value = float('-inf')
        best_move = legal_moves[0]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = True)
            value = next_game.min_value(depth + 1)

            if CatTrapGame.terminated:
                return TIMEOUT, 0

            if value > best_value:
                best_value = value
                best_move = move
  
        return best_move, best_value

    def min_value(self, depth):
        """
        Calculate the minimum value for the current game in the Minimax algorithm.

        Unlike max_value, min_value does not iterate over specific 
        directions (E, W, NE, NW, etc.). Instead, it examines every 
        possible free tile on the board.
        """
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return 0

        # Check if terminal state
        r, c = self.cat
        n = CatTrapGame.size
        if (
            r == 0 or r == n - 1 or 
            c == 0 or c == n - 1
        ):
            max_turns = 2 * (CatTrapGame.size ** 2)
            return (max_turns - depth) * (500) # Utility for cat's victory
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.evaluation(cat_turn = False)
        
        best_value = float('inf')

        # Iterate through all legal moves for the player (empty tiles)
        legal_moves = [list(rc) for rc in np.argwhere(self.hexgrid == EMPTY_TILE)]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = False)
            _, value = next_game.max_value(depth + 1)

            if CatTrapGame.terminated:
                return 0
            
            best_value = min(best_value, value)

        return best_value

    def minimax(self):
        """
        Perform the Minimax algorithm to determine the best move.
        """
        best_move, _ = self.max_value(depth = 0) 
        return best_move

    def alpha_beta_max_value(self, alpha, beta, depth):
        """
        Calculate the maximum value for the current game state 
        using Alpha-Beta pruning.
        """
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return TIMEOUT, 0
        
        legal_moves = self.get_cat_moves() # Possible directions: E, W, NE, NW, SE, SW
        if not legal_moves:
            max_turns = 2 * (CatTrapGame.size ** 2)
            utility = (max_turns - depth) * (-500) # Utility for cat's defeat 
            return self.cat, utility
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.cat, self.evaluation(cat_turn = True)
        
        best_value = float('-inf')
        best_move = legal_moves[0]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = True)
            value = next_game.alpha_beta_min_value(alpha, beta, depth + 1)

            if CatTrapGame.terminated:
                return TIMEOUT, 0

            if value > best_value:
                best_value = value
                best_move = move

            if best_value >= beta: # Pruning
                return best_move, best_value
            alpha = max(alpha, best_value)

        return best_move, best_value

    def alpha_beta_min_value(self, alpha, beta, depth):
        """
        Calculate the minimum value for the current game state 
        using Alpha-Beta pruning.

        Unlike max_value, min_value does not iterate over specific 
        directions (E, W, NE, NW, etc.). Instead, it examines every 
        possible free tile on the board.
        """
        if self.time_left() < LAST_CALL_MS:
            CatTrapGame.terminated = True
            return 0

        # Check if terminal state
        r, c = self.cat
        n = CatTrapGame.size
        if (
            r == 0 or r == n - 1 or 
            c == 0 or c == n - 1
        ):
            max_turns = 2 * (CatTrapGame.size ** 2)
            return (max_turns - depth) * (500) # Utility for cat's victory
        
        if depth == CatTrapGame.max_depth:
            CatTrapGame.reached_max_depth = True
            return self.evaluation(cat_turn = False)
        
        best_value = float('inf')

        # Iterate through all legal moves for the player (empty tiles)
        legal_moves = [list(rc) for rc in np.argwhere(self.hexgrid == EMPTY_TILE)]
        for move in legal_moves:
            next_game = copy.deepcopy(self)
            next_game.apply_move(move, cat_turn = False)
            _, value = next_game.alpha_beta_max_value(alpha, beta, depth + 1)

            if CatTrapGame.terminated:
                return 0
            
            best_value = min(best_value, value)

            if best_value <= alpha: # Pruning
                return best_value
            beta = min(beta, best_value)

        return best_value

    def alpha_beta(self):
        """
        Perform the Alpha-Beta pruning algorithm to determine the best move.
        """
        alpha = float('-inf')
        beta = float('inf')
        best_move, _ = self.alpha_beta_max_value(alpha, beta, depth = 0)
        return best_move

    def iterative_deepening(self, alpha_beta):
        """
        Perform iterative deepening search with an option to use Alpha-Beta pruning.
        """
        self.placeholder_warning()
        return self.random_cat_move()

    def placeholder_warning(self):
        signs = '⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️'
        print(f'{signs} {signs}')
        print('                WARNING')
        print('This is a temporary implementation using')
        print("the random algorithm. You're supposed to")
        print('write code to solve a challenge.')
        print('Did you run the wrong version of main.py?')
        print('Double-check its path.')
        print(f'{signs} {signs}')

if __name__ == '__main__':
    signs = '⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️ ⚠️'
    print(f'\n{signs} {signs}')
    print('               WARNING')
    print('You ran cat_trap_algorithms.py')
    print('This file contains the AI algorithms')
    print('and classes for the intelligent cat.')
    print('Did you mean to run main.py?')
    print(f'{signs} {signs}\n')
