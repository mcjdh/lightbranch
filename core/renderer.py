import pygame
from core.config import USE_TEXTURES, TEXTURE_SIZE, CEILING_COLOR, FLOOR_COLOR, TEXTURE_DISTANCE_SHADING, FLOOR_TEXTURE_ENABLED

def render_scene(screen, wall_data, width, height, textures=None):
    """Render the scene using the raycasting data with texture support."""
    # Use configuration settings
    use_textures = USE_TEXTURES and textures is not None
    
    # Wall colors lookup table (type -> [side0_color, side1_color])
    WALL_COLORS = {
        1: [(200, 0, 0), (150, 0, 0)],     # Red walls
        2: [(0, 200, 0), (0, 150, 0)],     # Green walls
        3: [(0, 0, 200), (0, 0, 150)],     # Blue walls
        # Default handled separately
    }
    DEFAULT_COLORS = [(158, 158, 158), (100, 100, 100)]
    
    # Draw ceiling and floor
    if use_textures and 'ceiling' in textures and 'floor' in textures and FLOOR_TEXTURE_ENABLED:
        # Use textured ceiling and floor (more computationally expensive)
        render_textured_background(screen, width, height, textures)
    else:
        # Use solid color ceiling and floor
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
        
        if use_textures:
            # Create texture key format: wall_1_0 (type 1, side 0)
            texture_key = f'wall_{wall_type}_{side}'
            
            if texture_key in textures and textures[texture_key]:
                # Draw textured wall strip
                texture = textures[texture_key]
                texture_width = texture.get_width()
                
                # Calculate where on the wall the ray hit
                if side == 0:
                    # Vertical wall hit
                    wall_x = data.get('player_y', 0) + data['perp_wall_dist'] * data.get('ray_dir_y', 0)
                else:
                    # Horizontal wall hit
                    wall_x = data.get('player_x', 0) + data['perp_wall_dist'] * data.get('ray_dir_x', 0)
                wall_x -= int(wall_x)  # Keep fractional part only
                
                # Calculate texture column
                tex_x = int(wall_x * texture_width)
                if (side == 0 and data.get('ray_dir_x', 0) > 0) or (side == 1 and data.get('ray_dir_y', 0) < 0):
                    tex_x = texture_width - tex_x - 1
                
                # Fallback if ray direction not available
                if 'ray_dir_x' not in data:
                    tex_x = x % texture_width
                
                # Create a subsurface for the texture stripe
                try:
                    texture_strip = texture.subsurface((tex_x, 0, 1, texture.get_height()))
                    
                    # Scale the strip to the right height
                    scaled_strip = pygame.transform.scale(texture_strip, (1, strip_height))
                    
                    # Apply distance shading if enabled
                    if TEXTURE_DISTANCE_SHADING:
                        distance_factor = min(5.0 / data['perp_wall_dist'], 1.0) if data['perp_wall_dist'] > 0 else 1.0
                        if distance_factor < 0.99:  # Only modify if significant shading needed
                            # Create a surface to apply shading
                            shaded_strip = scaled_strip.copy()
                            shaded_strip.fill((0, 0, 0, int(255 * (1 - distance_factor))), special_flags=pygame.BLEND_RGBA_MULT)
                            scaled_strip = shaded_strip
                    
                    # Draw it to the screen
                    screen.blit(scaled_strip, (x, draw_start))
                except (ValueError, pygame.error):
                    # Fallback if subsurface fails
                    draw_flat_wall(screen, x, draw_start, strip_height, wall_type, side, data['perp_wall_dist'])
            else:
                # Texture not available, fall back to flat color
                draw_flat_wall(screen, x, draw_start, strip_height, wall_type, side, data['perp_wall_dist'])
        else:
            # Draw flat-colored wall strip when textures are disabled
            draw_flat_wall(screen, x, draw_start, strip_height, wall_type, side, data['perp_wall_dist'])

def draw_flat_wall(screen, x, draw_start, strip_height, wall_type, side, distance):
    """Draw a flat-colored wall strip."""
    # Wall colors lookup
    WALL_COLORS = {
        1: [(200, 0, 0), (150, 0, 0)],     # Red walls
        2: [(0, 200, 0), (0, 150, 0)],     # Green walls
        3: [(0, 0, 200), (0, 0, 150)],     # Blue walls
    }
    DEFAULT_COLORS = [(158, 158, 158), (100, 100, 100)]
    
    color = WALL_COLORS.get(wall_type, DEFAULT_COLORS)[side]
    
    # Apply distance shading
    distance_factor = min(5.0 / distance, 1.0) if distance > 0 else 1.0
    color = [int(c * distance_factor) for c in color]
    
    # Draw the wall strip
    pygame.draw.rect(screen, color, (x, draw_start, 1, strip_height))

def render_textured_background(screen, width, height, textures):
    """Render textured ceiling and floor."""
    # Get ceiling and floor textures
    ceiling_texture = textures.get('ceiling')
    floor_texture = textures.get('floor')
    
    # Only simple implementation for now - scaled texturing
    if ceiling_texture:
        # Scale texture to screen width
        scaled_ceiling = pygame.transform.scale(ceiling_texture, (width, height // 2))
        screen.blit(scaled_ceiling, (0, 0))
    else:
        pygame.draw.rect(screen, CEILING_COLOR, (0, 0, width, height // 2))
    
    if floor_texture:
        # Scale texture to screen width
        scaled_floor = pygame.transform.scale(floor_texture, (width, height // 2))
        screen.blit(scaled_floor, (0, height // 2))
    else:
        pygame.draw.rect(screen, FLOOR_COLOR, (0, height // 2, width, height // 2))

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
