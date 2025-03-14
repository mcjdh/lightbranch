from core.player import Player
from core.entity import generate_entity, Entity
import random
from collections import deque
from modules.procedural_generator import generate_procedural_map, get_map_type_info

# Keep a small set of predefined maps as fallbacks or starting points
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
    ]
}

# Track game progression
current_level_number = 0
generated_maps = {}

def load_level(level_name):
    """
    Load a specific level map, generating it procedurally if needed.
    
    Args:
        level_name: String identifier for the level
        
    Returns:
        list: 2D list representing the game map
    """
    global generated_maps
    
    # If it's a numbered procedural level
    if level_name.startswith("proc_"):
        try:
            level_num = int(level_name.split("_")[1])
            
            # If we've already generated this level, return it
            if level_name in generated_maps:
                return generated_maps[level_name]
            
            # Otherwise generate a new map
            # Keep size reasonable - start small and increase gradually
            map_size = min(10 + int(level_num * 0.5), 20)  # More conservative size growth
            difficulty = min(0.2 + level_num * 0.05, 0.8)  # More gradual difficulty increase
            
            # Generate a map using a method based on the level number
            gen_method = level_num % 3  # Cycle through different generation methods
            
            # Generate the map with error handling
            try:
                from modules.procedural_generator import generate_procedural_map, validate_map
                new_map = generate_procedural_map(map_size, difficulty, method=gen_method)
                
                # Verify the map is valid
                if not validate_map(new_map):
                    print(f"Generated map for {level_name} is invalid, using fallback")
                    # Use first level as fallback
                    new_map = game_maps["level1"]
            except Exception as e:
                print(f"Error generating map: {e}, using fallback")
                new_map = game_maps["level1"]
            
            # Store the generated map
            generated_maps[level_name] = new_map
            return new_map
        except Exception as e:
            print(f"Error in procedural level loading: {e}, using fallback level")
            return game_maps["level1"]  # Fallback to level1
    
    # Otherwise use predefined maps as fallbacks
    elif level_name in game_maps:
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
    # For procedural maps, the levels are now infinite
    return ["proc_" + str(i) for i in range(current_level_number + 1)] + list(game_maps.keys())

def transition_to_new_level(current_level):
    """
    Transition to a new procedurally generated level.
    
    Args:
        current_level: String identifier of the current level
        
    Returns:
        tuple: (new_game_map, new_level_name, new_player, new_entity)
    """
    global current_level_number
    
    # Extract level number if it's a procedural level
    if current_level.startswith("proc_"):
        try:
            current_level_number = int(current_level.split("_")[1])
        except (IndexError, ValueError):
            current_level_number = 0
    
    # Create the next procedural level
    next_level_number = current_level_number + 1
    next_level = f"proc_{next_level_number}"
    
    # Generate the new map
    new_game_map = load_level(next_level)
    
    # Create a new player at a valid starting position
    new_player = Player()
    new_player.current_map = new_game_map  # Ensure player has reference to new map
    
    # Place player in a good starting position
    place_player_in_valid_position(new_player, new_game_map)
    
    # Generate a new entity for the new level with map reference
    # Try to place it near but not too near the player
    new_entity = generate_entity_for_level_transition(new_game_map, new_player)
    
    # Get information about the map type to potentially customize gameplay
    map_type, features = get_map_type_info(next_level)
    print(f"Entering {map_type} map with features: {features}")
    
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
    try:
        # Try to find an open area, preferring the edges
        map_height = len(game_map)
        map_width = len(game_map[0])
        
        # Try edges first
        edge_positions = []
        for y in [1, map_height - 2]:
            for x in range(1, map_width - 1):
                if y < len(game_map) and x < len(game_map[0]) and game_map[y][x] == 0 and count_open_neighbors(game_map, x, y) >= 2:
                    edge_positions.append((x + 0.5, y + 0.5))
        
        for x in [1, map_width - 2]:
            for y in range(1, map_height - 1):
                if y < len(game_map) and x < len(game_map[0]) and game_map[y][x] == 0 and count_open_neighbors(game_map, x, y) >= 2:
                    edge_positions.append((x + 0.5, y + 0.5))
        
        if edge_positions:
            player.pos_x, player.pos_y = random.choice(edge_positions)
            print(f"Player positioned at edge: ({player.pos_x}, {player.pos_y})")
            return
            
        # Fall back to any open spot
        valid_positions = []
        for y in range(1, map_height-1):
            for x in range(1, map_width-1):
                if game_map[y][x] == 0:
                    valid_positions.append((x + 0.5, y + 0.5))
                    
        if valid_positions:
            player.pos_x, player.pos_y = random.choice(valid_positions)
            print(f"Player positioned at ({player.pos_x}, {player.pos_y})")
            return
    
    except Exception as e:
        print(f"Error placing player: {e}, using fallback position")
    
    # Last resort - use a known safe position
    player.pos_x, player.pos_y = 1.5, 1.5
    print("Using fallback player position")

def count_open_neighbors(game_map, x, y):
    """Count the number of open (non-wall) neighboring cells."""
    count = 0
    for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
        nx, ny = x + dx, y + dy
        if (0 <= nx < len(game_map[0]) and 
            0 <= ny < len(game_map) and 
            game_map[ny][nx] == 0):
            count += 1
    return count

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
