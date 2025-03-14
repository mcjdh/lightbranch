import pygame
import sys
import math

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Setup")

# Set up clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Define the game map (10x10 grid)
# 1 represents walls, 0 represents empty spaces
game_map = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 0, 1, 1, 0, 0, 1, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 1, 0, 1, 0, 1],
    [1, 0, 1, 0, 1, 1, 0, 0, 0, 1],
    [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 1, 1, 1, 0, 1, 0, 1],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
]

# Define the player object
class Player:
    def __init__(self):
        # Player position
        self.pos_x = 1.5
        self.pos_y = 1.5
        
        # Player direction vector
        self.dir_x = 1.0
        self.dir_y = 0.0
        
        # Camera plane vector
        self.plane_x = 0.0
        self.plane_y = 0.66
        
        # Movement speed
        self.move_speed = 0.05
        
        # Rotation speed
        self.rot_speed = 0.03

    def rotate(self, angle):
        """Rotate the player direction and camera plane vectors by the given angle."""
        # Store old direction vector components
        old_dir_x = self.dir_x
        old_dir_y = self.dir_y
        
        # Rotate direction vector
        self.dir_x = old_dir_x * math.cos(angle) - old_dir_y * math.sin(angle)
        self.dir_y = old_dir_x * math.sin(angle) + old_dir_y * math.cos(angle)
        
        # Store old plane vector components
        old_plane_x = self.plane_x
        old_plane_y = self.plane_y
        
        # Rotate camera plane vector
        self.plane_x = old_plane_x * math.cos(angle) - old_plane_y * math.sin(angle)
        self.plane_y = old_plane_x * math.sin(angle) + old_plane_y * math.cos(angle)
    
    def move(self, forward, game_map):
        """Move the player forward or backward along the direction vector.
        
        Args:
            forward: Boolean, True to move forward, False to move backward
            game_map: 2D list representing the game map
        """
        # Calculate movement direction and distance
        move_step = self.move_speed if forward else -self.move_speed
        
        # Calculate new position
        new_x = self.pos_x + self.dir_x * move_step
        new_y = self.pos_y + self.dir_y * move_step
        
        # Check for collisions with walls
        # Add a small buffer (0.2) to avoid getting too close to walls
        buffer = 0.2
        
        # Only update position if the new position is not inside a wall
        map_x = int(new_x)
        map_y = int(new_y)
        
        # Check if new position is valid (inside map bounds and not in a wall)
        if (0 <= map_x < len(game_map[0]) and 
            0 <= map_y < len(game_map) and 
            game_map[map_y][map_x] == 0):
            
            # Additional collision checks for corners
            if forward:
                # Check a bit ahead in the direction of movement
                check_x = self.pos_x + self.dir_x * (self.move_speed + buffer)
                check_y = self.pos_y + self.dir_y * (self.move_speed + buffer)
            else:
                # Check a bit behind in the direction of movement
                check_x = self.pos_x - self.dir_x * (self.move_speed + buffer)
                check_y = self.pos_y - self.dir_y * (self.move_speed + buffer)
            
            check_map_x = int(check_x)
            check_map_y = int(check_y)
            
            if (0 <= check_map_x < len(game_map[0]) and 
                0 <= check_map_y < len(game_map) and 
                game_map[check_map_y][check_map_x] == 0):
                self.pos_x = new_x
                self.pos_y = new_y

# Create player instance
player = Player()

def raycast(player, game_map):
    """
    Perform raycasting for the entire screen width.
    
    Args:
        player: Player object containing position and direction
        game_map: 2D list representing the game map
    
    Returns:
        list: A list of dictionaries containing wall rendering data for each column
    """
    wall_data = []
    
    # Loop through each screen column
    for x in range(WIDTH):
        # Calculate ray position and direction
        # x-coordinate in camera space (from -1 to 1)
        camera_x = 2 * x / WIDTH - 1
        ray_dir_x = player.dir_x + player.plane_x * camera_x
        ray_dir_y = player.dir_y + player.plane_y * camera_x
        
        # Which map cell the player is currently in
        map_x = int(player.pos_x)
        map_y = int(player.pos_y)
        
        # Length of ray from current position to next x or y-side
        side_dist_x = 0
        side_dist_y = 0
        
        # Length of ray from one x or y-side to next x or y-side
        try:
            delta_dist_x = abs(1 / ray_dir_x)
        except ZeroDivisionError:
            delta_dist_x = 1e30  # Very large number
        
        try:
            delta_dist_y = abs(1 / ray_dir_y)
        except ZeroDivisionError:
            delta_dist_y = 1e30  # Very large number
        
        # Direction to step in x or y direction (either +1 or -1)
        step_x = 1 if ray_dir_x >= 0 else -1
        step_y = 1 if ray_dir_y >= 0 else -1
        
        # Calculate step and initial side_dist
        if ray_dir_x < 0:
            step_x = -1
            side_dist_x = (player.pos_x - map_x) * delta_dist_x
        else:
            step_x = 1
            side_dist_x = (map_x + 1.0 - player.pos_x) * delta_dist_x
            
        if ray_dir_y < 0:
            step_y = -1
            side_dist_y = (player.pos_y - map_y) * delta_dist_y
        else:
            step_y = 1
            side_dist_y = (map_y + 1.0 - player.pos_y) * delta_dist_y
            
        # Perform DDA (Digital Differential Analysis)
        hit = 0  # Was there a wall hit?
        side = 0  # Was a NS or a EW wall hit?
        
        while hit == 0:
            # Jump to next map square, either in x-direction, or in y-direction
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
                
            # Check if ray has hit a wall
            if map_x < 0 or map_x >= len(game_map[0]) or map_y < 0 or map_y >= len(game_map):
                hit = 1  # Hit map boundary
            elif game_map[map_y][map_x] > 0:
                hit = 1  # Hit a wall
                wall_type = game_map[map_y][map_x]  # Store the wall type
        
        # Calculate distance projected on camera direction
        if side == 0:
            perp_wall_dist = (map_x - player.pos_x + (1 - step_x) / 2) / ray_dir_x
        else:
            perp_wall_dist = (map_y - player.pos_y + (1 - step_y) / 2) / ray_dir_y
            
        # Calculate height of line to draw on screen
        line_height = int(HEIGHT / perp_wall_dist) if perp_wall_dist > 0 else HEIGHT
        
        # Calculate lowest and highest pixel to fill in current stripe
        draw_start = -line_height // 2 + HEIGHT // 2
        if draw_start < 0:
            draw_start = 0
            
        draw_end = line_height // 2 + HEIGHT // 2
        if draw_end >= HEIGHT:
            draw_end = HEIGHT - 1
            
        # Store the data for this wall strip
        wall_data.append({
            'x': x,
            'draw_start': draw_start,
            'draw_end': draw_end,
            'side': side,
            'wall_type': wall_type if hit else 0,
            'perp_wall_dist': perp_wall_dist
        })
    
    return wall_data

def render_scene(screen, wall_data):
    """
    Render the scene using the raycasting data.
    
    Args:
        screen: Pygame surface to draw on
        wall_data: List of dictionaries containing wall rendering data
    """
    # Define colors
    ceiling_color = (50, 50, 80)  # Dark blue
    floor_color = (80, 80, 80)    # Gray
    
    # Define wall colors based on wall type and side
    wall_colors = {
        1: [(200, 0, 0), (150, 0, 0)],     # Red walls (lighter for N/S, darker for E/W)
        2: [(0, 200, 0), (0, 150, 0)],     # Green walls
        3: [(0, 0, 200), (0, 0, 150)],     # Blue walls
    }
    
    # Default colors if wall_type not in wall_colors
    default_colors = [(158, 158, 158), (100, 100, 100)]
    
    # Draw ceiling and floor
    pygame.draw.rect(screen, ceiling_color, (0, 0, WIDTH, HEIGHT // 2))
    pygame.draw.rect(screen, floor_color, (0, HEIGHT // 2, WIDTH, HEIGHT // 2))
    
    # Draw each wall strip
    for data in wall_data:
        x = data['x']
        draw_start = data['draw_start']
        draw_end = data['draw_end']
        side = data['side']
        wall_type = data['wall_type']
        
        # Choose color based on wall type and side
        if wall_type in wall_colors:
            color = wall_colors[wall_type][side]
        else:
            color = default_colors[side]
        
        # Draw wall strip as a rectangle
        strip_height = draw_end - draw_start
        if strip_height > 0:  # Avoid drawing strips with no height
            pygame.draw.rect(screen, color, (x, draw_start, 1, strip_height))
        
        # Optional: Add distance shading to create depth perception
        # The further away the wall, the darker it appears
        perp_wall_dist = data['perp_wall_dist']
        if perp_wall_dist > 0:
            # Limit the distance factor to avoid completely black walls
            distance_factor = min(5.0 / perp_wall_dist, 1.0)
            shaded_color = [int(c * distance_factor) for c in color]
            pygame.draw.rect(screen, shaded_color, (x, draw_start, 1, strip_height))

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
    
    # Handle player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_UP] or keys[pygame.K_w]:
        player.move(True, game_map)
    if keys[pygame.K_DOWN] or keys[pygame.K_s]:
        player.move(False, game_map)
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        player.rotate(player.rot_speed)
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        player.rotate(-player.rot_speed)
    
    # Fill the screen with a color
    screen.fill((0, 0, 0))
    
    # Perform raycasting to get wall data
    wall_data = raycast(player, game_map)
    
    # Render the scene using the wall data
    render_scene(screen, wall_data)
    
    # Update the display
    pygame.display.flip()
    
    # Control the frame rate
    clock.tick(FPS)

# Quit Pygame properly
pygame.quit()
sys.exit()
