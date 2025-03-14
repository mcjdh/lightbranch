import math
import random

class Entity:
    def __init__(self, x, y, color):
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

def generate_entity(game_map):
    """
    Generate an entity with a random position and color.
    
    Args:
        game_map: 2D list representing the game map
        
    Returns:
        Entity: A newly generated entity object
    """
    # Find all valid positions (non-wall cells)
    valid_positions = []
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            # Check if position is not a wall and add some padding to avoid spawning too close to walls
            if game_map[y][x] == 0:
                valid_positions.append((x + 0.5, y + 0.5))
    
    # Select a random position from valid positions
    if valid_positions:
        pos_x, pos_y = random.choice(valid_positions)
        
        # Generate a random color
        random_color = (
            random.randint(100, 255),  # R
            random.randint(100, 255),  # G
            random.randint(100, 255)   # B
        )
        
        return Entity(pos_x, pos_y, random_color)
    
    # Fallback if no valid positions found
    return Entity(1.5, 1.5, (255, 0, 255))

def render_entity(screen, player, entity, wall_data, width, height):
    """
    Render the entity using raycasting perspective.
    
    Args:
        screen: Pygame surface to draw on
        player: Player object containing position and direction
        entity: Entity object to render
        wall_data: List of dictionaries containing wall rendering data
        width: Screen width
        height: Screen height
    """
    # Calculate distance from player to entity
    dx = entity.x - player.pos_x
    dy = entity.y - player.pos_y
    distance = math.sqrt(dx * dx + dy * dy)
    
    if distance < 0.1:  # Avoid division by zero and rendering if too close
        return
    
    # Calculate the angle between player's direction and entity
    angle = math.atan2(dy, dx)
    player_angle = math.atan2(player.dir_y, player.dir_x)
    
    # Adjust angle to be relative to player view
    rel_angle = angle - player_angle
    if rel_angle > math.pi:
        rel_angle -= 2 * math.pi
    elif rel_angle < -math.pi:
        rel_angle += 2 * math.pi
        
    # Check if entity is in field of view
    half_fov = math.atan2(player.plane_y, player.plane_x)
    if abs(rel_angle) > half_fov * 1.5:  # Slightly wider than FOV to avoid pop-in
        return
    
    # Calculate screen x-coordinate for entity
    screen_x = int((0.5 + rel_angle / (2 * half_fov)) * width)
    
    # Calculate entity height on screen
    entity_height = int(height / distance * entity.height)
    
    # Calculate vertical position
    draw_start = (height - entity_height) // 2
    draw_end = draw_start + entity_height
    
    # Ensure draw bounds are within screen
    if draw_start < 0:
        draw_start = 0
    if draw_end >= height:
        draw_end = height - 1
    
    # Calculate entity width on screen
    entity_width = entity_height // 2  # You can adjust this ratio
    
    # Calculate horizontal bounds
    left_bound = max(0, screen_x - entity_width // 2)
    right_bound = min(width - 1, screen_x + entity_width // 2)
    
    # Draw the entity
    for x in range(left_bound, right_bound + 1):
        # Only draw if entity is closer than the wall at this x-coordinate
        if x >= 0 and x < len(wall_data):
            wall_dist = wall_data[x]['perp_wall_dist']
            if distance < wall_dist:
                # Apply distance shading to entity color
                distance_factor = min(8.0 / distance, 1.0)
                shaded_color = [int(c * distance_factor) for c in entity.color]
                
                # Draw entity strip
                import pygame
                pygame.draw.line(screen, shaded_color, (x, draw_start), (x, draw_end), 1)

def is_player_looking_at_entity(player, entity, wall_data, width, height):
    """
    Check if the player is looking at the entity.
    
    Args:
        player: Player object containing position and direction
        entity: Entity object
        wall_data: List of dictionaries containing wall rendering data
        width: Screen width
        height: Screen height
    
    Returns:
        bool: True if player is looking at the entity, False otherwise
    """
    # Calculate vector from player to entity
    dx = entity.x - player.pos_x
    dy = entity.y - player.pos_y
    
    # Calculate distance to entity
    distance = math.sqrt(dx * dx + dy * dy)
    
    # If entity is too far, player can't be looking at it
    if distance > entity.interaction_distance:
        return False
    
    # Calculate angle between player's direction and entity
    player_to_entity_angle = math.atan2(dy, dx)
    player_direction_angle = math.atan2(player.dir_y, player.dir_x)
    
    # Calculate the difference between the angles
    angle_diff = player_to_entity_angle - player_direction_angle
    
    # Normalize the angle difference to be between -pi and pi
    while angle_diff > math.pi:
        angle_diff -= 2 * math.pi
    while angle_diff < -math.pi:
        angle_diff += 2 * math.pi
    
    # Check if entity is in field of view (using a smaller angle for precision)
    half_fov = math.atan2(player.plane_y, player.plane_x)
    if abs(angle_diff) > half_fov * 0.5:  # Using a tighter cone than rendering
        return False
    
    # Check if there are walls between player and entity
    # Find the x-coordinate on screen where the entity would be rendered
    relative_angle = angle_diff / (2 * half_fov)
    screen_x = int((0.5 + relative_angle) * width)
    
    # Check if screen_x is within bounds
    if 0 <= screen_x < width:
        # Get the wall distance at this screen column
        wall_dist = wall_data[screen_x]['perp_wall_dist']
        
        # If the wall is further away than the entity, the player can see the entity
        if distance < wall_dist:
            return True
    
    return False
