import math
from collections import deque
from global_names import *
from tools import *

# Increase depth for better lookahead
DEPTH = 4
DIRS = (RIGHT, LEFT, DOWN, UP)
VECT = {RIGHT: (1, 0), LEFT: (-1, 0), DOWN: (0, 1), UP: (0, -1)}

# Cache level information for performance
_level_cache = {}

def _level_info(level):
    lid = id(level)
    if lid in _level_cache:
        return _level_cache[lid]
    width = len(level[0].rstrip('\n'))
    walls = {(x, y)
             for y, row in enumerate(level)
             for x, ch in enumerate(row)
             if ch not in ('.', ' ', '0')}
    _level_cache[lid] = (width, walls)
    return width, walls

def _legal_moves(pos, walls, width):
    x, y = pos
    return [k for k in DIRS if ((x + VECT[k][0]) % width, y + VECT[k][1]) not in walls] or [None]

def _manhattan_distance(a, b, width):
    """Calculate Manhattan distance with tunnel consideration"""
    dx = min(abs(a[0] - b[0]), width - abs(a[0] - b[0]))
    dy = abs(a[1] - b[1])
    return dx + dy

def _advance(pos, key, width):
    if key is None:
        return pos
    dx, dy = VECT[key]
    x, y = pos
    return ((x + dx) % width, y + dy)

# Improved ghost movement prediction
def next_ghost_move(ghost_pos, target_pos, walls, width, forbidden_dir=None):
    moves = _legal_moves(ghost_pos, walls, width)
    
    if forbidden_dir and forbidden_dir in moves and len(moves) > 1:
        moves.remove(forbidden_dir)
    
    best_move = None
    min_dist = float('inf')
    
    for direction in moves:
        new_pos = _advance(ghost_pos, direction, width)
        dist = _manhattan_distance(new_pos, target_pos, width)
        if dist < min_dist:
            min_dist = dist
            best_move = direction
    
    return best_move

def blinky_move(ghost_pos, ghost_state, pacman_pos, walls, width, last_dir=None):
    """Blinky directly targets Pac-Man"""
    if ghost_state[1]:  # If frightened
        # Run away from Pac-Man in scatter mode
        return next_ghost_move(ghost_pos, (26, -3), walls, width, forbidden_dir=opposite_keys.get(last_dir))
    return next_ghost_move(ghost_pos, pacman_pos, walls, width, forbidden_dir=opposite_keys.get(last_dir))

def pinky_move(ghost_pos, ghost_state, pacman_pos, pacman_dir, walls, width, last_dir=None):
    """Pinky targets 4 tiles ahead of Pac-Man"""
    if ghost_state[1]:  # If frightened
        return next_ghost_move(ghost_pos, (2, -3), walls, width, forbidden_dir=opposite_keys.get(last_dir))
    
    px, py = pacman_pos
    if pacman_dir == UP:
        target = (px - 4, py - 4)  # Preserve the original game's bug
    elif pacman_dir == DOWN:
        target = (px, py + 4)
    elif pacman_dir == LEFT:
        target = (px - 4, py)
    else:  # RIGHT
        target = (px + 4, py)
    
    return next_ghost_move(ghost_pos, target, walls, width, forbidden_dir=opposite_keys.get(last_dir))

def inky_move(ghost_pos, ghost_state, pacman_pos, pacman_dir, blinky_pos, walls, width, last_dir=None):
    """Inky uses both Pac-Man and Blinky's positions"""
    if ghost_state[1]:  # If frightened
        return next_ghost_move(ghost_pos, (27, 34), walls, width, forbidden_dir=opposite_keys.get(last_dir))
    
    px, py = pacman_pos
    if pacman_dir == UP:
        tile = (px, py - 2)
    elif pacman_dir == DOWN:
        tile = (px, py + 2)
    elif pacman_dir == LEFT:
        tile = (px - 2, py)
    else:  # RIGHT
        tile = (px + 2, py)
    
    # Vector: Blinky -> tile, then double
    vx = tile[0] - blinky_pos[0]
    vy = tile[1] - blinky_pos[1]
    target = (blinky_pos[0] + 2 * vx, blinky_pos[1] + 2 * vy)
    
    return next_ghost_move(ghost_pos, target, walls, width, forbidden_dir=opposite_keys.get(last_dir))

def clyde_move(ghost_pos, ghost_state, pacman_pos, walls, width, last_dir=None):
    """Clyde targets Pac-Man when far, runs away when close"""
    if ghost_state[1]:  # If frightened
        return next_ghost_move(ghost_pos, (0, 34), walls, width, forbidden_dir=opposite_keys.get(last_dir))
    
    dist = _manhattan_distance(ghost_pos, pacman_pos, width)
    if dist >= 8:
        target = pacman_pos
    else:
        target = (0, 34)  # Scatter target
    
    return next_ghost_move(ghost_pos, target, walls, width, forbidden_dir=opposite_keys.get(last_dir))

# Improved collision detection
def check_rect_collision(pos1, type1, pos2, type2):
    rect_getters = {
        'pacman': pacman_rect,
        'ghost': ghost_rect,
        'food': food_rect,
        'energizer': energizer_rect
    }
    r1 = rect_getters[type1](pos1)
    r2 = rect_getters[type2](pos2)
    return r1.colliderect(r2)

def pacman_rect(pos):
    x, y = pos
    return pygame.Rect(
        CELL_SIZE * x - CELL_SIZE // 4,
        CELL_SIZE * y - CELL_SIZE // 4,
        CELL_SIZE * 1.5,
        CELL_SIZE * 1.5
    )

def ghost_rect(pos):
    x, y = pos
    return pygame.Rect(
        CELL_SIZE * x + CELL_SIZE // 4,
        CELL_SIZE * y + CELL_SIZE // 4,
        CELL_SIZE // 2,
        CELL_SIZE // 2
    )

def food_rect(pos):
    x, y = pos
    return pygame.Rect(
        CELL_SIZE * (x) + CELL_SIZE // 2 - 2,
        CELL_SIZE * (y) + CELL_SIZE // 2 - 2,
        4, 4
    )

def energizer_rect(pos):
    x, y = pos
    return pygame.Rect(
        CELL_SIZE * x,
        CELL_SIZE * y,
        CELL_SIZE // 2, CELL_SIZE // 2
    )

# Improved game state update function
def update_game(pacman, alive, enemy_group, ghosts_status, foods_group, energizers_group, width):
    pac_pos = pacman  # tuple (x, y)
    
    # Check collision with ghosts
    for i, ghost in enumerate(enemy_group):
        ghost_pos = ghost
        if check_rect_collision(pac_pos, 'pacman', ghost_pos, 'ghost'):
            if ghosts_status[i][0]:  # If ghost is alive
                if ghosts_status[i][1]:  # If ghost is frightened
                    # Ghost gets eaten
                    new_status = list(ghosts_status)
                    new_status[i] = (False, True)
                    ghosts_status = tuple(new_status)
                else:
                    # Pac-Man gets eaten
                    alive = False
    
    # Check collision with foods
    new_foods = set(foods_group)
    for food in foods_group:
        if check_rect_collision(pac_pos, 'pacman', food, 'food'):
            new_foods.remove(food)
    
    # Check collision with energizers
    new_energizers = set(energizers_group)
    for energizer in energizers_group:
        if check_rect_collision(pac_pos, 'pacman', energizer, 'energizer'):
            new_energizers.remove(energizer)
            # Make all ghosts frightened
            new_ghosts_status = []
            for status in ghosts_status:
                if status[0]:  # If ghost is alive
                    new_ghosts_status.append((True, True))  # Make it frightened
                else:
                    new_ghosts_status.append(status)
            ghosts_status = tuple(new_ghosts_status)
    
    return pacman, alive, enemy_group, ghosts_status, new_foods, new_energizers

# Improved alpha-beta search
def alpha_beta(state, depth, alpha, beta, maximizing_player, width, walls):
    pacman, alive, direction, ghosts, ghosts_status, ghosts_names, foods, energizers = state
    
    if depth == 0 or not alive or not foods:
        return evaluate_game(state, width, walls), None
    
    if maximizing_player:
        max_eval = float('-inf')
        best_action = None
        
        # Get legal moves for Pac-Man
        moves = _legal_moves(pacman, walls, width)
        forbidden = opposite_keys.get(direction)
        
        # Don't allow reversing direction unless necessary
        legal_moves = [m for m in moves if m != forbidden] or moves
        
        # Prioritize current direction if it's still valid to reduce oscillation
        if direction in legal_moves:
            # Move the current direction to the front of the list
            legal_moves.remove(direction)
            legal_moves.insert(0, direction)
        
        # Check if there are nearby ghosts or energizers to consider
        dangerous_ghosts = []
        frightened_ghosts = []
        
        for i, ghost in enumerate(ghosts):
            if ghosts_status[i][0]:  # If ghost is alive
                if ghosts_status[i][1]:  # If frightened
                    frightened_ghosts.append(ghost)
                else:
                    dangerous_ghosts.append(ghost)
        
        # If there's a nearby frightened ghost, allow reversing to chase it
        if frightened_ghosts:
            closest_dist = min(_manhattan_distance(g, pacman, width) for g in frightened_ghosts)
            if closest_dist <= 5:
                legal_moves = moves  # Allow all moves including reversing
        
        # If there's a nearby dangerous ghost, allow reversing to escape
        elif dangerous_ghosts:
            closest_dist = min(_manhattan_distance(g, pacman, width) for g in dangerous_ghosts)
            if closest_dist <= 3:
                legal_moves = moves  # Allow all moves including reversing
        
        # Try each possible move
        for action in legal_moves:
            new_pacman = _advance(pacman, action, width)
            new_direction = action
            
            # Create new state after Pac-Man's move
            new_alive = alive
            new_ghosts = ghosts
            new_ghosts_status = ghosts_status
            new_foods = foods
            new_energizers = energizers
            
            # Update game state
            new_pacman, new_alive, new_ghosts, new_ghosts_status, new_foods, new_energizers = update_game(
                new_pacman, new_alive, new_ghosts, new_ghosts_status, new_foods, new_energizers, width
            )
            
            new_state = (new_pacman, new_alive, new_direction, new_ghosts, new_ghosts_status,
                         ghosts_names, new_foods, new_energizers)
            
            eval_score, _ = alpha_beta(new_state, depth - 1, alpha, beta, False, width, walls)
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_action = action
            
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        
        return max_eval, best_action
    
    else:  # Minimizing player (ghosts)
        min_eval = float('inf')
        
        # Calculate ghost moves
        new_ghosts = list(ghosts)
        
        for i, ghost_pos in enumerate(ghosts):
            if not ghosts_status[i][0]:  # If ghost is not alive
                continue
            
            ghost_state = ghosts_status[i]
            ghost_name = ghosts_names[i]
            last_dir = None  # We don't track previous directions in this simplified model
            
            # Determine ghost's move based on its type
            if ghost_name == "Blinky":
                move = blinky_move(ghost_pos, ghost_state, pacman, walls, width, last_dir)
            elif ghost_name == "Pinky":
                move = pinky_move(ghost_pos, ghost_state, pacman, direction, walls, width, last_dir)
            elif ghost_name == "Inky":
                blinky_pos = next((ghosts[j] for j, name in enumerate(ghosts_names) if name == "Blinky"), (13, 11))
                move = inky_move(ghost_pos, ghost_state, pacman, direction, blinky_pos, walls, width, last_dir)
            elif ghost_name == "Clyde":
                move = clyde_move(ghost_pos, ghost_state, pacman, walls, width, last_dir)
            else:
                move = None
            
            if move:
                new_ghosts[i] = _advance(ghost_pos, move, width)
        
        # Update game state after ghost moves
        new_alive = alive
        new_ghosts_status = ghosts_status
        new_foods = foods
        new_energizers = energizers
        
        new_pacman, new_alive, new_ghosts, new_ghosts_status, new_foods, new_energizers = update_game(
            pacman, new_alive, new_ghosts, new_ghosts_status, new_foods, new_energizers, width
        )
        
        new_state = (new_pacman, new_alive, direction, new_ghosts, new_ghosts_status,
                     ghosts_names, new_foods, new_energizers)
        
        eval_score, _ = alpha_beta(new_state, depth - 1, alpha, beta, True, width, walls)
        min_eval = min(min_eval, eval_score)
        
        return min_eval, None

# Improved evaluation function
def evaluate_game(state, width, walls):
    pacman, alive, direction, ghosts, ghosts_status, ghosts_names, foods, energizers = state
    
    if not alive:
        return -100000  # Large penalty for dying
    
    if not foods and not energizers:
        return 100000  # Large reward for clearing the level
    
    score = 0
    
    # Base score: remaining pellets
    score -= len(foods) * 10  # Fewer pellets is better
    
    # Energizer value
    if energizers:
        closest_energizer = min(energizers, key=lambda e: _manhattan_distance(e, pacman, width))
        energizer_dist = _manhattan_distance(closest_energizer, pacman, width)
        
        # If ghosts are nearby and not frightened, prioritize getting energizers
        dangerous_nearby = False
        for i, ghost in enumerate(ghosts):
            if ghosts_status[i][0] and not ghosts_status[i][1]:  # Alive and not frightened
                if _manhattan_distance(ghost, pacman, width) < 5:
                    dangerous_nearby = True
                    break
        
        if dangerous_nearby:
            score += 500 / (energizer_dist + 1)  # Higher priority when in danger
        else:
            score += 200 / (energizer_dist + 1)  # Normal priority
    
    # Food value - prioritize closest food
    if foods:
        closest_food = min(foods, key=lambda f: _manhattan_distance(f, pacman, width))
        food_dist = _manhattan_distance(closest_food, pacman, width)
        score += 300 / (food_dist + 1)
    
    # Ghost evaluation
    for i, ghost_pos in enumerate(ghosts):
        if not ghosts_status[i][0]:  # Ghost is not alive (already eaten)
            score += 1000  # Reward for eating ghosts
            continue
        
        dist = _manhattan_distance(ghost_pos, pacman, width)
        
        if ghosts_status[i][1]:  # Ghost is frightened
            if dist < 8:  # Close enough to chase
                score += 2000 / (dist + 1)  # Reward for being close to frightened ghosts
            else:
                score += 500 / (dist + 1)  # Less reward for distant frightened ghosts
        else:  # Ghost is dangerous
            if dist < 3:  # Very close
                score -= 5000 / (dist + 1)  # Heavy penalty for being close to dangerous ghosts
            elif dist < 8:  # Moderately close
                score -= 1000 / (dist + 1)  # Moderate penalty
            else:
                score -= 200 / (dist + 1)  # Small penalty for distant ghosts
    
    # Avoid getting trapped - penalize positions with few escape routes
    escape_routes = len(_legal_moves(pacman, walls, width))
    if escape_routes < 3:
        score -= (3 - escape_routes) * 200  # Penalty for positions with few escape routes
    
    # Add movement consistency bonus to prevent oscillation
    if direction is not None:
        # Check if continuing in the same direction is a valid move
        next_pos = _advance(pacman, direction, width)
        next_pos_xy = (next_pos[0], next_pos[1])
        if next_pos_xy not in walls:
            # Give a small bonus for continuing in the same direction
            score += 100
    
    return score

# Main function to determine Pac-Man's next move
def next_move(game_obj, game_parameters, enemy_group, foods_group, energizers_group):
    # Get current game state
    pacman = tuple(position(game_obj['Pac-Man']))
    alive = True
    direction = game_obj['Pac-Man'].action
    
    # Get ghost information
    ghosts = [tuple(position(enemy)) for enemy in enemy_group]
    ghosts_status = [tuple((enemy.alive, enemy.frightened)) for enemy in enemy_group]
    ghosts_names = [enemy.name for enemy in enemy_group]
    
    # Get food and energizer information
    foods = set(tuple(position(food)) for food in foods_group)
    energizers = set(tuple(position(energizer)) for energizer in energizers_group)
    
    # Get level information
    level = game_parameters['map']
    width, walls = _level_info(level)
    
    # Create initial state
    state = (pacman, alive, direction, ghosts, ghosts_status, ghosts_names, foods, energizers)
    
    # Run alpha-beta search
    score, action = alpha_beta(state, DEPTH, float('-inf'), float('inf'), True, width, walls)
    
    # If no good move is found, choose a random legal move
    if action is None:
        legal_moves = _legal_moves(pacman, walls, width)
        if legal_moves:
            action = legal_moves[0]
    
    # Apply smoothing to prevent oscillation
    current_action = direction
    action = smooth_decision(current_action, action, game_obj, walls, width)
    
    return action

def smooth_decision(current_action, new_action, game_obj, walls, width):
    """Apply smoothing to prevent oscillation in Pac-Man's movement"""
    # If the new action is the opposite of the current one, we need to check if it's really necessary
    if new_action == opposite_keys.get(current_action):
        pacman_pos = tuple(position(game_obj['Pac-Man']))
        
        # Check if continuing in the current direction is dangerous
        next_pos = _advance(pacman_pos, current_action, width)
        if next_pos not in walls:
            # Check if there's an immediate danger in the current direction
            for enemy in enemy_group:
                enemy_pos = tuple(position(enemy))
                if not enemy.frightened and _manhattan_distance(next_pos, enemy_pos, width) < 2:
                    # Danger ahead! Allow the direction change
                    return new_action
            
            # No immediate danger, stick with current direction to avoid oscillation
            return current_action
    
    return new_action
