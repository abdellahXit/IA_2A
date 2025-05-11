import math
import random
import copy
from itertools import product
from collections import deque
import heapq

# Directions possibles
DIRECTIONS = ["UP", "DOWN", "LEFT", "RIGHT"]

class PacmanAI:
    def __init__(self, depth=5, proximity_threshold=5):
        """
        Initialise l'IA de Pacman avec une approche hybride.
        
        Args:
            depth: Profondeur maximale de l'arbre de recherche pour Alpha-Beta
            proximity_threshold: Distance à laquelle un fantôme est considéré comme proche
        """
        self.depth = depth
        self.proximity_threshold = proximity_threshold
        self.last_direction = None
        self.nodes_explored = 0  # Pour le débogage
        self.transposition_table = {}  # Table de transposition pour la mise en cache
        self.ghost_points = [200, 400, 800, 1600]
        self.current_mode = "A*"  # Mode par défaut
        self.last_distance = None
        self.previous_positions = []  # Pour détecter les va-et-vient
        self.max_positions_memory = 10  # Nombre de positions à mémoriser
        self.direction_change_penalty = 50  # Pénalité pour changement de direction
        self.oscillation_penalty = 100  # Pénalité pour oscillation (va-et-vient)
        
    def get_current_mode(self):
        """
        Retourne le mode actuel utilisé par l'IA.
        """
        if str(self.current_mode).strip() == "Alpha-Beta":
            return "α-β"
        return self.current_mode
    
    def get_move(self, game_state):
        """
        Détermine le meilleur mouvement pour Pacman en utilisant une approche hybride:
        - A* si aucun fantôme dangereux n'est à proximité
        - Alpha-Beta sinon
        
        Args:
            game_state: État actuel du jeu contenant:
                - pacman: Objet Pacman
                - ghosts: Liste des fantômes
                - game_map: Carte du jeu
                - ghost_home_coords: Coordonnées de la maison des fantômes
        
        Returns:
            Direction optimale ("UP", "DOWN", "LEFT", "RIGHT")
        """
        pacman = game_state["pacman"]
        ghosts = game_state["ghosts"]
        game_map = game_state["game_map"]
        ghost_home_coords = game_state["ghost_home_coords"]
        
        # Mémoriser la position actuelle pour détecter les oscillations
        current_position = (pacman.grid_x, pacman.grid_y)
        self.previous_positions.append(current_position)
        if len(self.previous_positions) > self.max_positions_memory:
            self.previous_positions.pop(0)
        
        # Vérifier si des fantômes dangereux sont à proximité
        dangerous_ghosts_nearby = self._are_dangerous_ghosts_nearby(
            pacman.grid_x, pacman.grid_y, ghosts, self.proximity_threshold
        )
        
        # Choisir l'algorithme en fonction de la situation
        if not dangerous_ghosts_nearby:
            # Mode A*: Aller vers la nourriture la plus proche ou un fantôme effrayé
            self.current_mode = "A*"
            return self._get_move_astar(game_state)
        else:
            # Mode Alpha-Beta: Situation dangereuse, utiliser Alpha-Beta
            self.current_mode = "α-β"
            return self._get_move_alpha_beta(game_state)
    
    def _are_dangerous_ghosts_nearby(self, pacman_x, pacman_y, ghosts, threshold):
        """
        Vérifie si des fantômes dangereux (non effrayés et non mangés) sont à proximité.
        
        Args:
            pacman_x, pacman_y: Position de Pacman
            ghosts: Liste des fantômes
            threshold: Distance seuil pour considérer un fantôme comme proche
        
        Returns:
            True si au moins un fantôme dangereux est proche, False sinon
        """
        for ghost in ghosts:
            if not ghost.frightened and not ghost.eaten:
                distance = self._manhattan_distance(pacman_x, pacman_y, ghost.grid_x, ghost.grid_y)
                if distance <= threshold:
                    return True
        return False
    
    def _get_move_astar(self, game_state):
        """
        Utilise l'algorithme A* pour trouver le meilleur mouvement vers:
        1. Un fantôme effrayé (priorité)
        2. La nourriture la plus proche
        
        Args:
            game_state: État actuel du jeu
        
        Returns:
            Direction optimale ("UP", "DOWN", "LEFT", "RIGHT")
        """
        pacman = game_state["pacman"]
        ghosts = game_state["ghosts"]
        game_map = game_state["game_map"]
        ghost_home_coords = game_state["ghost_home_coords"]
        
        # Obtenir les mouvements valides
        valid_moves = self._get_valid_moves(pacman, game_map, ghost_home_coords)
        
        if not valid_moves:
            return None
        
        # Si un seul mouvement est valide, le retourner directement
        if len(valid_moves) == 1:
            self.last_direction = valid_moves[0]
            return valid_moves[0]
        
        # Chercher des fantômes effrayés qui ne sont pas dans la maison
        frightened_ghosts = []
        for ghost in ghosts:
            if ghost.frightened and not ghost.eaten:
                # Vérifier si le fantôme n'est pas dans la maison
                GHOST_HOME_X_MIN, GHOST_HOME_X_MAX, GHOST_HOME_Y_MIN, GHOST_HOME_Y_MAX = ghost_home_coords
                is_in_ghost_home = (
                    GHOST_HOME_X_MIN <= ghost.grid_x <= GHOST_HOME_X_MAX and
                    GHOST_HOME_Y_MIN <= ghost.grid_y <= GHOST_HOME_Y_MAX
                )
                
                if not is_in_ghost_home:
                    frightened_ghosts.append((ghost.grid_x, ghost.grid_y))
        
        # Chercher de la nourriture et des énergisants
        food_positions = []
        energizer_positions = []
        
        for y in range(len(game_map)):
            for x in range(len(game_map[0])):
                if game_map[y][x] == 0:  # Nourriture
                    food_positions.append((x, y))
                elif game_map[y][x] == 3:  # Énergisant
                    energizer_positions.append((x, y))
        
        # Définir la cible prioritaire
        target_positions = []
        
        # Priorité 1: Fantômes effrayés
        if frightened_ghosts:
            target_positions = frightened_ghosts
        # Priorité 2: Énergisants
        elif energizer_positions:
            target_positions = energizer_positions
        # Priorité 3: Nourriture normale
        elif food_positions:
            target_positions = food_positions


        
        if not target_positions:
            # Aucune cible trouvée, choisir un mouvement qui évite les oscillations
            return self._choose_non_oscillating_move(pacman, valid_moves)
        
        # Trouver la cible la plus proche
        closest_target = None
        min_distance = float('inf')
        
        for target_x, target_y in target_positions:
            distance = self._manhattan_distance(pacman.grid_x, pacman.grid_y, target_x, target_y)
            if distance < min_distance:
                min_distance = distance
                closest_target = (target_x, target_y)
        
        # Utiliser A* pour trouver le chemin vers la cible la plus proche
        path = self._astar(
            (pacman.grid_x, pacman.grid_y),
            closest_target,
            game_map,
            ghost_home_coords
        )
        
        # Si un chemin est trouvé, retourner la première direction
        if path and len(path) > 1:
            next_pos = path[1]  # La première position après la position actuelle
            
            # Déterminer la direction pour atteindre cette position
            dx = next_pos[0] - pacman.grid_x
            dy = next_pos[1] - pacman.grid_y
            
            # Gérer le tunnel
            if dx > 1:
                dx = -1
            elif dx < -1:
                dx = 1
            
            if dy > 1:
                dy = -1
            elif dy < -1:
                dy = 1
            
            if dx == 1:
                self.last_direction = "RIGHT"
                return "RIGHT"
            elif dx == -1:
                self.last_direction = "LEFT"
                return "LEFT"
            elif dy == 1:
                self.last_direction = "DOWN"
                return "DOWN"
            elif dy == -1:
                self.last_direction = "UP"
                return "UP"
        
        # Si aucun chemin n'est trouvé, choisir un mouvement qui évite les oscillations
        return self._choose_non_oscillating_move(pacman, valid_moves)
    
    def _choose_non_oscillating_move(self, pacman, valid_moves):
        """
        Choisit un mouvement qui évite les oscillations (va-et-vient).
        Préfère continuer dans la même direction si possible.
        """
        # Si la dernière direction est valide, la privilégier
        if self.last_direction in valid_moves:
            return self.last_direction
        
        # Éviter de revenir sur ses pas (détecter les oscillations)
        if len(self.previous_positions) >= 3:
            # Vérifier si on est en train de faire un va-et-vient
            if self.previous_positions[-1] == self.previous_positions[-3]:
                # Trouver une direction qui ne nous ramène pas à la position précédente
                for move in valid_moves:
                    next_x, next_y = self._get_next_position(pacman.grid_x, pacman.grid_y, move)
                    if (next_x, next_y) != self.previous_positions[-2]:
                        self.last_direction = move
                        return move
        
        # Sinon, choisir aléatoirement
        move = random.choice(valid_moves)
        self.last_direction = move
        return move
    
    def _astar(self, start, goal, game_map, ghost_home_coords):
        """
        Implémentation de l'algorithme A* pour trouver le chemin le plus court.
        
        Args:
            start: Position de départ (x, y)
            goal: Position d'arrivée (x, y)
            game_map: Carte du jeu
            ghost_home_coords: Coordonnées de la maison des fantômes
        
        Returns:
            Liste des positions formant le chemin le plus court, ou None si aucun chemin n'est trouvé
        """
        # Initialiser les structures de données
        open_set = []  # File de priorité (heapq)
        closed_set = set()  # Ensemble des nœuds déjà explorés
        
        # Dictionnaire pour reconstruire le chemin
        came_from = {}
        
        # Coût du chemin de départ à chaque nœud
        g_score = {start: 0}
        
        # Coût estimé total de départ à l'arrivée en passant par chaque nœud
        f_score = {start: self._manhattan_distance(start[0], start[1], goal[0], goal[1])}
        
        # Ajouter le nœud de départ à la file de priorité
        heapq.heappush(open_set, (f_score[start], start))
        
        while open_set:
            # Récupérer le nœud avec le score f le plus bas
            _, current = heapq.heappop(open_set)
            
            # Si on a atteint l'objectif, reconstruire le chemin
            if current == goal:
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                path.reverse()
                return path
            
            # Marquer le nœud comme exploré
            closed_set.add(current)
            
            # Explorer les voisins
            for direction in DIRECTIONS:
                next_x, next_y = self._get_next_position(current[0], current[1], direction)
                
                # Gérer le tunnel
                if next_x < 0:
                    next_x = len(game_map[0]) - 1
                elif next_x >= len(game_map[0]):
                    next_x = 0
                if next_y < 0:
                    next_y = len(game_map) - 1
                elif next_y >= len(game_map):
                    next_y = 0
                
                neighbor = (next_x, next_y)
                
                # Vérifier si le mouvement est valide
                if game_map[next_y][next_x] == 1:  # Mur
                    continue
                
                # Vérifier si Pacman essaie d'entrer dans la maison des fantômes
                GHOST_HOME_X_MIN, GHOST_HOME_X_MAX, GHOST_HOME_Y_MIN, GHOST_HOME_Y_MAX = ghost_home_coords
                is_entering_ghost_home = (
                    GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
                    GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
                )
                
                if is_entering_ghost_home:
                    continue  # Pacman ne peut pas entrer dans la maison des fantômes
                
                # Si le voisin a déjà été exploré, passer au suivant
                if neighbor in closed_set:
                    continue
                
                # Calculer le nouveau score g
                tentative_g_score = g_score[current] + 1
                
                # Si le voisin n'est pas dans la file de priorité ou si le nouveau chemin est meilleur
                if neighbor not in [item[1] for item in open_set] or tentative_g_score < g_score.get(neighbor, float('inf')):
                    # Mettre à jour le chemin
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    f_score[neighbor] = tentative_g_score + self._manhattan_distance(next_x, next_y, goal[0], goal[1])
                    
                    # Ajouter le voisin à la file de priorité
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))
        
        # Si on arrive ici, c'est qu'aucun chemin n'a été trouvé
        return None
    
    def _get_move_alpha_beta(self, game_state):
        """
        Détermine le meilleur mouvement pour Pacman en utilisant Alpha-Beta Pruning.
        
        Args:
            game_state: État actuel du jeu
        
        Returns:
            Direction optimale ("UP", "DOWN", "LEFT", "RIGHT")
        """
        self.nodes_explored = 0
        self.transposition_table = {}  # Réinitialiser la table de transposition
        
        pacman = game_state["pacman"]
        ghosts = game_state["ghosts"]
        game_map = game_state["game_map"]
        ghost_home_coords = game_state["ghost_home_coords"]
        direction = pacman.direction if hasattr(pacman, 'direction') else None
        
        # Obtenir les mouvements valides
        valid_moves = self._get_valid_moves(pacman, game_map, ghost_home_coords)
        
        if not valid_moves:
            return None
        
        # Si un seul mouvement est valide, le retourner directement
        if len(valid_moves) == 1:
            self.last_direction = valid_moves[0]
            return valid_moves[0]
        
        # Initialiser les valeurs pour alpha-beta
        best_score = float('-inf')
        best_move = None
        alpha = float('-inf')
        beta = float('inf')
        
        # Évaluer chaque mouvement possible
        for move in valid_moves:
            # Créer des copies pour la simulation
            game_map_copy = copy.deepcopy(game_map)
            ghost_copies = self._copy_ghosts(ghosts)
            
            # Simuler le mouvement de Pacman
            next_x, next_y = self._get_next_position(pacman.grid_x, pacman.grid_y, move)
            
            # Gérer le tunnel
            if next_x < 0:
                next_x = len(game_map_copy[0]) - 1
            elif next_x >= len(game_map_copy[0]):
                next_x = 0
            if next_y < 0:
                next_y = len(game_map_copy) - 1
            elif next_y >= len(game_map_copy):
                next_y = 0
            
            # Mettre à jour la carte (manger de la nourriture ou un énergisant)
            eaten_energizer = False
            if game_map_copy[next_y][next_x] == 0:  # Nourriture
                game_map_copy[next_y][next_x] = 2  # Marquer comme mangé
            elif game_map_copy[next_y][next_x] == 3:  # Énergisant
                game_map_copy[next_y][next_x] = 2  # Marquer comme mangé
                eaten_energizer = True
            
            # Si un énergisant est mangé, effrayer tous les fantômes
            if eaten_energizer:
                for ghost in ghost_copies:
                    if not ghost.eaten:
                        ghost.frightened = True
            
            # Vérifier les collisions avec les fantômes
            pacman_died = False
            ghosts_eaten = 0
            
            for ghost in ghost_copies:
                if ghost.grid_x == next_x and ghost.grid_y == next_y:
                    if ghost.frightened:
                        ghost.eaten = True
                        ghost.frightened = False
                        ghosts_eaten += 1
                    elif not ghost.eaten:
                        pacman_died = True
                        break
            
            # Si Pacman est mort, c'est le pire scénario
            if pacman_died:
                score = -10000
            else:
                # Calculer le score pour ce mouvement
                score = self._alpha_beta(next_x, next_y, ghost_copies, game_map_copy, ghost_home_coords, 
                                        1, self.depth, alpha, beta, False, direction, move, ghosts_eaten)
                
                # Ajouter un bonus/pénalité pour la continuité de direction
                if direction == move:
                    # Bonus pour continuer dans la même direction
                    score += 5
                
            
            # Mettre à jour le meilleur mouvement
            if score > best_score:
                best_score = score
                best_move = move
            
            # Mise à jour d'alpha
            alpha = max(alpha, best_score)
        
        # Si aucun bon mouvement n'est trouvé, choisir un mouvement qui évite les oscillations
        if best_move is None:
            best_move = self._choose_non_oscillating_move(pacman, valid_moves)
        
        self.last_direction = best_move
        return best_move
    
    def _is_oscillating(self, current_x, current_y, next_x, next_y):
        """
        Vérifie si le mouvement de (current_x, current_y) à (next_x, next_y) 
        fait partie d'une oscillation (va-et-vient).
        """
        # Vérifier si on a au moins 3 positions précédentes
        if len(self.previous_positions) < 3:
            return False
        
        # Vérifier si la nouvelle position est identique à l'avant-dernière position
        # (ce qui indiquerait un va-et-vient)
        if len(self.previous_positions) >= 2 and (next_x, next_y) == self.previous_positions[-2]:
            return True
        
        # Vérifier si on a visité cette position récemment (dans les 5 derniers mouvements)
        recent_positions = self.previous_positions[-5:] if len(self.previous_positions) >= 5 else self.previous_positions
        if (next_x, next_y) in recent_positions:
            # Compter combien de fois on a visité cette position récemment
            visit_count = recent_positions.count((next_x, next_y))
            # Si on l'a visitée plus d'une fois, c'est probablement une oscillation
            if visit_count >= 1:
                return True
        
        return False
    
    def _alpha_beta(self, pacman_x, pacman_y, ghosts, game_map, ghost_home_coords, 
                   current_depth, max_depth, alpha, beta, is_max, pac_dir, last_move, ghosts_eaten=0):
        """
        Implémentation récursive de l'algorithme Alpha-Beta Pruning avec mise à jour de la carte.
        
        Args:
            pacman_x, pacman_y: Position de Pacman
            ghosts: Liste des fantômes
            game_map: Carte du jeu
            ghost_home_coords: Coordonnées de la maison des fantômes
            current_depth: Profondeur actuelle dans l'arbre
            max_depth: Profondeur maximale de recherche
            alpha, beta: Valeurs pour l'élagage
            is_max: True si c'est le tour de Pacman (maximiser), False sinon
            pac_dir: Direction actuelle de Pacman
            last_move: Dernier mouvement effectué
            ghosts_eaten: Nombre de fantômes mangés dans cette séquence
        
        Returns:
            Score évalué pour cet état
        """
        self.nodes_explored += 1
        
        # Vérifier si l'état est terminal (profondeur max atteinte ou Pacman mort/victoire)
        if current_depth >= max_depth or self._is_terminal_state(pacman_x, pacman_y, ghosts, game_map):
            return self._evaluate_state(pacman_x, pacman_y, ghosts, game_map, ghosts_eaten, pac_dir, last_move)
        
        if is_max:  # Tour de Pacman (maximiser)
            max_eval = float('-inf')
            
            # Pour chaque mouvement possible de Pacman
            for direction in DIRECTIONS:
                next_x, next_y = self._get_next_position(pacman_x, pacman_y, direction)
                
                # Gérer le tunnel
                if next_x < 0:
                    next_x = len(game_map[0]) - 1
                elif next_x >= len(game_map[0]):
                    next_x = 0
                if next_y < 0:
                    next_y = len(game_map) - 1
                elif next_y >= len(game_map):
                    next_y = 0
                
                # Vérifier si le mouvement est valide
                if game_map[next_y][next_x] == 1:  # Mur
                    continue
                
                # Vérifier si Pacman essaie d'entrer dans la maison des fantômes
                GHOST_HOME_X_MIN, GHOST_HOME_X_MAX, GHOST_HOME_Y_MIN, GHOST_HOME_Y_MAX = ghost_home_coords
                is_entering_ghost_home = (
                    GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
                    GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
                )
                
                if is_entering_ghost_home:
                    continue  # Pacman ne peut pas entrer dans la maison des fantômes
                
                # Créer des copies pour la simulation
                game_map_copy = copy.deepcopy(game_map)
                ghost_copies = self._copy_ghosts(ghosts)
                current_ghosts_eaten = ghosts_eaten
                
                # Mettre à jour la carte (manger de la nourriture ou un énergisant)
                eaten_energizer = False
                if game_map_copy[next_y][next_x] == 0:  # Nourriture
                    game_map_copy[next_y][next_x] = 2  # Marquer comme mangé
                elif game_map_copy[next_y][next_x] == 3:  # Énergisant
                    game_map_copy[next_y][next_x] = 2  # Marquer comme mangé
                    eaten_energizer = True
                
                # Si un énergisant est mangé, effrayer tous les fantômes
                if eaten_energizer:
                    for ghost in ghost_copies:
                        if not ghost.eaten:
                            ghost.frightened = True
                
                # Vérifier les collisions avec les fantômes
                pacman_died = False
                
                for ghost in ghost_copies:
                    if ghost.grid_x == next_x and ghost.grid_y == next_y:
                        if ghost.frightened:
                            ghost.eaten = True
                            ghost.frightened = False
                            current_ghosts_eaten += 1
                        elif not ghost.eaten:
                            pacman_died = True
                            break
                
                # Si Pacman est mort, c'est le pire scénario
                if pacman_died:
                    eval_score = -10000
                else:
                    # Évaluer récursivement
                    eval_score = self._alpha_beta(next_x, next_y, ghost_copies, game_map_copy, ghost_home_coords,
                                                current_depth + 1, max_depth, alpha, beta, False, last_move, direction, current_ghosts_eaten)
                    

                
                max_eval = max(max_eval, eval_score)
                
                # Mise à jour d'alpha
                alpha = max(alpha, max_eval)
                
                # Élagage beta
                if beta <= alpha:
                    break
            
            return max_eval
        
        else:  # Tour des fantômes (minimiser)
            min_eval = float('inf')
            
            # SIMULATION COMPLÈTE DES MOUVEMENTS DES FANTÔMES
            # 1. Créer une copie des fantômes pour la simulation
            ghost_copies = self._copy_ghosts(ghosts)
            
            # 2. Générer toutes les combinaisons possibles de mouvements des fantômes
            ghost_move_combinations = self._generate_ghost_move_combinations(ghost_copies, game_map, ghost_home_coords, pacman_x, pacman_y)
            
            # 3. Évaluer chaque combinaison
            for ghost_moves in ghost_move_combinations:
                # Créer des copies pour la simulation
                game_map_copy = copy.deepcopy(game_map)
                current_ghost_copies = self._copy_ghosts(ghost_copies)
                current_ghosts_eaten = ghosts_eaten
                
                # Appliquer cette combinaison de mouvements
                pacman_died = False
                
                for i, (ghost, move) in enumerate(zip(current_ghost_copies, ghost_moves)):
                    if move is None:
                        continue
                    
                    # Appliquer le mouvement
                    next_x, next_y = self._get_next_position(ghost.grid_x, ghost.grid_y, move)
                    
                    # Gérer le tunnel
                    if next_x < 0:
                        next_x = len(game_map_copy[0]) - 1
                    elif next_x >= len(game_map_copy[0]):
                        next_x = 0
                    if next_y < 0:
                        next_y = len(game_map_copy) - 1
                    elif next_y >= len(game_map_copy):
                        next_y = 0
                    
                    ghost.grid_x, ghost.grid_y = next_x, next_y
                    
                    # Vérifier si Pacman est capturé ou si un fantôme est mangé
                    if pacman_x == next_x and pacman_y == next_y:
                        if ghost.frightened:
                            ghost.eaten = True
                            ghost.frightened = False
                            current_ghosts_eaten += 1
                        elif not ghost.eaten:
                            pacman_died = True
                            break
                
                # Si Pacman est mort, c'est le pire scénario
                if pacman_died:
                    eval_score = -10000
                else:
                    # Évaluer récursivement cet état
                    eval_score = self._alpha_beta(pacman_x, pacman_y, current_ghost_copies, game_map_copy, ghost_home_coords,
                                                current_depth + 1, max_depth, alpha, beta, True, pac_dir, last_move, current_ghosts_eaten)
                
                # Mettre à jour le score minimal
                min_eval = min(min_eval, eval_score)
                
                # Mise à jour de beta
                beta = min(beta, min_eval)
                
                # Élagage alpha
                if beta <= alpha:
                    break
            
            return min_eval
    
    def _is_terminal_state(self, pacman_x, pacman_y, ghosts, game_map):
        """
        Vérifie si l'état est terminal (Pacman mort ou victoire).
        """
        # Vérifier si Pacman est mort (collision avec un fantôme non effrayé)
        for ghost in ghosts:
            if ghost.grid_x == pacman_x and ghost.grid_y == pacman_y and not ghost.frightened and not ghost.eaten:
                return True
        
        # Vérifier s'il reste de la nourriture ou des énergisants
        for row in game_map:
            for cell in row:
                if cell == 0 or cell == 3:  # Nourriture ou énergisant
                    return False
        
        # Si on arrive ici, c'est que Pacman a mangé toute la nourriture (victoire)
        return True
    
    def _evaluate_state(self, pacman_x, pacman_y, ghosts, game_map, ghosts_eaten, pac_dir, last_move):
        """
        Fonction d'évaluation pour un état donné selon les critères spécifiés:
        - -10000 si Pacman meurt
        - +10000 s'il n'y a plus de nourriture et d'énergisants
        - Pénalité pour la nourriture restante: -10 par nourriture
        - Pénalité pour les énergisants restants: -50 par énergisant
        - Bonus pour les fantômes mangés
        - Bonus pour maintenir la même direction
        - Pénalité pour les oscillations
        """
        score = 0
        
        # Vérifier si Pacman est mort (collision avec un fantôme non effrayé)
        for ghost in ghosts:
            if ghost.grid_x == pacman_x and ghost.grid_y == pacman_y and not ghost.frightened and not ghost.eaten:
                return -10000
        
        # Compter la nourriture et les énergisants restants
        foods = []
        energizers = []
        
        for y in range(len(game_map)):
            for x in range(len(game_map[0])):
                if game_map[y][x] == 0:  # Nourriture normale
                    foods.append((x, y))
                elif game_map[y][x] == 3:  # Énergisant (power pellet)
                    energizers.append((x, y))
        
        # S'il n'y a plus de nourriture ni d'énergisants, c'est une victoire
        if not foods and not energizers:
            return 10000
        
        # Pénalité pour la nourriture restante
        score -= len(foods) * 10
        
        # Pénalité pour les énergisants restants
        score -= len(energizers) * 50
        
        # Bonus pour les fantômes mangés
        # Les points pour manger un fantôme augmentent: 200, 400, 800, 1600
        ghost_score = 0
        for i in range(ghosts_eaten):
            ghost_score += self.ghost_points[-1]  # Utiliser la dernière valeur pour les fantômes supplémentaires
        
        score += ghost_score
        

        
 
        
        return score
    
    def _generate_ghost_move_combinations(self, ghosts, game_map, ghost_home_coords, pacman_x, pacman_y):
        """
        Génère toutes les combinaisons possibles de mouvements des fantômes,
        en considérant tous les mouvements valides comme aléatoires, peu importe leur état.
    
        Args:
            ghosts: Liste des fantômes
            game_map: Carte du jeu
            ghost_home_coords: Coordonnées de la maison des fantômes
            pacman_x, pacman_y: Position de Pacman
    
        Returns:
            Liste de toutes les combinaisons possibles de mouvements (liste de tuples)
        """
        ghost_valid_moves = []
    
        for ghost in ghosts:
            valid_moves = self._get_ghost_valid_moves(ghost, game_map, ghost_home_coords)
            if not valid_moves:
                ghost_valid_moves.append([None])  # Aucun mouvement possible
            else:
                ghost_valid_moves.append(valid_moves)
    
        # Générer le produit cartésien de tous les mouvements possibles
        List=list(product(*ghost_valid_moves))
        #print(len(List))
        return List
    
    def _generate_limited_combinations(self, ghosts, ghost_valid_moves, pacman_x, pacman_y):
        """
        Génère un nombre limité de combinaisons en se concentrant sur les fantômes les plus importants.
        """
        # Calculer la distance de chaque fantôme à Pacman
        ghost_distances = []
        for i, ghost in enumerate(ghosts):
            if not ghost.frightened and not ghost.eaten and ghost_valid_moves[i]:
                distance = self._manhattan_distance(ghost.grid_x, ghost.grid_y, pacman_x, pacman_y)
                ghost_distances.append((i, distance))
        
        # Trier par distance croissante
        ghost_distances.sort(key=lambda x: x[1])
        
        # Ne garder que les 2 fantômes les plus proches
        important_ghosts = [idx for idx, _ in ghost_distances[:2]]
        
        # Créer des combinaisons limitées
        limited_moves = []
        for i in range(len(ghosts)):
            if i in important_ghosts:
                limited_moves.append(ghost_valid_moves[i])
            else:
                # Pour les autres fantômes, on ne considère qu'un seul mouvement (ou aucun)
                if ghost_valid_moves[i]:
                    limited_moves.append([ghost_valid_moves[i][0]])
                else:
                    limited_moves.append([None])
        
        return list(product(*limited_moves))
    
    def _get_ghost_valid_moves(self, ghost, game_map, ghost_home_coords):
        """
        Obtient les mouvements valides pour un fantôme en tenant compte des règles du jeu.
        
        Args:
            ghost: Objet fantôme
            game_map: Carte du jeu
            ghost_home_coords: Coordonnées de la maison des fantômes
        
        Returns:
            Liste des directions valides
        """
        valid_moves = []
        opposite_dir = self._get_opposite_direction(ghost.direction)
        
        for direction in DIRECTIONS:
            # Les fantômes ne peuvent pas faire demi-tour (sauf si c'est leur seule option)
            if direction == opposite_dir:
                continue
            
            next_x, next_y = self._get_next_position(ghost.grid_x, ghost.grid_y, direction)
            
            # Gérer le tunnel
            if next_x < 0:
                next_x = len(game_map[0]) - 1
            elif next_x >= len(game_map[0]):
                next_x = 0
            if next_y < 0:
                next_y = len(game_map) - 1
            elif next_y >= len(game_map):
                next_y = 0
            
            # Vérifier si le mouvement est valide (pas un mur)
            if game_map[next_y][next_x] != 1:
                # Vérifier les règles de la maison des fantômes
                GHOST_HOME_X_MIN, GHOST_HOME_X_MAX, GHOST_HOME_Y_MIN, GHOST_HOME_Y_MAX = ghost_home_coords
                
                is_in_ghost_home = (
                    GHOST_HOME_X_MIN <= ghost.grid_x <= GHOST_HOME_X_MAX and
                    GHOST_HOME_Y_MIN <= ghost.grid_y <= GHOST_HOME_Y_MAX
                )
                
                is_entering_ghost_home = (
                    GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
                    GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
                )
                
                # Si le fantôme a quitté la maison et essaie d'y retourner (sauf s'il est mangé)
                if not is_in_ghost_home and is_entering_ghost_home and not ghost.eaten:
                    continue
                
                valid_moves.append(direction)
        
        # Si aucun mouvement valide (rare), autoriser le demi-tour
        if not valid_moves and opposite_dir:
            next_x, next_y = self._get_next_position(ghost.grid_x, ghost.grid_y, opposite_dir)
            if game_map[next_y][next_x] != 1:
                valid_moves.append(opposite_dir)
        
        return valid_moves
    
    def _get_opposite_direction(self, direction):
        """
        Retourne la direction opposée.
        """
        if direction == "UP":
            return "DOWN"
        elif direction == "DOWN":
            return "UP"
        elif direction == "LEFT":
            return "RIGHT"
        elif direction == "RIGHT":
            return "LEFT"
        return None
    
    def _get_eaten_ghost_move(self, ghost, game_map, ghost_home_coords):
        """
        Détermine le mouvement d'un fantôme mangé (retour à la maison).
        """
        # Cible: centre de la maison des fantômes
        GHOST_HOME_X_MIN, GHOST_HOME_X_MAX, GHOST_HOME_Y_MIN, GHOST_HOME_Y_MAX = ghost_home_coords
        target_x = (GHOST_HOME_X_MIN + GHOST_HOME_X_MAX) // 2
        target_y = (GHOST_HOME_Y_MIN + GHOST_HOME_Y_MAX) // 2
        
        return self._get_best_move_to_target(ghost, target_x, target_y, game_map, ghost_home_coords)
    
    def _get_ghost_scatter_target(self, ghost):
        """
        Retourne la cible de dispersion pour un fantôme.
        """
        # Coins de dispersion pour chaque fantôme
        scatter_targets = {
            "BLINKY": (18, 1),  # Coin supérieur droit
            "PINKY": (1, 1),    # Coin supérieur gauche
            "INKY": (18, 20),   # Coin inférieur droit
            "CLYDE": (1, 20)    # Coin inférieur gauche
        }
        
        return scatter_targets.get(ghost.name, (1, 1))
    
    def _get_ghost_chase_target(self, ghost, pacman_x, pacman_y, ghosts):
        """
        Retourne la cible de poursuite pour un fantôme selon sa personnalité.
        """
        if ghost.name == "BLINKY":  # Rouge - poursuit directement Pacman
            return pacman_x, pacman_y
            
        elif ghost.name == "PINKY":  # Rose - vise 4 cases devant Pacman
            # Déterminer la direction de Pacman
            # Pour simplifier, on suppose que Pacman se déplace dans la direction de sa dernière action
            direction = self.last_direction if hasattr(self, 'last_direction') else "RIGHT"
            
            target_x, target_y = pacman_x, pacman_y
            
            if direction == "UP":
                target_y -= 4
                target_x -= 4  # Bug/feature du Pacman original
            elif direction == "DOWN":
                target_y += 4
            elif direction == "LEFT":
                target_x -= 4
            elif direction == "RIGHT":
                target_x += 4
                
            return target_x, target_y
            
        elif ghost.name == "INKY":  # Cyan - utilise la position de Blinky
            # Trouver Blinky
            blinky = None
            for g in ghosts:
                if g.name == "BLINKY":
                    blinky = g
                    break
            
            if not blinky:
                return pacman_x, pacman_y
                
            # Déterminer la direction de Pacman
            direction = self.last_direction if hasattr(self, 'last_direction') else "RIGHT"
            
            # Obtenir le point pivot (2 cases devant Pacman)
            pivot_x, pivot_y = pacman_x, pacman_y
            
            if direction == "UP":
                pivot_y -= 2
            elif direction == "DOWN":
                pivot_y += 2
            elif direction == "LEFT":
                pivot_x -= 2
            elif direction == "RIGHT":
                pivot_x += 2
                
            # Calculer le vecteur de Blinky au point pivot
            vector_x = pivot_x - blinky.grid_x
            vector_y = pivot_y - blinky.grid_y
            
            # Doubler ce vecteur pour obtenir la cible d'Inky
            target_x = pivot_x + vector_x
            target_y = pivot_y + vector_y
            
            return target_x, target_y
            
        elif ghost.name == "CLYDE":  # Orange - alterne entre poursuite et dispersion
            # Calculer la distance à Pacman
            distance = self._manhattan_distance(ghost.grid_x, ghost.grid_y, pacman_x, pacman_y)
            
            if distance > 8:  # Si loin de Pacman, le poursuivre
                return pacman_x, pacman_y
            else:  # Si proche, aller au coin de dispersion
                return self._get_ghost_scatter_target(ghost)
        
        # Par défaut, poursuivre Pacman
        return pacman_x, pacman_y
    
    def _get_best_move_to_target(self, ghost, target_x, target_y, game_map, ghost_home_coords):
        """
        Détermine le meilleur mouvement pour un fantôme vers une cible.
        """
        valid_moves = self._get_ghost_valid_moves(ghost, game_map, ghost_home_coords)
        
        if not valid_moves:
            return None
            
        best_move = None
        min_distance = float('inf')
        
        # Priorité pour départager les égalités (UP > LEFT > DOWN > RIGHT)
        priority_order = ["UP", "LEFT", "DOWN", "RIGHT"]
        
        for move in valid_moves:
            next_x, next_y = self._get_next_position(ghost.grid_x, ghost.grid_y, move)
            
            # Gérer le tunnel
            if next_x < 0:
                next_x = len(game_map[0]) - 1
            elif next_x >= len(game_map[0]):
                next_x = 0
            if next_y < 0:
                next_y = len(game_map) - 1
            elif next_y >= len(game_map):
                next_y = 0
                
            # Calculer la distance à la cible
            distance = self._manhattan_distance(next_x, next_y, target_x, target_y)
            
            # Si cette direction donne une distance plus courte, ou égale mais avec une priorité plus élevée
            if distance < min_distance or (distance == min_distance and 
                                          priority_order.index(move) < priority_order.index(best_move)):
                min_distance = distance
                best_move = move
        
        return best_move
    
    def _get_valid_moves(self, pacman, game_map, ghost_home_coords):
        """
        Retourne les mouvements valides pour Pacman.
        """
        valid_moves = []
        
        for direction in DIRECTIONS:
            next_x, next_y = self._get_next_position(pacman.grid_x, pacman.grid_y, direction)
            
            # Gérer le tunnel
            if next_x < 0:
                next_x = len(game_map[0]) - 1
            elif next_x >= len(game_map[0]):
                next_x = 0
            if next_y < 0:
                next_y = len(game_map) - 1
            elif next_y >= len(game_map):
                next_y = 0
            
            # Vérifier si le mouvement est valide
            if game_map[next_y][next_x] != 1:  # Pas un mur
                # Vérifier si Pacman essaie d'entrer dans la maison des fantômes
                GHOST_HOME_X_MIN, GHOST_HOME_X_MAX, GHOST_HOME_Y_MIN, GHOST_HOME_Y_MAX = ghost_home_coords
                
                is_entering_ghost_home = (
                    GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
                    GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
                )
                
                if not is_entering_ghost_home or not pacman.left_ghost_home:
                    valid_moves.append(direction)
        
        return valid_moves
    
    def _get_next_position(self, x, y, direction):
        """
        Calcule la position suivante en fonction de la direction.
        """
        if direction == "UP":
            return x, y - 1
        elif direction == "DOWN":
            return x, y + 1
        elif direction == "LEFT":
            return x - 1, y
        elif direction == "RIGHT":
            return x + 1, y
        return x, y
    
    def _manhattan_distance(self, x1, y1, x2, y2):
        """
        Calcule la distance de Manhattan entre deux points.
        """
        return abs(x1 - x2) + abs(y1 - y2)
    
    def _copy_ghosts(self, ghosts):
        """
        Crée une copie profonde des fantômes pour la simulation.
        """
        ghost_copies = []
        for ghost in ghosts:
            # Créer un nouvel objet fantôme avec les mêmes propriétés
            ghost_copy = type('GhostCopy', (), {})()
            ghost_copy.grid_x = ghost.grid_x
            ghost_copy.grid_y = ghost.grid_y
            ghost_copy.direction = ghost.direction if hasattr(ghost, 'direction') else "RIGHT"
            ghost_copy.frightened = ghost.frightened
            ghost_copy.eaten = ghost.eaten
            ghost_copy.mode = ghost.mode
            ghost_copy.name = ghost.name
            ghost_copy.left_ghost_home = getattr(ghost, 'left_ghost_home', True)
            ghost_copies.append(ghost_copy)
        return ghost_copies