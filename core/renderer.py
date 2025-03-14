import pygame

def render_scene(screen, wall_data, width, height):
    """
    Render the scene using the raycasting data.
    
    Args:
        screen: Pygame surface to draw on
        wall_data: List of dictionaries containing wall rendering data
        width: Screen width
        height: Screen height
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
    pygame.draw.rect(screen, ceiling_color, (0, 0, width, height // 2))
    pygame.draw.rect(screen, floor_color, (0, height // 2, width, height // 2))
    
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

def draw_minimap(screen, player, game_map, width, height, entities=None):
    """
    Draw a minimap in the corner of the screen.
    
    Args:
        screen: Pygame surface to draw on
        player: Player object containing position
        game_map: 2D list representing the game map
        width: Screen width
        height: Screen height
        entities: Optional list of entity objects to draw on minimap
    """
    # Minimap settings
    minimap_size = 150
    minimap_cell_size = minimap_size // max(len(game_map), len(game_map[0]))
    minimap_x = width - minimap_size - 10
    minimap_y = 10
    
    # Draw background
    pygame.draw.rect(screen, (50, 50, 50), 
                    (minimap_x, minimap_y, minimap_size, minimap_size))
    
    # Draw map cells
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            cell_color = (200, 200, 200) if game_map[y][x] > 0 else (0, 0, 0)
            pygame.draw.rect(screen, cell_color, 
                            (minimap_x + x * minimap_cell_size, 
                             minimap_y + y * minimap_cell_size, 
                             minimap_cell_size - 1, minimap_cell_size - 1))
    
    # Draw entities on minimap if provided
    if entities:
        for entity in entities:
            entity_x = minimap_x + int(entity.x * minimap_cell_size)
            entity_y = minimap_y + int(entity.y * minimap_cell_size)
            pygame.draw.circle(screen, entity.color, (entity_x, entity_y), 2)
    
    # Draw player position
    player_x = minimap_x + int(player.pos_x * minimap_cell_size)
    player_y = minimap_y + int(player.pos_y * minimap_cell_size)
    pygame.draw.circle(screen, (255, 0, 0), (player_x, player_y), 3)
    
    # Draw player direction
    dir_end_x = player_x + int(player.dir_x * 10)
    dir_end_y = player_y + int(player.dir_y * 10)
    pygame.draw.line(screen, (255, 255, 0), (player_x, player_y), (dir_end_x, dir_end_y), 2)

def display_fps(screen, clock):
    """
    Display the current FPS on screen.
    
    Args:
        screen: Pygame surface to draw on
        clock: Pygame clock object
    """
    font = pygame.font.SysFont(None, 24)
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255, 255, 255))
    screen.blit(fps_text, (10, 10))
