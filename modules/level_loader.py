from core.player import Player
from core.entity import generate_entity, Entity
import random
from collections import deque

# Define the game maps for different levels
game_maps = {
    "level1": [
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
    ],
    "level2": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 1, 0, 1],
        [1, 1, 1, 1, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ],
    "level3": [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
    ]
}

def load_level(level_name):
    """
    Load a specific level map.
    
    Args:
        level_name: String identifier for the level
        
    Returns:
        list: 2D list representing the game map
    """
    if level_name in game_maps:
        return game_maps[level_name]
    else:
        # Return default level if the requested one doesn't exist
        return game_maps["level1"]

def get_level_names():
    """
    Get the list of available level names.
    
    Returns:
        list: List of level names
    """
    return list(game_maps.keys())

def transition_to_new_level(current_level):
    """
    Transition to a new level by selecting a different map.
    
    Args:
        current_level: String identifier of the current level
        
    Returns:
        tuple: (new_game_map, new_level_name, new_player, new_entity)
    """
    # Get the list of available levels
    available_levels = get_level_names()
    
    # Find the current level index
    current_index = available_levels.index(current_level)
    
    # Move to the next level (with wrapping)
    next_index = (current_index + 1) % len(available_levels)
    next_level = available_levels[next_index]
    
    # Get the new map
    new_game_map = load_level(next_level)
    
    # Create a new player at a valid starting position
    new_player = Player()
    new_player.current_map = new_game_map  # Ensure player has reference to new map
    
    # Place player in a good starting position
    place_player_in_valid_position(new_player, new_game_map)
    
    # Generate a new entity for the new level with map reference
    # Try to place it near but not too near the player
    new_entity = generate_entity_for_level_transition(new_game_map, new_player)
    
    return new_game_map, next_level, new_player, new_entity

def is_path_between(game_map, start_x, start_y, end_x, end_y):
    """
    Check if there is a valid path between two points on the map.
    Uses breadth-first search algorithm.
    
    Args:
        game_map: 2D list representing the game map
        start_x, start_y: Starting position
        end_x, end_y: Ending position
        
    Returns:
        bool: True if there is a path, False otherwise
    """
    # Convert to integer coordinates for grid-based search
    start_x, start_y = int(start_x), int(start_y)
    end_x, end_y = int(end_x), int(end_y)
    
    # Check if start or end positions are walls
    if (game_map[start_y][start_x] != 0 or 
        game_map[end_y][end_x] != 0):
        return False
    
    # Directions: up, right, down, left
    directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    
    # Create a visited map
    visited = [[False for _ in range(len(game_map[0]))] for _ in range(len(game_map))]
    visited[start_y][start_x] = True
    
    # Queue for BFS
    queue = deque([(start_x, start_y)])
    
    while queue:
        x, y = queue.popleft()
        
        # Check if we've reached the destination
        if x == end_x and y == end_y:
            return True
        
        # Try all four directions
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            
            # Check if the new position is valid
            if (0 <= nx < len(game_map[0]) and 
                0 <= ny < len(game_map) and 
                game_map[ny][nx] == 0 and 
                not visited[ny][nx]):
                visited[ny][nx] = True
                queue.append((nx, ny))
    
    # If we've searched everywhere and didn't find a path
    return False

def find_valid_positions(game_map, min_dist_from_walls=0, min_dist_from_player=0, max_dist_from_player=None, player=None):
    """
    Find valid positions on the map based on various criteria.
    
    Args:
        game_map: 2D list representing the game map
        min_dist_from_walls: Minimum tiles away from walls
        min_dist_from_player: Minimum distance from player
        max_dist_from_player: Maximum distance from player
        player: Player object (required if min/max_dist_from_player > 0)
        
    Returns:
        list: List of (x, y) valid positions
    """
    valid_positions = []
    
    for y in range(min_dist_from_walls, len(game_map) - min_dist_from_walls):
        for x in range(min_dist_from_walls, len(game_map[y]) - min_dist_from_walls):
            if game_map[y][x] != 0:  # Skip wall tiles
                continue
                
            # Check surrounding cells if needed
            if min_dist_from_walls > 0:
                too_close_to_wall = False
                
                for ny in range(y-min_dist_from_walls, y+min_dist_from_walls+1):
                    for nx in range(x-min_dist_from_walls, x+min_dist_from_walls+1):
                        if (ny < 0 or ny >= len(game_map) or nx < 0 or nx >= len(game_map[0]) or 
                            game_map[ny][nx] != 0):
                            too_close_to_wall = True
                            break
                    if too_close_to_wall:
                        break
                
                if too_close_to_wall:
                    continue
            
            # Calculate position with offset to avoid grid alignment
            pos_x = x + 0.5  # Center of tile
            pos_y = y + 0.5
            
            # Check distance from player if specified
            if player and (min_dist_from_player > 0 or max_dist_from_player):
                dx = pos_x - player.pos_x
                dy = pos_y - player.pos_y
                dist = (dx**2 + dy**2)**0.5
                
                if (min_dist_from_player > 0 and dist < min_dist_from_player) or \
                   (max_dist_from_player and dist > max_dist_from_player):
                    continue
                    
                # Check path to player if needed
                if min_dist_from_player > 0 and not is_path_between(game_map, player.pos_x, player.pos_y, pos_x, pos_y):
                    continue
            
            valid_positions.append((pos_x, pos_y))
    
    return valid_positions

def place_player_in_valid_position(player, game_map):
    """Place the player in a valid position in the new level."""
    valid_positions = find_valid_positions(game_map, min_dist_from_walls=1)
    
    if valid_positions:
        player.pos_x, player.pos_y = random.choice(valid_positions)
        print(f"Player positioned at ({player.pos_x}, {player.pos_y})")
    else:
        # Fallback to any empty cell
        for y in range(len(game_map)):
            for x in range(len(game_map[y])):
                if game_map[y][x] == 0:
                    player.pos_x = x + 0.5
                    player.pos_y = y + 0.5
                    return

def generate_entity_for_level_transition(game_map, player):
    """Generate an entity in a valid position that's reachable from the player."""
    # Find positions good for entities (not too close, not too far from player)
    valid_positions = find_valid_positions(game_map, min_dist_from_walls=0, 
                                          min_dist_from_player=2.0, 
                                          max_dist_from_player=7.0, 
                                          player=player)
    
    if valid_positions:
        # Choose a position
        pos_x, pos_y = random.choice(valid_positions)
        
        # Generate a bright color for better visibility
        random_color = (
            random.randint(180, 255),  # R (brighter)
            random.randint(150, 255),  # G
            random.randint(100, 255)   # B
        )
        
        print(f"Entity spawned at ({pos_x:.2f}, {pos_y:.2f})")
        return Entity(pos_x, pos_y, random_color, current_map=game_map)
    
    # If no good position found, fall back to manual placement
    print("No ideal entity position found. Using fallback position...")
    return place_entity_at_fallback_position(game_map, player)

def place_entity_at_fallback_position(game_map, player):
    """
    Place entity at a predefined fallback position for each level type.
    
    Args:
        game_map: 2D list representing the game map
        player: Player object
        
    Returns:
        Entity: An entity at a valid fallback position
    """
    # Try to identify the level type by comparing with known maps
    for level_name, level_map in game_maps.items():
        if game_map == level_map:
            print(f"Using fallback position for {level_name}")
            
            # Predefined fallback positions for each level
            fallback_positions = {
                "level1": (8.5, 8.5),
                "level2": (3.5, 8.5),
                "level3": (8.5, 8.5)
            }
            
            if level_name in fallback_positions:
                pos_x, pos_y = fallback_positions[level_name]
                
                # Verify this position is empty
                if game_map[int(pos_y)][int(pos_x)] == 0:
                    # Create entity with bright color
                    entity_color = (255, 200, 100)  # Bright orange
                    print(f"Entity placed at fallback position ({pos_x}, {pos_y})")
                    return Entity(pos_x, pos_y, entity_color, current_map=game_map)
    
    # If all else fails, try to find any empty space far from the player
    empty_positions = []
    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            if game_map[y][x] == 0:
                pos_x = x + 0.5
                pos_y = y + 0.5
                distance = ((pos_x - player.pos_x)**2 + (pos_y - player.pos_y)**2)**0.5
                if distance > 3.0:  # Ensure some minimum distance
                    empty_positions.append((pos_x, pos_y, distance))
    
    if empty_positions:
        # Choose the farthest position
        empty_positions.sort(key=lambda p: -p[2])  # Sort by distance descending
        pos_x, pos_y, _ = empty_positions[0]
        entity_color = (255, 100, 255)  # Bright pink for last-resort fallback
        print(f"Entity placed at last-resort position ({pos_x}, {pos_y})")
        return Entity(pos_x, pos_y, entity_color, current_map=game_map)
    
    # Absolute last resort - a fixed position
    print("WARNING: Using fixed position for entity!")
    return Entity(1.5, 1.5, (255, 0, 0), current_map=game_map)
