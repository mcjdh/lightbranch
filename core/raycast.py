def raycast(player, game_map, width, height):
    """Optimized raycasting function with better performance and texture support."""
    wall_data = []
    map_width, map_height = len(game_map[0]), len(game_map)
    
    # Precalculate constants outside the loop
    height_half = height // 2
    
    for x in range(width):
        # Calculate ray position and direction
        camera_x = 2 * x / width - 1
        ray_dir_x = player.dir_x + player.plane_x * camera_x
        ray_dir_y = player.dir_y + player.plane_y * camera_x
        
        # Starting map position
        map_x, map_y = int(player.pos_x), int(player.pos_y)
        
        # Calculate delta distances - optimized to handle zero cases
        delta_dist_x = 1e30 if ray_dir_x == 0 else abs(1 / ray_dir_x)
        delta_dist_y = 1e30 if ray_dir_y == 0 else abs(1 / ray_dir_y)
        
        # Calculate step and initial side_dist in a more compact way
        step_x = 1 if ray_dir_x >= 0 else -1
        step_y = 1 if ray_dir_y >= 0 else -1
        
        # Calculate initial side distances more concisely
        side_dist_x = (step_x * (map_x + step_x * 0.5 + 0.5 - player.pos_x)) * delta_dist_x if ray_dir_x != 0 else 1e30
        side_dist_y = (step_y * (map_y + step_y * 0.5 + 0.5 - player.pos_y)) * delta_dist_y if ray_dir_y != 0 else 1e30
        if ray_dir_x < 0: side_dist_x = (player.pos_x - map_x) * delta_dist_x
        if ray_dir_y < 0: side_dist_y = (player.pos_y - map_y) * delta_dist_y
        
        # Perform DDA with early exit when hitting map boundaries
        wall_type, side = 0, 0
        while True:
            # Jump to next map square
            if side_dist_x < side_dist_y:
                side_dist_x += delta_dist_x
                map_x += step_x
                side = 0
            else:
                side_dist_y += delta_dist_y
                map_y += step_y
                side = 1
            
            # Exit loop if out of bounds
            if map_x < 0 or map_x >= map_width or map_y < 0 or map_y >= map_height:
                wall_type = 1  # Default wall type for boundaries
                break
                
            # Exit loop if hit wall
            if game_map[map_y][map_x] > 0:
                wall_type = game_map[map_y][map_x]
                break
        
        # Calculate perpendicular wall distance to avoid fisheye effect
        perp_wall_dist = ((map_x - player.pos_x + (1 - step_x) / 2) / ray_dir_x if side == 0 
                         else (map_y - player.pos_y + (1 - step_y) / 2) / ray_dir_y)
        
        # Use a fast integer division and clamping
        line_height = int(height / max(0.001, perp_wall_dist))
        draw_start = max(0, height_half - line_height // 2)
        draw_end = min(height - 1, height_half + line_height // 2)
        
        # Calculate wall hit position for texturing
        if side == 0:
            wall_x = player.pos_y + perp_wall_dist * ray_dir_y
        else:
            wall_x = player.pos_x + perp_wall_dist * ray_dir_x
        wall_x -= int(wall_x)  # Only fractional part
        
        # Store wall data with extended texture information
        wall_data.append({
            'x': x,
            'draw_start': draw_start,
            'draw_end': draw_end,
            'side': side,
            'wall_type': wall_type,
            'perp_wall_dist': perp_wall_dist,
            'ray_dir_x': ray_dir_x,
            'ray_dir_y': ray_dir_y,
            'player_x': player.pos_x,
            'player_y': player.pos_y,
            'wall_x': wall_x  # For texture mapping
        })
    
    return wall_data
