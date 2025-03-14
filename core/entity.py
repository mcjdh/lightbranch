import math
import random
import pygame

class Entity:
    def __init__(self, x, y, color, current_map=None):
        # Position on the map
        self.x = x
        self.y = y
        # Color of the entity
        self.color = color
        # Size of the entity (for collision detection)
        self.radius = 0.25
        # Height of the entity (relative to walls)
        self.height = 0.6
        # Add interaction properties
        self.is_looked_at = False
        self.interaction_distance = 3.0  # Maximum distance for interaction
        self.prompt_shown = False
        # Sprite data for rendering
        self.sprite_width = 32
        self.sprite_height = 64
        # Fixed screen position (updated during rendering)
        self.screen_x = 0
        self.screen_y = 0
        self.on_screen = False
        # Store reference to current map for collision detection
        self.current_map = current_map

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

def render_entity(screen, player, entity, wall_data, width, height):
    """
    Render the entity using raycasting perspective with improved stability.
    
    Args:
        screen: Pygame surface to draw on
        player: Player object containing position and direction
        entity: Entity object to render
        wall_data: List of dictionaries containing wall rendering data
        width: Screen width
        height: Screen height
    """
    # If entity has no map reference, update it
    if entity.current_map is None and player.current_map is not None:
        entity.current_map = player.current_map
        print("Updated entity map reference")
    
    # Calculate vector from player to entity
    dx = entity.x - player.pos_x
    dy = entity.y - player.pos_y
    
    # Calculate distance from player to entity (squared for efficiency in comparisons)
    distance_squared = dx*dx + dy*dy
    distance = math.sqrt(distance_squared)
    
    # Skip if too close to avoid rendering issues
    if distance < 0.1:
        entity.on_screen = False
        return
    
    # Calculate angle between entity and player's direction
    # Transform entity with the inverse camera matrix
    inv_det = 1.0 / (player.plane_x * player.dir_y - player.dir_x * player.plane_y)
    
    transform_x = inv_det * (player.dir_y * dx - player.dir_x * dy)
    transform_y = inv_det * (-player.plane_y * dx + player.plane_x * dy)
    
    # Entity is behind the camera
    if transform_y <= 0.1:
        entity.on_screen = False
        return
    
    # Calculate the screen position using perspective projection
    entity_screen_x = int((width / 2) * (1 + transform_x / transform_y))
    
    # Calculate height on screen
    entity_height = abs(int(height / transform_y * entity.height))
    entity_width = entity_height // 2  # Adjust aspect ratio as needed
    
    # Calculate vertical start and end positions
    draw_start_y = height // 2 - entity_height // 2
    draw_end_y = height // 2 + entity_height // 2
    
    # Ensure we stay within screen bounds
    if draw_start_y < 0: draw_start_y = 0
    if draw_end_y >= height: draw_end_y = height - 1
    
    # Calculate horizontal bounds
    half_width = entity_width // 2
    draw_start_x = entity_screen_x - half_width
    draw_end_x = entity_screen_x + half_width
    
    # Ensure horizontal bounds are within screen
    if draw_start_x < 0: draw_start_x = 0
    if draw_end_x >= width: draw_end_x = width - 1
    
    # Update entity's screen position for interaction checks
    entity.screen_x = entity_screen_x
    entity.screen_y = height // 2
    entity.on_screen = draw_end_x >= 0 and draw_start_x < width
    
    # Only continue if entity is on screen
    if not entity.on_screen:
        return
    
    # Draw the entity by vertical strips
    for stripe in range(draw_start_x, draw_end_x + 1):
        if 0 <= stripe < width and stripe < len(wall_data):
            # Only draw if in front of wall
            wall_dist = wall_data[stripe].get('perp_wall_dist', float('inf'))
            if transform_y < wall_dist:
                # Apply distance shading
                distance_factor = min(8.0 / transform_y, 1.0)
                
                # Main color with distance shading
                shaded_color = [int(c * distance_factor) for c in entity.color]
                
                # Draw the vertical strip
                pygame.draw.line(screen, shaded_color, (stripe, draw_start_y), (stripe, draw_end_y), 1)
                
                # Draw outline on entity edges for better visibility
                if (stripe == draw_start_x or stripe == draw_end_x or 
                    abs(stripe - entity_screen_x) <= 1):
                    outline_color = [min(c + 50, 255) for c in shaded_color]  # Lighter outline
                    pygame.draw.line(screen, outline_color, (stripe, draw_start_y), (stripe, draw_end_y), 1)

def is_player_looking_at_entity(player, entity, wall_data, width, height):
    """
    Check if player is looking directly at entity using improved accuracy.
    
    Args:
        player: Player object containing position and direction
        entity: Entity object
        wall_data: List of dictionaries containing wall rendering data
        width: Screen width
        height: Screen height
    
    Returns:
        bool: True if player is looking at the entity, False otherwise
    """
    # If entity is not on screen, player can't be looking at it
    if not entity.on_screen:
        return False
    
    # Calculate vector from player to entity
    dx = entity.x - player.pos_x
    dy = entity.y - player.pos_y
    
    # Calculate distance to entity
    distance = math.sqrt(dx * dx + dy * dy)
    
    # If entity is too far, player can't be looking at it
    if distance > entity.interaction_distance:
        return False
    
    # Check if the entity is near the center of the screen
    center_x = width // 2
    
    # Calculate the targeting range based on distance
    # Closer entities need more precise targeting
    targeting_range = max(width // 20, width // (10 + int(distance * 2))) 
    
    # Check if entity screen position is near center
    if abs(entity.screen_x - center_x) > targeting_range:
        return False
    
    # Find the corresponding wall distance at this screen position
    mid_x = min(width - 1, max(0, entity.screen_x))
    if mid_x < len(wall_data):
        wall_dist = wall_data[mid_x].get('perp_wall_dist', float('inf'))
        
        # If wall is closer than entity, player can't see the entity
        if distance >= wall_dist:
            return False
    
    # Check if there's a wall between player and entity
    step_size = 0.05
    steps = int(distance / step_size)
    
    # Use entity's map reference if available, otherwise fall back to player's
    current_map = entity.current_map if entity.current_map is not None else player.current_map
    
    for i in range(1, steps + 1):
        # Interpolate position between player and entity
        t = i * step_size / distance
        check_x = player.pos_x + dx * t
        check_y = player.pos_y + dy * t
        
        # Check if this position is a wall
        map_x, map_y = int(check_x), int(check_y)
        
        # Skip if out of bounds
        if (map_y < 0 or map_y >= len(current_map) or 
            map_x < 0 or map_x >= len(current_map[0])):
            continue
            
        # If we hit a wall before reaching the entity, can't see it
        if current_map[map_y][map_x] > 0:
            return False
    
    return True
