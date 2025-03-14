import math
import random
import pygame

class Entity:
    """Entity class with optimizations for rendering and interaction."""
    
    # Class variables for shared configuration
    DEFAULT_COLOR = (255, 0, 255)
    
    def __init__(self, x, y, color=None, current_map=None):
        self.x = x
        self.y = y
        self.color = color or self.DEFAULT_COLOR
        self.radius = 0.25
        self.height = 0.6
        self.is_looked_at = False
        self.interaction_distance = 3.0
        self.prompt_shown = False
        self.sprite_width = 32
        self.sprite_height = 64
        self.screen_x = 0
        self.screen_y = 0
        self.on_screen = False
        self.current_map = current_map
    
    def set_random_color(self, bright=False):
        """Set a random color for the entity."""
        min_value = 180 if bright else 100
        self.color = (
            random.randint(min_value, 255),
            random.randint(min_value, 255),
            random.randint(min_value, 255)
        )
        return self

# Keep existing generate_entity function, but simplify using modules/level_loader.py find_valid_positions

def generate_entity(game_map):
    """
    Generate an entity with a valid position and color.
    
    Args:
        game_map: 2D list representing the game map
        
    Returns:
        Entity: A newly generated entity object
    """
    # Find all valid positions (non-wall cells with buffer from walls)
    valid_positions = []
    for y in range(1, len(game_map) - 1):  # Skip border cells
        for x in range(1, len(game_map[y]) - 1):
            # Check if current position and surrounding cells are safe
            if game_map[y][x] == 0:
                # Check if it's not too close to walls
                safe_position = True
                
                # Check surrounding cells in a 3x3 grid
                for check_y in range(y-1, y+2):
                    for check_x in range(x-1, x+2):
                        # Skip corners (diagonal positions)
                        if (check_x != x and check_y != y):
                            continue
                        
                        # If any surrounding cell is a wall, position is not safe
                        if check_y < 0 or check_y >= len(game_map) or check_x < 0 or check_x >= len(game_map[0]) or game_map[check_y][check_x] != 0:
                            safe_position = False
                            break
                
                if safe_position:
                    # Add position with a random offset to avoid grid alignment
                    pos_x = x + random.uniform(0.3, 0.7)
                    pos_y = y + random.uniform(0.3, 0.7)
                    valid_positions.append((pos_x, pos_y))
    
    # Select a random position from valid positions
    if valid_positions:
        pos_x, pos_y = random.choice(valid_positions)
        
        # Generate a random color
        random_color = (
            random.randint(100, 255),  # R
            random.randint(100, 255),  # G
            random.randint(100, 255)   # B
        )
        
        return Entity(pos_x, pos_y, random_color, current_map=game_map)
    
    # Fallback if no valid positions found - try center of a known empty cell
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            if game_map[y][x] == 0:
                return Entity(x + 0.5, y + 0.5, (255, 0, 255), current_map=game_map)
    
    # Ultimate fallback
    return Entity(1.5, 1.5, (255, 0, 255), current_map=game_map)

def is_player_looking_at_entity(player, entity, wall_data, width, height):
    """Optimized check if player is looking at entity."""
    # Early exit conditions combined
    if not entity.on_screen:
        return False
    
    # Distance calculation
    dx, dy = entity.x - player.pos_x, entity.y - player.pos_y
    distance_squared = dx*dx + dy*dy
    
    # Quick square distance check before expensive sqrt
    if distance_squared > entity.interaction_distance * entity.interaction_distance:
        return False
    
    # Only calculate distance if needed
    distance = math.sqrt(distance_squared)
    
    # Check if entity is near center of screen - use proportional tolerance based on distance
    center_x = width // 2
    # Closer entities need more precise targeting
    tolerance = max(width // 20, int(width / (10 + distance * 5)))
    
    if abs(entity.screen_x - center_x) > tolerance:
        return False
    
    # Check if wall is between player and entity - first use raycast data
    mid_x = min(width - 1, max(0, entity.screen_x))
    if mid_x < len(wall_data) and distance >= wall_data[mid_x].get('perp_wall_dist', float('inf')):
        return False
    
    # Optimized ray check - use fewer steps for better performance
    current_map = entity.current_map or player.current_map
    if not current_map:
        return False
        
    # Use 3-5 steps max for performance, but ensure some minimal checking
    step_count = min(max(3, int(distance * 2)), 5)
    
    if step_count > 0:
        step_size = distance / step_count
        for i in range(1, step_count):
            t = i * step_size / distance
            check_x, check_y = int(player.pos_x + dx * t), int(player.pos_y + dy * t)
            
            if (0 <= check_y < len(current_map) and 
                0 <= check_x < len(current_map[0]) and
                current_map[check_y][check_x] > 0):
                return False
    
    return True

def render_entity(screen, player, entity, wall_data, width, height):
    """Render the entity using an optimized approach."""
    # Update entity map reference if needed
    if entity.current_map is None and player.current_map is not None:
        entity.current_map = player.current_map
    
    # Calculate vector and distance from player to entity
    dx, dy = entity.x - player.pos_x, entity.y - player.pos_y
    distance_squared = dx*dx + dy*dy
    
    # Early exit for very close entities (avoid division by zero)
    if distance_squared < 0.01:  # Square distance for efficiency
        entity.on_screen = False
        return
    
    distance = math.sqrt(distance_squared)
    
    # Camera transformation matrix
    inv_det = 1.0 / (player.plane_x * player.dir_y - player.dir_x * player.plane_y)
    transform_x = inv_det * (player.dir_y * dx - player.dir_x * dy)
    transform_y = inv_det * (-player.plane_y * dx + player.plane_x * dy)
    
    if transform_y <= 0.1:  # Behind camera
        entity.on_screen = False
        return
    
    # Screen position and dimensions
    entity_screen_x = int((width / 2) * (1 + transform_x / transform_y))
    entity_height = abs(int(height / transform_y * entity.height))
    entity_width = entity_height // 2
    
    # Calculate bounds with clamping
    draw_start_y = max(0, height // 2 - entity_height // 2)
    draw_end_y = min(height - 1, height // 2 + entity_height // 2)
    draw_start_x = max(0, entity_screen_x - entity_width // 2)
    draw_end_x = min(width - 1, entity_screen_x + entity_width // 2)
    
    entity_width = draw_end_x - draw_start_x + 1
    entity_height = draw_end_y - draw_start_y + 1
    
    # Update entity screen position
    entity.screen_x = entity_screen_x
    entity.screen_y = height // 2
    entity.on_screen = entity_width > 0 and entity_height > 0
    
    if not entity.on_screen:
        return
    
    # Calculate shading once
    distance_factor = min(8.0 / transform_y, 1.0)
    color = [int(c * distance_factor) for c in entity.color]
    outline = [min(c + 50, 255) for c in color]
    
    # Only create a surface if entity is large enough to see
    if entity_width >= 2 and entity_height >= 2:
        # Use direct pixel drawing if entity is small
        if entity_width * entity_height < 1000:  # Arbitrary threshold for small entities
            for stripe in range(draw_start_x, draw_end_x + 1):
                if 0 <= stripe < width and stripe < len(wall_data):
                    if transform_y < wall_data[stripe].get('perp_wall_dist', float('inf')):
                        # Choose color based on whether this is an edge
                        use_color = outline if (stripe == draw_start_x or stripe == draw_end_x or 
                                            abs(stripe - entity_screen_x) <= 1) else color
                        
                        # Draw vertical line directly to screen
                        pygame.draw.line(screen, use_color, (stripe, draw_start_y), (stripe, draw_end_y), 1)
        else:
            # For larger entities, use surface-based rendering
            entity_surface = pygame.Surface((entity_width, entity_height), pygame.SRCALPHA)
            entity_surface.fill((0, 0, 0, 0))  # Transparent
            
            # Process walls in chunks for better performance
            for stripe in range(draw_start_x, draw_end_x + 1):
                if 0 <= stripe < width and stripe < len(wall_data):
                    if transform_y < wall_data[stripe].get('perp_wall_dist', float('inf')):
                        rel_x = stripe - draw_start_x
                        
                        # Choose color based on whether this is an edge
                        use_color = outline if (stripe == draw_start_x or stripe == draw_end_x or 
                                            abs(stripe - entity_screen_x) <= 1) else color
                        
                        # Draw vertical line on surface
                        pygame.draw.line(entity_surface, use_color, (rel_x, 0), (rel_x, entity_height), 1)
            
            # Blit the entity surface to the screen in one operation
            screen.blit(entity_surface, (draw_start_x, draw_start_y))
