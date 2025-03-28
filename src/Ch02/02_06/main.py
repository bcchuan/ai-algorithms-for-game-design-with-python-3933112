"""
main.py: Entry Point for the Cat Trap Game Server

This script initializes and runs the Cat Trap game server, handling client
connections and managing game state updates through WebSocket communication.
The client is the Cat Trap GUI VSCode extension.

Usage:
    Run this file to start the game server.
    Start the Cat Trap GUI Extension: (Ctrl+Shift+P, then "Start Cat Trap Game")

Dependencies:
    - cat_trap_algorithms: Contains the game logic and algorithms.
    - websockets: Used for WebSocket server communication.
    - asyncio: Enables asynchronous operations.
"""

import asyncio
import json
import websockets
import numpy as np
from cat_trap_algorithms import *
from enum import Enum

class GameStatus(Enum):
    GAME_ON = 0
    PLAYER_WINS = 1
    CAT_WINS = 2
    CAT_TIMEOUT = 3

game_status = GameStatus.GAME_ON
game = None
debug_mode = False

async def handler(websocket, path):
    global game
    global game_status
    global debug_mode
    try:
        async for message in websocket:
            if debug_mode:
                print(f'Received message: {message}')  # Debug log
            data = json.loads(message)
            if data['command'] == 'new_game':
                game_status = GameStatus.GAME_ON
                game = CatTrapGame(data['size'])
                game.initialize_random_hexgrid()
                await websocket.send(json.dumps({'command': 'updateGrid', 'data': json.dumps(game.hexgrid.tolist())}))
            elif data['command'] == 'move':
                if not game:
                    # Recreate the game using the provided grid
                    size = len(data['grid'])
                    game = CatTrapGame(size)
                    game.set_hexgrid(np.array(data['grid'], dtype=int))
                if game_status == GameStatus.GAME_ON:
                    game.block_tile(data['clicked_tile'])
                    strategy = data['strategy']
                    random_cat = (strategy == 'random')
                    minimax = (strategy == 'minimax')
                    depth_limited = (strategy == 'limited')
                    iterative_deepening = (strategy == 'iterative')
                    max_depth = data['depth']
                    alpha_beta = data['alpha_beta_pruning']
                    allotted_time = data['deadline']
                    r, c = game.cat
                    if r == 0 or r == game.size - 1 or c == 0 or c == game.size - 1:
                        game_status = GameStatus.CAT_WINS
                    else:
                        new_cat = game.select_cat_move(random_cat,minimax, alpha_beta, depth_limited, max_depth, iterative_deepening, allotted_time)
                        if new_cat == TIMEOUT:
                            game_status = GameStatus.CAT_TIMEOUT
                        else: 
                            if new_cat == game.cat:
                                game_status = GameStatus.PLAYER_WINS
                            game.move_cat(new_cat)
                await websocket.send(json.dumps({'command': 'updateGrid', 'data': json.dumps(game.hexgrid.tolist())}))
            elif data['command'] == 'edit':
                if not game:
                    # Recreate the game using the provided grid
                    size = len(data['grid'])
                    game = CatTrapGame(size)
                    game.hexgrid = np.array(data['grid'], dtype=int)
                    cat = np.argwhere(game.hexgrid == CAT_TILE)  # Find the cat
                    if cat.size > 0: # Cat may be absent in edit mode
                        game.cat = list(cat[0])
                action = data['action']
                if action == 'block':
                    game.block_tile(data['tile'])
                elif action == 'unblock':
                    game.unblock_tile(data['tile'])
                elif action == 'place_cat':
                    game.place_cat(data['tile'])
                game_status = GameStatus.GAME_ON
                await websocket.send(json.dumps({'command': 'updateGrid', 'data': json.dumps(game.hexgrid.tolist())}))
            elif data['command'] == 'request_grid':
                if not game:
                    # Recreate the game using the provided grid
                    size = len(data['grid'])
                    if size > 0:
                        game = CatTrapGame(size)
                        game.hexgrid = np.array(data['grid'], dtype=int)
                        cat = np.argwhere(game.hexgrid == CAT_TILE)  # Find the cat
                        if cat.size > 0: # Cat may be absent in edit mode
                            game.cat = list(cat[0])
                    else:
                        game = CatTrapGame(7)
                        game.initialize_random_hexgrid()
                    game_status = GameStatus.GAME_ON
                await websocket.send(json.dumps({'command': 'updateGrid', 'data': json.dumps(game.hexgrid.tolist())}))

            if game and (game_status != GameStatus.GAME_ON):
                await websocket.send(json.dumps({'command': 'endgame', 'reason': game_status.value}))
                if game_status == GameStatus.CAT_TIMEOUT:
                    game_status = GameStatus.GAME_ON
    
    except websockets.exceptions.ConnectionClosedError as e:
        print(f"Connection closed: {e}")
    except asyncio.CancelledError:
        print("WebSocket handler task was cancelled.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print("Cleaning up after the connection.")


async def main():
    async with websockets.serve(handler, 'localhost', 8765):
        await asyncio.Future()  # Run forever

if __name__ == '__main__':
    asyncio.run(main())
