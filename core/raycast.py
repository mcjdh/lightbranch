def raycast(player, game_map, width, height):
    """
    Perform raycasting for the entire screen width.
    
    Args:
        player: Player object containing position and direction
        game_map: 2D list representing the game map
        width: Screen width
        height: Screen height
    
    Returns:
        list: A list of dictionaries containing wall rendering data for each column
    """
    wall_data = []
    
    # Loop through each screen column
    for x in range(width):
        # Calculate ray position and direction
        # x-coordinate in camera space (from -1 to 1)
        camera_x = 2 * x / width - 1
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
        line_height = int(height / perp_wall_dist) if perp_wall_dist > 0 else height
        
        # Calculate lowest and highest pixel to fill in current stripe
        draw_start = -line_height // 2 + height // 2
        if draw_start < 0:
            draw_start = 0
            
        draw_end = line_height // 2 + height // 2
        if draw_end >= height:
            draw_end = height - 1
            
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
