import pygame
import random
import sys
import math
import os
from pacman_ai import PacmanAI

# Initialize pygame
pygame.init()

# Grid settings
GRID_SIZE = 30
GRID_WIDTH = 19
GRID_HEIGHT = 22
WIDTH = GRID_SIZE * GRID_WIDTH
HEIGHT = GRID_SIZE * GRID_HEIGHT

# Colors
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
RED = (255, 0, 0)
PINK = (255, 192, 203)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)
BLUE_GHOST = (0, 0, 200)  # Color for frightened ghosts

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pacman Grid Game")
clock = pygame.time.Clock()

# Game map (1 = wall, 0 = path with food, 2 = empty path, 3 = power pellet)
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 1],
    [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 2, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 2, 2, 2, 1, 0, 1, 0, 1, 1, 1, 1],
    [0, 0, 0, 0, 0, 0, 0, 1, 2, 2, 2, 1, 0, 0, 0, 0, 0, 0, 0],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    [1, 3, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 3, 1],
    [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
    [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Define ghost home area coordinates
# This defines the rectangle of the ghost home
GHOST_HOME_X_MIN = 7
GHOST_HOME_X_MAX = 11
GHOST_HOME_Y_MIN = 8
GHOST_HOME_Y_MAX = 10

# Count total food and power pellets
total_food = sum(row.count(0) for row in game_map) + sum(row.count(3) for row in game_map)

# Ghost mode constants
SCATTER = "SCATTER"
CHASE = "CHASE"
FRIGHTENED = "FRIGHTENED"

# Ghost home corners (scatter targets)
GHOST_CORNERS = {
    "BLINKY": (GRID_WIDTH - 2, 1),  # Top-right
    "PINKY": (1, 1),                # Top-left
    "INKY": (GRID_WIDTH - 2, GRID_HEIGHT - 2),  # Bottom-right
    "CLYDE": (1, GRID_HEIGHT - 2)   # Bottom-left
}

# Function to load ghost images
def load_ghost_images():
    # Dictionary to store all ghost images
    ghost_images = {
        "BLINKY": None,
        "PINKY": None,
        "INKY": None,
        "CLYDE": None,
        "FRIGHTENED": None,
        "FRIGHTENED_FLASH": None,
        "EATEN": None
    }
    
    # Check if the images directory exists
    if not os.path.exists("images"):
        # If not, we'll use placeholder colors instead
        return None
    
    try:
        # Try to load images if they exist
        ghost_images["BLINKY"] = pygame.image.load("images/blinky.png")
        ghost_images["PINKY"] = pygame.image.load("images/pinky.png")
        ghost_images["INKY"] = pygame.image.load("images/inky.png")
        ghost_images["CLYDE"] = pygame.image.load("images/clyde.png")
        ghost_images["FRIGHTENED"] = pygame.image.load("images/frightened.png")
        ghost_images["FRIGHTENED_FLASH"] = pygame.image.load("images/frightened_flash.png")
        ghost_images["EATEN"] = pygame.image.load("images/eaten.png")
        
        # Resize all images to fit the grid
        for key in ghost_images:
            if ghost_images[key]:
                ghost_images[key] = pygame.transform.scale(ghost_images[key], (GRID_SIZE, GRID_SIZE))
        
        return ghost_images
    except (pygame.error, FileNotFoundError):
        # If any image fails to load, return None to use fallback rendering
        return None

# Try to load ghost images
ghost_images = load_ghost_images()

class Pacman:
    def __init__(self):
        self.grid_x = 9
        self.grid_y = 16
        self.direction = None
        self.next_direction = None  # Store the next direction for smoother control
        self.score = 0
        self.lives = 4
        self.mouth_open = True
        self.mouth_change_timer = 0
        self.moving = False
        
        # NEW: Add speed control for Pacman
        self.move_counter = 0
        self.speed = 6 # Pacman moves every 2 frames (slower than original)
        
        # NEW: Track if Pacman has left the ghost home
        self.left_ghost_home = True  # Pacman starts outside the ghost home
        
    def update(self):
        # Change mouth state every 10 frames
        self.mouth_change_timer += 1
        if self.mouth_change_timer >= 10:
            self.mouth_open = not self.mouth_open
            self.mouth_change_timer = 0
            
        # NEW: Implement speed control for Pacman
        self.move_counter += 1
        if self.move_counter < self.speed:
            return False  # No power pellet eaten, skip movement this frame
            
        # Reset counter when it's time to move
        self.move_counter = 0
            
        # If not currently moving, do nothing
        if not self.moving:
            return False
            
        # Move in the current direction
        if self.direction:
            next_x, next_y = self.grid_x, self.grid_y
            
            if self.direction == "UP":
                next_y -= 1
            elif self.direction == "DOWN":
                next_y += 1
            elif self.direction == "LEFT":
                next_x -= 1
            elif self.direction == "RIGHT":
                next_x += 1
                
            # Wrap around the screen (tunnel)
            if next_x < 0:
                next_x = GRID_WIDTH - 1
            elif next_x >= GRID_WIDTH:
                next_x = 0
            if next_y < 0:
                next_y = GRID_HEIGHT - 1
            elif next_y >= GRID_HEIGHT:
                next_y = 0
                
            # NEW: Check if Pacman is trying to enter the ghost home after leaving it
            is_entering_ghost_home = (
                GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
                GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
            )
            
            # NEW: Check if Pacman is currently in the ghost home
            is_in_ghost_home = (
                GHOST_HOME_X_MIN <= self.grid_x <= GHOST_HOME_X_MAX and
                GHOST_HOME_Y_MIN <= self.grid_y <= GHOST_HOME_Y_MAX
            )
            
            # NEW: If Pacman was in the ghost home, mark that he has left
            if is_in_ghost_home and not is_entering_ghost_home:
                self.left_ghost_home = True
                
            # NEW: If Pacman has left the ghost home and is trying to re-enter, prevent movement
            if self.left_ghost_home and is_entering_ghost_home:
                # Don't move into the ghost home
                self.moving = False
                return False
                
            # If the next position is not a wall, move
            if game_map[next_y][next_x] != 1:
                self.grid_x, self.grid_y = next_x, next_y
                
                # Eat food
                if game_map[self.grid_y][self.grid_x] == 0:
                    game_map[self.grid_y][self.grid_x] = 2
                    self.score += 10
                # Eat power pellet
                elif game_map[self.grid_y][self.grid_x] == 3:
                    game_map[self.grid_y][self.grid_x] = 2
                    self.score += 50
                    return True  # Signal that a power pellet was eaten
            
            # Stop moving after one step
            self.moving = False
            
            # Try to move in the next direction if it's set
            if self.next_direction and self.next_direction != self.direction:
                self.move(self.next_direction)
                self.next_direction = None
                
        return False  # No power pellet eaten
    
    def move(self, direction):
        # Store the next direction if we're already moving
        if self.moving:
            self.next_direction = direction
            return
            
        self.direction = direction
        
        # Check if the move is valid
        next_x, next_y = self.grid_x, self.grid_y
        
        if direction == "UP":
            next_y -= 1
        elif direction == "DOWN":
            next_y += 1
        elif direction == "LEFT":
            next_x -= 1
        elif direction == "RIGHT":
            next_x += 1
            
        # Wrap around the screen (tunnel)
        if next_x < 0:
            next_x = GRID_WIDTH - 1
        elif next_x >= GRID_WIDTH:
            next_x = 0
        if next_y < 0:
            next_y = GRID_HEIGHT - 1
        elif next_y >= GRID_HEIGHT:
            next_y = 0
            
        # NEW: Check if Pacman is trying to enter the ghost home after leaving it
        is_entering_ghost_home = (
            GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
            GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
        )
        
        # NEW: If Pacman has left the ghost home and is trying to re-enter, prevent movement
        if self.left_ghost_home and is_entering_ghost_home:
            return  # Don't move
            
        # If the next position is not a wall, set moving to true
        if game_map[next_y][next_x] != 1:
            self.moving = True
    
    def draw(self):
        x = self.grid_x * GRID_SIZE
        y = self.grid_y * GRID_SIZE
        
        # Draw Pacman as a circle with a mouth
        if self.mouth_open:
            # Draw with mouth open based on direction
            if self.direction == "RIGHT":
                pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE//2, y + GRID_SIZE//2), GRID_SIZE//2)
                pygame.draw.polygon(screen, BLACK, [
                    (x + GRID_SIZE//2, y + GRID_SIZE//2),
                    (x + GRID_SIZE, y + GRID_SIZE//4),
                    (x + GRID_SIZE, y + GRID_SIZE - GRID_SIZE//4)
                ])
            elif self.direction == "LEFT":
                pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE//2, y + GRID_SIZE//2), GRID_SIZE//2)
                pygame.draw.polygon(screen, BLACK, [
                    (x + GRID_SIZE//2, y + GRID_SIZE//2),
                    (x, y + GRID_SIZE//4),
                    (x, y + GRID_SIZE - GRID_SIZE//4)
                ])
            elif self.direction == "UP":
                pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE//2, y + GRID_SIZE//2), GRID_SIZE//2)
                pygame.draw.polygon(screen, BLACK, [
                    (x + GRID_SIZE//2, y + GRID_SIZE//2),
                    (x + GRID_SIZE//4, y),
                    (x + GRID_SIZE - GRID_SIZE//4, y)
                ])
            elif self.direction == "DOWN":
                pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE//2, y + GRID_SIZE//2), GRID_SIZE//2)
                pygame.draw.polygon(screen, BLACK, [
                    (x + GRID_SIZE//2, y + GRID_SIZE//2),
                    (x + GRID_SIZE//4, y + GRID_SIZE),
                    (x + GRID_SIZE - GRID_SIZE//4, y + GRID_SIZE)
                ])
            else:
                # Default to right direction if no direction set
                pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE//2, y + GRID_SIZE//2), GRID_SIZE//2)
                pygame.draw.polygon(screen, BLACK, [
                    (x + GRID_SIZE//2, y + GRID_SIZE//2),
                    (x + GRID_SIZE, y + GRID_SIZE//4),
                    (x + GRID_SIZE, y + GRID_SIZE - GRID_SIZE//4)
                ])
        else:
            # Draw as a full circle when mouth is closed
            pygame.draw.circle(screen, YELLOW, (x + GRID_SIZE//2, y + GRID_SIZE//2), GRID_SIZE//2)

class Ghost:
    def __init__(self, grid_x, grid_y, color, name):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.color = color
        self.name = name  # BLINKY, PINKY, INKY, or CLYDE
        self.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        self.moving = False
        self.mode = SCATTER
        self.target_x = 0
        self.target_y = 0
        self.frightened_timer = 0
        self.frightened = False
        self.eaten = False
        
        # Speed control variables
        self.move_counter = 0
        
        # NEW: Add flashing state for frightened mode
        self.flashing = False
        self.flash_timer = 0
        self.flash_state = True  # True = blue, False = white
        
        # NEW: Track if ghost has left the ghost home
        self.left_ghost_home = False
        
        # Set different speeds for different ghosts (higher = slower)
        if name == "BLINKY":
            self.speed = 6  # Moves every 3 frames (slower)
        elif name == "PINKY":
            self.speed = 6  # Moves every 4 frames
        elif name == "INKY":
            self.speed = 6  # Moves every 4 frames
        else:  # CLYDE
            self.speed = 6  # Moves every 5 frames (slowest)
        
        # For drawing order (z-index)
        self.draw_priority = 0
        
    def update(self, pacman, ghosts):
        # Increment move counter and check if it's time to move
        self.move_counter += 1
        if self.move_counter < self.speed:
            # Still update frightened timer and flashing even if not moving
            if self.frightened:
                self.frightened_timer -= 1
                
                # NEW: Start flashing when timer is low
                if self.frightened_timer <= 30 and not self.flashing:  # Start flashing with 1 second left
                    self.flashing = True
                
                # NEW: Update flash state
                if self.flashing:
                    self.flash_timer += 1
                    if self.flash_timer >= 5:  # Flash every 5 frames
                        self.flash_state = not self.flash_state
                        self.flash_timer = 0
                
                # End frightened mode when timer expires
                if self.frightened_timer <= 0:
                    self.frightened = False
                    self.flashing = False
                    
                    # Make ghosts even slower when coming out of frightened mode
                    if not self.eaten:
                        self.speed += 1  # Temporarily slower
                        # Cap the speed to prevent it from getting too slow
                        if self.speed > 12:
                            self.speed = 12
            
            return  # Skip movement this frame
        
        # Reset counter when it's time to move
        self.move_counter = 0
        
        # If not currently moving, start moving
        if not self.moving:
            # NEW: Check if ghost is in home
            is_in_ghost_home = (
                GHOST_HOME_X_MIN <= self.grid_x <= GHOST_HOME_X_MAX and
                GHOST_HOME_Y_MIN <= self.grid_y <= GHOST_HOME_Y_MAX
            )
            
            if is_in_ghost_home and not self.eaten:
                # Use special home movement logic
                self.move_in_home()
            else:
                # Use normal movement logic
                self.move(pacman, ghosts)
            return
            
        # Move in the current direction
        next_x, next_y = self.grid_x, self.grid_y
        
        if self.direction == "UP":
            next_y -= 1
        elif self.direction == "DOWN":
            next_y += 1
        elif self.direction == "LEFT":
            next_x -= 1
        elif self.direction == "RIGHT":
            next_x += 1
            
        # Wrap around the screen (tunnel)
        if next_x < 0:
            next_x = GRID_WIDTH - 1
        elif next_x >= GRID_WIDTH:
            next_x = 0
        if next_y < 0:
            next_y = GRID_HEIGHT - 1
        elif next_y >= GRID_HEIGHT:
            next_y = 0
            
        # NEW: Check if ghost is currently in the ghost home
        is_in_ghost_home = (
            GHOST_HOME_X_MIN <= self.grid_x <= GHOST_HOME_X_MAX and
            GHOST_HOME_Y_MIN <= self.grid_y <= GHOST_HOME_Y_MAX
        )
        
        # NEW: Check if ghost is trying to enter the ghost home
        is_entering_ghost_home = (
            GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
            GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
        )
        
        # NEW: If ghost was in the ghost home and is now leaving, mark it
        if is_in_ghost_home and not is_entering_ghost_home:
            self.left_ghost_home = True
            
        # NEW: If ghost has left the ghost home and is trying to re-enter (and not eaten)
        if self.left_ghost_home and is_entering_ghost_home and not self.eaten:
            # Don't move into the ghost home
            self.moving = False
            return
            
        # If the next position is not a wall, move
        if game_map[next_y][next_x] != 1:
            self.grid_x, self.grid_y = next_x, next_y
            
        # Stop moving after one step
        self.moving = False
        
        # Update draw priority based on position (for proper z-index)
        self.draw_priority = self.grid_y * 100 + self.grid_x
        
    def move_in_home(self):
        """Special movement logic for ghosts inside the home"""
        self.moving = True
        
        # Define the exit point
        exit_x, exit_y = 9, 7  # Home entrance + 1
        
        # Calculate the best direction to reach the exit
        if self.grid_x < exit_x:
            # Need to move right
            self.direction = "RIGHT"
        elif self.grid_x > exit_x:
            # Need to move left
            self.direction = "LEFT"
        elif self.grid_y > exit_y:
            # Need to move up
            self.direction = "UP"
        else:
            # Already at the right position horizontally, move up
            self.direction = "UP"
        
        # Move in the chosen direction
        next_x, next_y = self.grid_x, self.grid_y
        
        if self.direction == "UP":
            next_y -= 1
        elif self.direction == "DOWN":
            next_y += 1
        elif self.direction == "LEFT":
            next_x -= 1
        elif self.direction == "RIGHT":
            next_x += 1
        
        # Check if the next position is valid (not a wall and still in or near home)
        if game_map[next_y][next_x] != 1:
            self.grid_x, self.grid_y = next_x, next_y
        else:
            # If we hit a wall, try another direction
            # Priority: UP, LEFT, RIGHT, DOWN
            for test_dir in ["UP", "LEFT", "RIGHT", "DOWN"]:
                if test_dir == self.direction:
                    continue  # Skip the direction we just tried
                    
                test_x, test_y = self.grid_x, self.grid_y
                
                if test_dir == "UP":
                    test_y -= 1
                elif test_dir == "DOWN":
                    test_y += 1
                elif test_dir == "LEFT":
                    test_x -= 1
                elif test_dir == "RIGHT":
                    test_x += 1
                    
                if game_map[test_y][test_x] != 1:
                    self.direction = test_dir
                    self.grid_x, self.grid_y = test_x, test_y
                    break
        
        # Stop moving after one step
        self.moving = False
        
        # Update draw priority
        self.draw_priority = self.grid_y * 100 + self.grid_x
    
    def move(self, pacman, ghosts):
        self.moving = True
        
        # If eaten, head back to the ghost house
        if self.eaten:
            # Define specific starting positions for each ghost
            ghost_start_positions = {
                "BLINKY": (10, 9),
                "PINKY": (8, 9),
                "INKY": (10, 10),
                "CLYDE": (8, 10)
            }
        
            # Get this ghost's specific starting position
            target_x, target_y = ghost_start_positions[self.name]
            if self.grid_x == target_x and self.grid_y == target_y:
                self.eaten = False
                self.frightened = False
                self.flashing = False
                self.left_ghost_home = False  # Reset this flag when respawning
                # Reset speed to normal after respawning
                if self.name == "BLINKY":
                    self.speed = 6
                elif self.name == "PINKY" or self.name == "INKY":
                    self.speed = 6
                else:  # CLYDE
                    self.speed = 6
                # Choose a random direction to start moving (preferably upward to leave home)
                valid_dirs = self.get_valid_directions()
                if "UP" in valid_dirs:
                    self.direction = "UP"  # Prefer going up to leave the ghost house
                else:
                    self.direction = random.choice(valid_dirs) if valid_dirs else "UP"
                    
                return
            else:
                # Head to the specific starting position
                self.choose_direction_to_target(target_x, target_y)
            return
    
        
        # If in frightened mode, move randomly
        if self.frightened:
            valid_directions = self.get_valid_directions()
            # Remove the opposite direction to avoid reversing
            opposite = self.get_opposite_direction()
            if opposite in valid_directions and len(valid_directions) > 1:
                valid_directions.remove(opposite)
            
            if valid_directions:
                self.direction = random.choice(valid_directions)
            return
        
        # Determine target based on mode and ghost type
        if self.mode == SCATTER:
            # Head to home corner
            self.target_x, self.target_y = GHOST_CORNERS[self.name]
        else:  # CHASE mode
            if self.name == "BLINKY":  # Red ghost - directly targets Pacman
                self.target_x, self.target_y = pacman.grid_x, pacman.grid_y
            
            elif self.name == "PINKY":  # Pink ghost - targets 4 tiles ahead of Pacman
                self.target_x, self.target_y = pacman.grid_x, pacman.grid_y
                
                # Get 4 tiles ahead in Pacman's direction
                if pacman.direction == "UP":
                    self.target_y -= 4
                    self.target_x -= 4  # The original Pacman bug/feature
                elif pacman.direction == "DOWN":
                    self.target_y += 4
                elif pacman.direction == "LEFT":
                    self.target_x -= 4
                elif pacman.direction == "RIGHT":
                    self.target_x += 4
                else:  # If Pacman isn't moving, target his position
                    pass
            
            elif self.name == "INKY":  # Cyan ghost - uses Blinky's position
                # Find Blinky
                blinky = None
                for ghost in ghosts:
                    if ghost.name == "BLINKY":
                        blinky = ghost
                        break
                
                if blinky:
                    # Get 2 tiles ahead of Pacman
                    pivot_x, pivot_y = pacman.grid_x, pacman.grid_y
                    
                    if pacman.direction == "UP":
                        pivot_y -= 2
                    elif pacman.direction == "DOWN":
                        pivot_y += 2
                    elif pacman.direction == "LEFT":
                        pivot_x -= 2
                    elif pacman.direction == "RIGHT":
                        pivot_x += 2
                    
                    # Calculate the vector from Blinky to the pivot point
                    vector_x = pivot_x - blinky.grid_x
                    vector_y = pivot_y - blinky.grid_y
                    
                    # Double the vector to get Inky's target
                    self.target_x = pivot_x + vector_x
                    self.target_y = pivot_y + vector_y
                else:
                    # If Blinky isn't found, just target Pacman
                    self.target_x, self.target_y = pacman.grid_x, pacman.grid_y
            
            elif self.name == "CLYDE":  # Orange ghost - alternates between chase and scatter
                # Calculate distance to Pacman
                distance = math.sqrt((self.grid_x - pacman.grid_x)**2 + (self.grid_y - pacman.grid_y)**2)
                
                if distance > 8:  # If far from Pacman, chase him
                    self.target_x, self.target_y = pacman.grid_x, pacman.grid_y
                else:  # If close to Pacman, go to scatter corner
                    self.target_x, self.target_y = GHOST_CORNERS["CLYDE"]
                # NEW: Check if ghost is currently in the ghost home
                
        # Choose the direction that gets closest to the target
        self.choose_direction_to_target(self.target_x, self.target_y)

    
    def choose_direction_to_target(self, target_x, target_y):
        # Get valid directions (no walls)
        valid_directions = self.get_valid_directions()
        
        # Remove the opposite direction to avoid reversing
        opposite = self.get_opposite_direction()
        if opposite in valid_directions and len(valid_directions) > 1:
            valid_directions.remove(opposite)
        
        # If no valid directions, stay in place
        if not valid_directions:
            return
        
        # Find the direction that minimizes distance to target
        best_direction = None
        min_distance = float('inf')
        
        # Priority order for tie-breaking (Up > Left > Down > Right)
        priority_order = ["UP", "LEFT", "DOWN", "RIGHT"]
        
        for direction in valid_directions:
            next_x, next_y = self.grid_x, self.grid_y
            
            if direction == "UP":
                next_y -= 1
            elif direction == "DOWN":
                next_y += 1
            elif direction == "LEFT":
                next_x -= 1
            elif direction == "RIGHT":
                next_x += 1
                
            # Wrap around the screen (tunnel)
            if next_x < 0:
                next_x = GRID_WIDTH - 1
            elif next_x >= GRID_WIDTH:
                next_x = 0
            if next_y < 0:
                next_y = GRID_HEIGHT - 1
            elif next_y >= GRID_HEIGHT:
                next_y = 0
                
            # NEW: Check if ghost is trying to enter the ghost home after leaving it
            is_entering_ghost_home = (
                GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
                GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
            )
            
            # NEW: Skip this direction if it would enter the ghost home (unless eaten)
            if self.left_ghost_home and is_entering_ghost_home and not self.eaten:
                continue
                
            # Calculate Euclidean distance to target
            distance = math.sqrt((next_x - target_x)**2 + (next_y - target_y)**2)
            
            # If this direction gives a shorter distance, or it's the same but higher priority
            if distance < min_distance or (distance == min_distance and priority_order.index(direction) < priority_order.index(best_direction)):
                min_distance = distance
                best_direction = direction
        
        # If we found a valid direction, use it
        if best_direction:
            self.direction = best_direction
    
    def get_valid_directions(self):
        valid_directions = []
        
        # Check each direction
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]
        for direction in directions:
            next_x, next_y = self.grid_x, self.grid_y
            
            if direction == "UP":
                next_y -= 1
            elif direction == "DOWN":
                next_y += 1
            elif direction == "LEFT":
                next_x -= 1
            elif direction == "RIGHT":
                next_x += 1
                
            # Wrap around the screen (tunnel)
            if next_x < 0:
                next_x = GRID_WIDTH - 1
            elif next_x >= GRID_WIDTH:
                next_x = 0
            if next_y < 0:
                next_y = GRID_HEIGHT - 1
            elif next_y >= GRID_HEIGHT:
                next_y = 0
                
            # NEW: Check if ghost is trying to enter the ghost home after leaving it
            is_entering_ghost_home = (
                GHOST_HOME_X_MIN <= next_x <= GHOST_HOME_X_MAX and
                GHOST_HOME_Y_MIN <= next_y <= GHOST_HOME_Y_MAX
            )
            
            # NEW: Skip this direction if it would enter the ghost home (unless eaten)
            if self.left_ghost_home and is_entering_ghost_home and not self.eaten:
                continue
                
            # If the next position is not a wall, it's a valid direction
            if game_map[next_y][next_x] != 1:
                valid_directions.append(direction)
        
        return valid_directions
    
    def get_opposite_direction(self):
        if self.direction == "UP":
            return "DOWN"
        elif self.direction == "DOWN":
            return "UP"
        elif self.direction == "LEFT":
            return "RIGHT"
        elif self.direction == "RIGHT":
            return "LEFT"
        return None
    
    def set_frightened(self, duration=150):  # 5 seconds at 30 FPS
        self.frightened = True
        self.frightened_timer = duration
        self.flashing = False
        self.flash_state = True
        
        # Make ghosts slower when frightened
        self.speed = 10  # Very slow when frightened
        
        # Reverse direction when entering frightened mode
        self.direction = self.get_opposite_direction()
    
    def set_eaten(self):
        self.eaten = True
        self.frightened = False
        self.flashing = False
        # Eaten ghosts move faster to return to the ghost house
        self.speed = 2
    
    def draw(self):
        x = self.grid_x * GRID_SIZE
        y = self.grid_y * GRID_SIZE
        
        # Use images if available, otherwise fall back to shapes
        if ghost_images:
            # Choose the appropriate image based on ghost state
            if self.eaten:
                image = ghost_images["EATEN"]
            elif self.frightened:
                if self.flashing:
                    image = ghost_images["FRIGHTENED_FLASH"] if self.flash_state else ghost_images["FRIGHTENED"]
                else:
                    image = ghost_images["FRIGHTENED"]
            else:
                image = ghost_images[self.name]
            
            # Draw the image
            screen.blit(image, (x, y))
        else:
            # Fallback to shape-based rendering if images aren't available
            # Choose color based on state
            color = self.color
            if self.frightened:
                if self.flashing:
                    # Flash between blue and white
                    color = BLUE_GHOST if self.flash_state else WHITE
                else:
                    color = BLUE_GHOST
            elif self.eaten:
                color = WHITE
            
            # Draw ghost body as a circle
            pygame.draw.circle(screen, color, (x + GRID_SIZE//2, y + GRID_SIZE//2), GRID_SIZE//2)
            
            # If eaten, don't draw eyes
            if self.eaten:
                return
            
            # Draw eyes
            eye_radius = GRID_SIZE // 6
            left_eye_x = x + GRID_SIZE // 3
            right_eye_x = x + 2 * GRID_SIZE // 3
            eye_y = y + GRID_SIZE // 3
            
            pygame.draw.circle(screen, WHITE, (left_eye_x, eye_y), eye_radius)
            pygame.draw.circle(screen, WHITE, (right_eye_x, eye_y), eye_radius)
            
            # Draw pupils based on direction (unless frightened)
            if not self.frightened:
                pupil_radius = eye_radius // 2
                left_pupil_x, right_pupil_x = left_eye_x, right_eye_x
                pupil_y = eye_y
                
                if self.direction == "LEFT":
                    left_pupil_x -= pupil_radius
                    right_pupil_x -= pupil_radius
                elif self.direction == "RIGHT":
                    left_pupil_x += pupil_radius
                    right_pupil_x += pupil_radius
                elif self.direction == "UP":
                    pupil_y -= pupil_radius
                elif self.direction == "DOWN":
                    pupil_y += pupil_radius
                    
                pygame.draw.circle(screen, BLACK, (left_pupil_x, pupil_y), pupil_radius)
                pygame.draw.circle(screen, BLACK, (right_pupil_x, pupil_y), pupil_radius)

def draw_map():
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            if game_map[y][x] == 1:  # Wall
                pygame.draw.rect(screen, BLUE, rect)
            elif game_map[y][x] == 0:  # Food
                pygame.draw.circle(screen, WHITE, rect.center, GRID_SIZE // 8)
            elif game_map[y][x] == 3:  # Power pellet
                pygame.draw.circle(screen, WHITE, rect.center, GRID_SIZE // 4)
            
            # NEW: Highlight the ghost home area with a subtle border
            if (GHOST_HOME_X_MIN <= x <= GHOST_HOME_X_MAX and 
                GHOST_HOME_Y_MIN <= y <= GHOST_HOME_Y_MAX+1):
                # Draw a thin border around ghost home cells
                border_rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, (100, 100, 100), border_rect, 1)

def check_collision(pacman, ghosts):
    for ghost in ghosts:
        if pacman.grid_x == ghost.grid_x and pacman.grid_y == ghost.grid_y:
            if ghost.frightened:
                # Eat the ghost
                ghost.set_eaten()
                pacman.score += 200
                return False  # No life lost
            elif not ghost.eaten:
                return True  # Life lost
    return False

def reset_positions(pacman, ghosts):
    pacman.grid_x = 9
    pacman.grid_y = 16
    pacman.direction = None
    pacman.moving = False
    pacman.move_counter = 0
    pacman.left_ghost_home = True  # Pacman starts outside the ghost home
    
    # Reset ghost positions
    ghost_positions = [
        (10, 9, RED, "BLINKY"),
        (8, 9, PINK, "PINKY"),
        (10, 10, CYAN, "INKY"),
        (8, 10, ORANGE, "CLYDE")
    ]
    
    for i, ghost in enumerate(ghosts):
        ghost.grid_x, ghost.grid_y, _, _ = ghost_positions[i]
        ghost.direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
        ghost.moving = False
        ghost.frightened = False
        ghost.flashing = False
        ghost.eaten = False
        ghost.move_counter = 0
        ghost.left_ghost_home = False  # Reset this flag when respawning
        
        # Reset ghost speeds
        if ghost.name == "BLINKY":
            ghost.speed = 6
        elif ghost.name == "PINKY" or ghost.name == "INKY":
            ghost.speed = 6
        else:  # CLYDE
            ghost.speed = 6

def draw_score(score, lives, remaining_food, ai):
    font = pygame.font.SysFont(None, 24)
    score_text = font.render(f"Score: {score}", True, WHITE)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    food_text = font.render(f"Food: {remaining_food}", True, WHITE)
    algo_text = font.render(f"Algo: {ai.get_current_mode()}", True, WHITE)
    screen.blit(score_text, (10, 5))
    screen.blit(lives_text, (WIDTH - 100, 5))
    screen.blit(food_text, (WIDTH // 2 - 40, 5))
    screen.blit(algo_text, (WIDTH - 100, 220))

def draw_ai_mode(screen, ai):
    """
    Affiche le mode actuel de l'IA en vert sur l'écran.
    """
    # Créer une police
    font = pygame.font.Font(None, 24)
    
    # Obtenir le mode actuel
    mode = ai.get_current_mode()
    
    # Créer le texte
    mode_text = font.render(f"Mode: {mode}", True, GREEN)
    
    # Obtenir le rectangle du texte et définir sa position
    text_rect = mode_text.get_rect(topleft=(10, 10))
    
    # Créer un rectangle de fond légèrement plus grand
    background_rect = text_rect.inflate(10, 10)
    
    # Dessiner le fond et le texte
    pygame.draw.rect(screen, BLACK, background_rect)
    screen.blit(mode_text, text_rect)

def main():
    pacman = Pacman()
    
    # Initialiser l'IA de Pacman
    pacman_ai = PacmanAI(depth=3)
    
    # Activer/désactiver l'IA
    use_ai = True
    
    # Create ghosts with different colors and names
    ghosts = [
        Ghost(10, 9, RED, "BLINKY"),
        Ghost(8, 9, PINK, "PINKY"),
        Ghost(10, 10, CYAN, "INKY"),
        Ghost(8, 10, ORANGE, "CLYDE")
    ]
    
    game_over = False
    win = False
    
    # Game instructions
    font = pygame.font.SysFont(None, 24)
    instructions = font.render("Press arrow keys to move / A to toggle AI", True, WHITE)
    
    # Mode timers
    mode_timer = 0
    mode_durations = [
        (SCATTER, 7 * 30),  # 7 seconds at 30 FPS
        (CHASE, 20 * 30),   # 20 seconds at 30 FPS
        (SCATTER, 7 * 30),
        (CHASE, 20 * 30),
        (SCATTER, 5 * 30),
        (CHASE, 20 * 30),
        (SCATTER, 5 * 30),
        (CHASE, float('inf'))  # Permanent chase mode
    ]
    mode_index = 0
    current_mode, mode_duration = mode_durations[mode_index]
    
    # Set initial ghost mode
    for ghost in ghosts:
        ghost.mode = current_mode
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if not game_over and not win:
                    if event.key == pygame.K_a:
                        # Toggle AI
                        use_ai = not use_ai
                        instructions = font.render(f"{'AI active' if use_ai else 'Manual control'} / A to toggle", True, WHITE)
                    
                    # Manual control when AI is off
                    if not use_ai:
                        if event.key == pygame.K_UP:
                            pacman.move("UP")
                        elif event.key == pygame.K_DOWN:
                            pacman.move("DOWN")
                        elif event.key == pygame.K_LEFT:
                            pacman.move("LEFT")
                        elif event.key == pygame.K_RIGHT:
                            pacman.move("RIGHT")
                
                if event.key == pygame.K_r and (game_over or win):
                    # Reset the game
                    game_over = False
                    win = False
                    pacman = Pacman()
                    ghosts = [
                        Ghost(10, 9, RED, "BLINKY"),
                        Ghost(8, 9, PINK, "PINKY"),
                        Ghost(10, 10, CYAN, "INKY"),
                        Ghost(8, 10, ORANGE, "CLYDE")
                    ]
                    # Reset the map (put food back)
                    for y in range(GRID_HEIGHT):
                        for x in range(GRID_WIDTH):
                            if game_map[y][x] == 2:
                                # Check if it was a power pellet position
                                if (x == 3 and y == 3) or (x == 15 and y == 3) or \
                                   (x == 3 and y == 16) or (x == 15 and y == 16):
                                    game_map[y][x] = 3
                                else:
                                    game_map[y][x] = 0
                    
                    # Reset mode timers
                    mode_timer = 0
                    mode_index = 0
                    current_mode, mode_duration = mode_durations[mode_index]
                    for ghost in ghosts:
                        ghost.mode = current_mode
        
        screen.fill(BLACK)
        
        if not game_over and not win:
            # Update mode timer
            mode_timer += 1
            if mode_timer >= mode_duration:
                mode_timer = 0
                mode_index = (mode_index + 1) % len(mode_durations)
                current_mode, mode_duration = mode_durations[mode_index]
                
                # Update ghost modes
                for ghost in ghosts:
                    if not ghost.frightened:  # Don't change mode if frightened
                        ghost.mode = current_mode
                
            
            # AI control
            if use_ai and not pacman.moving:
                # Créer l'état du jeu pour l'IA
                game_state = {
                    "pacman": pacman,
                    "ghosts": ghosts,
                    "game_map": game_map,
                    "ghost_home_coords": (GHOST_HOME_X_MIN, GHOST_HOME_X_MAX, GHOST_HOME_Y_MIN, GHOST_HOME_Y_MAX)
                }
                
                # Obtenir le mouvement de l'IA
                ai_move = pacman_ai.get_move(game_state)
                
                # Appliquer le mouvement
                if ai_move:
                    pacman.move(ai_move)
            # Dessiner le mode de l'IA (après avoir dessiné le jeu mais avant pygame.display.flip())


            # Update pacman
            power_pellet_eaten = pacman.update()
            
            # If a power pellet was eaten, set all ghosts to frightened mode
            if power_pellet_eaten:
                for ghost in ghosts:
                    if not ghost.eaten:  # Don't frighten ghosts that are already eaten
                        ghost.set_frightened(150)  # 5 seconds at 30 FPS
            
            # Update ghosts
            for ghost in ghosts:
                ghost.update(pacman, ghosts)
            
            # Check for collision with ghosts
            if check_collision(pacman, ghosts):
                pacman.lives -= 1
                if pacman.lives <= 0:
                    game_over = True
                else:
                    reset_positions(pacman, ghosts)
            
            # Check if all food is eaten
            remaining_food = sum(row.count(0) for row in game_map) + sum(row.count(3) for row in game_map)
            if remaining_food == 0:
                win = True
        
        # Draw everything
        draw_map()
        pacman.draw()
        
        # Sort ghosts by draw priority (y-position) to fix superposition issue
        sorted_ghosts = sorted(ghosts, key=lambda g: g.draw_priority)
        for ghost in sorted_ghosts:
            ghost.draw()
        
        # Draw score and lives
        remaining_food = sum(row.count(0) for row in game_map) + sum(row.count(3) for row in game_map)
        draw_score(pacman.score, pacman.lives, remaining_food, pacman_ai)
        
        # Draw instructions
        screen.blit(instructions, (WIDTH//2 - instructions.get_width()//2, HEIGHT - 30))
        
        # Draw AI status
        ai_status = font.render(f"AI: {'ON' if use_ai else 'OFF'}", True, WHITE)
        screen.blit(ai_status, (10, 30))
        
        # Draw game over or win message
        if game_over:
            font = pygame.font.SysFont(None, 72)
            game_over_text = font.render("GAME OVER", True, RED)
            screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 36))
            
            font = pygame.font.SysFont(None, 36)
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 36))
        
        if win:
            font = pygame.font.SysFont(None, 72)
            win_text = font.render("YOU WIN!", True, YELLOW)
            screen.blit(win_text, (WIDTH//2 - win_text.get_width()//2, HEIGHT//2 - 36))
            
            font = pygame.font.SysFont(None, 36)
            restart_text = font.render("Press R to restart", True, WHITE)
            screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 36))
        
        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    main()