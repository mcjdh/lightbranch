import pygame

def render_scene(screen, wall_data, width, height):
    """Render the scene using the raycasting data."""
    # Define colors - moved to constants for better performance
    CEILING_COLOR = (50, 50, 80)
    FLOOR_COLOR = (80, 80, 80)
    
    # Wall colors lookup table (type -> [side0_color, side1_color])
    WALL_COLORS = {
        1: [(200, 0, 0), (150, 0, 0)],     # Red walls
        2: [(0, 200, 0), (0, 150, 0)],     # Green walls
        3: [(0, 0, 200), (0, 0, 150)],     # Blue walls
        # Default handled separately
    }
    DEFAULT_COLORS = [(158, 158, 158), (100, 100, 100)]
    
    # Draw ceiling and floor in one pass each
    pygame.draw.rect(screen, CEILING_COLOR, (0, 0, width, height // 2))
    pygame.draw.rect(screen, FLOOR_COLOR, (0, height // 2, width, height // 2))
    
    # Draw walls efficiently
    for data in wall_data:
        x, draw_start, draw_end = data['x'], data['draw_start'], data['draw_end']
        strip_height = draw_end - draw_start
        
        if strip_height <= 0:  # Skip zero-height strips
            continue
            
        # Get base color based on wall type and side
        wall_type, side = data['wall_type'], data['side']
        color = WALL_COLORS.get(wall_type, DEFAULT_COLORS)[side]
        
        # Apply distance shading
        distance_factor = min(5.0 / data['perp_wall_dist'], 1.0) if data['perp_wall_dist'] > 0 else 1.0
        color = [int(c * distance_factor) for c in color]
        
        # Draw the wall strip in a single operation
        pygame.draw.rect(screen, color, (x, draw_start, 1, strip_height))

def draw_minimap(screen, player, game_map, width, height, entities=None):
    """Draw a minimap in the corner of the screen."""
    # Minimap settings
    minimap_size = 150
    cell_size = minimap_size // max(len(game_map), len(game_map[0]))
    map_x, map_y = width - minimap_size - 10, 10
    
    # Draw background
    pygame.draw.rect(screen, (50, 50, 50), (map_x, map_y, minimap_size, minimap_size))
    
    # Draw walls individually
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            if game_map[y][x] > 0:  # Only draw walls
                wall_rect = pygame.Rect(
                    map_x + x * cell_size, 
                    map_y + y * cell_size,
                    cell_size - 1, 
                    cell_size - 1
                )
                pygame.draw.rect(screen, (200, 200, 200), wall_rect, 0)
    
    # Draw entities
    if entities:
        for entity in entities:
            entity_x = map_x + int(entity.x * cell_size)
            entity_y = map_y + int(entity.y * cell_size)
            pygame.draw.circle(screen, entity.color, (entity_x, entity_y), 3)
    
    # Draw player position and direction
    player_x = map_x + int(player.pos_x * cell_size)
    player_y = map_y + int(player.pos_y * cell_size)
    pygame.draw.circle(screen, (255, 0, 0), (player_x, player_y), 3)
    pygame.draw.line(screen, (255, 255, 0), 
                    (player_x, player_y),
                    (player_x + int(player.dir_x * 10), player_y + int(player.dir_y * 10)), 
                    2)

def display_fps(screen, clock):
    """Display the current FPS on screen."""
    # Use a static font to avoid recreating it every frame
    if not hasattr(display_fps, "font"):
        display_fps.font = pygame.font.SysFont(None, 24)
    
    fps_text = display_fps.font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))
