import random
from collections import deque

def generate_procedural_map(size=15, difficulty=0.5, method=0):
    """
    Generate a procedural game map.
    
    Args:
        size: Size of the map (size x size)
        difficulty: 0.0 to 1.0 difficulty factor (higher means more complex maps)
        method: Generation method (0=rooms, 1=cellular, 2=maze-like)
        
    Returns:
        list: 2D list representing the game map
    """
    # Make sure size is reasonable - too large maps might cause performance issues
    size = max(10, min(size, 30))
    
    # Cap difficulty
    difficulty = max(0.1, min(difficulty, 0.9))
    
    try:
        if method == 0:
            return generate_room_based_map(size, difficulty)
        elif method == 1:
            return generate_cellular_automata_map(size, difficulty)
        else:
            return generate_maze_map(size, difficulty)
    except Exception as e:
        # If any generation method fails, return a simple valid map
        print(f"Error in map generation: {e}, returning fallback map")
        return generate_fallback_map(size)

def generate_room_based_map(size, difficulty):
    """Generate a map with connected rooms."""
    # Create empty map (0=floor, 1=wall)
    game_map = [[1 for _ in range(size)] for _ in range(size)]
    
    # Parameters based on difficulty
    min_rooms = max(2, int(3 + difficulty * 4))
    max_rooms = max(min_rooms + 1, int(5 + difficulty * 6))
    min_size = max(2, int(3 - difficulty * 2))
    max_size = max(min_size + 2, int(4 + difficulty * 4))
    
    rooms = []
    num_rooms = random.randint(min_rooms, max_rooms)
    
    # Create rooms
    for _ in range(num_rooms):
        # Room width and height
        w = random.randint(min_size, max_size)
        h = random.randint(min_size, max_size)
        
        # Room position (ensure 1 cell border)
        x = random.randint(1, size - w - 2)
        y = random.randint(1, size - h - 2)
        
        # Check if the room overlaps with any existing room
        overlaps = False
        for room in rooms:
            room_x, room_y, room_w, room_h = room
            if (x < room_x + room_w + 1 and x + w + 1 > room_x and
                y < room_y + room_h + 1 and y + h + 1 > room_y):
                overlaps = True
                break
        
        if not overlaps:
            # Carve the room
            for ry in range(y, y + h):
                for rx in range(x, x + w):
                    game_map[ry][rx] = 0
            
            # Add room to the list
            rooms.append((x, y, w, h))
    
    # Connect rooms with corridors
    if rooms:
        # Sort rooms by position to create a more logical path
        rooms.sort(key=lambda r: r[0] + r[1])
        
        for i in range(len(rooms) - 1):
            # Get center of current and next room
            x1 = rooms[i][0] + rooms[i][2] // 2
            y1 = rooms[i][1] + rooms[i][3] // 2
            x2 = rooms[i+1][0] + rooms[i+1][2] // 2
            y2 = rooms[i+1][1] + rooms[i+1][3] // 2
            
            # Create L-shaped corridor
            if random.choice([True, False]):
                # Horizontal then vertical
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    game_map[y1][x] = 0
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    game_map[y][x2] = 0
            else:
                # Vertical then horizontal
                for y in range(min(y1, y2), max(y1, y2) + 1):
                    game_map[y][x1] = 0
                for x in range(min(x1, x2), max(x1, x2) + 1):
                    game_map[y2][x] = 0
    
    # Make sure borders are walls
    for y in range(size):
        game_map[y][0] = game_map[y][size-1] = 1
    for x in range(size):
        game_map[0][x] = game_map[size-1][x] = 1
    
    # Add wall types for visual interest (1-3)
    for y in range(size):
        for x in range(size):
            if game_map[y][x] == 1:
                # 25% chance of special wall types based on difficulty
                if random.random() < 0.25 * difficulty:
                    game_map[y][x] = random.randint(1, 3)
                    
    return game_map

def generate_cellular_automata_map(size, difficulty):
    """Generate a map using cellular automata (cave-like)."""
    # Initialize with random walls
    wall_probability = 0.4 + difficulty * 0.2
    game_map = [[1 if random.random() < wall_probability else 0 
                for _ in range(size)] for _ in range(size)]
    
    # Ensure borders are walls
    for y in range(size):
        game_map[y][0] = game_map[y][size-1] = 1
    for x in range(size):
        game_map[0][x] = game_map[size-1][x] = 1
    
    # Run cellular automata iterations
    iterations = 4 + int(difficulty * 3)
    for _ in range(iterations):
        new_map = [row[:] for row in game_map]
        
        for y in range(1, size - 1):
            for x in range(1, size - 1):
                # Count walls in 3x3 neighborhood
                walls = sum(game_map[ny][nx] > 0 
                           for nx in range(x-1, x+2) 
                           for ny in range(y-1, y+2))
                
                # Apply cellular automata rules
                if game_map[y][x] > 0:  # Wall
                    new_map[y][x] = 1 if walls >= 4 else 0
                else:  # Floor
                    new_map[y][x] = 1 if walls >= 5 else 0
        
        game_map = new_map
    
    # Ensure map connectivity
    ensure_connectivity(game_map)
    
    # Add wall types for visual interest
    for y in range(size):
        for x in range(size):
            if game_map[y][x] == 1:
                # 30% chance of special wall types
                if random.random() < 0.3:
                    game_map[y][x] = random.randint(1, 3)
    
    return game_map

def generate_maze_map(size, difficulty):
    """Generate a maze-like map using randomized depth-first search."""
    # Create a map filled with walls
    game_map = [[1 for _ in range(size)] for _ in range(size)]
    
    # Choose a random starting point (must be odd coordinates)
    start_x = random.randrange(1, size-1, 2)
    start_y = random.randrange(1, size-1, 2)
    game_map[start_y][start_x] = 0
    
    # Stack for backtracking
    stack = [(start_x, start_y)]
    
    # Directions: (dx, dy)
    directions = [(0, -2), (2, 0), (0, 2), (-2, 0)]
    
    while stack:
        x, y = stack[-1]
        
        # Find unvisited neighbors
        unvisited = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if (1 <= nx < size-1 and 1 <= ny < size-1 and game_map[ny][nx] == 1):
                unvisited.append((nx, ny, dx, dy))
        
        if unvisited:
            # Choose a random unvisited neighbor
            nx, ny, dx, dy = random.choice(unvisited)
            
            # Remove the wall between current and chosen cells
            game_map[y + dy//2][x + dx//2] = 0
            game_map[ny][nx] = 0
            
            # Push the chosen cell to the stack
            stack.append((nx, ny))
        else:
            # Backtrack
            stack.pop()
    
    # Create some random extra passages for better gameplay (based on difficulty)
    extra_passages = int((size * size) * 0.05 * difficulty)
    for _ in range(extra_passages):
        x = random.randint(1, size-2)
        y = random.randint(1, size-2)
        if game_map[y][x] == 1:
            game_map[y][x] = 0
    
    # Ensure map connectivity after adding random passages
    ensure_connectivity(game_map)
    
    # Add wall types for visual interest
    for y in range(size):
        for x in range(size):
            if game_map[y][x] == 1:
                # 35% chance of special wall types
                if random.random() < 0.35:
                    game_map[y][x] = random.randint(1, 3)
    
    return game_map

def ensure_connectivity(game_map):
    """Ensure all open spaces in the map are connected."""
    size = len(game_map)
    visited = [[False for _ in range(size)] for _ in range(size)]
    
    # Find first open space
    start_x, start_y = None, None
    for y in range(size):
        for x in range(size):
            if game_map[y][x] == 0:
                start_x, start_y = x, y
                break
        if start_x is not None:
            break
    
    if start_x is None:  # No open spaces
        return
    
    # Perform BFS from the starting point
    queue = deque([(start_x, start_y)])
    visited[start_y][start_x] = True
    
    while queue:
        x, y = queue.popleft()
        
        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if (0 <= nx < size and 0 <= ny < size and 
                game_map[ny][nx] == 0 and not visited[ny][nx]):
                visited[ny][nx] = True
                queue.append((nx, ny))
    
    # Identify disconnected regions and connect them
    for y in range(1, size-1):
        for x in range(1, size-1):
            # FIX: Use x instead of nx (which was undefined)
            if game_map[y][x] == 0 and not visited[y][x]:
                # Found a disconnected region, connect it to the main region
                best_distance = float('inf')
                best_point = None
                
                # Find closest visited open space
                for vy in range(size):
                    for vx in range(size):
                        if game_map[vy][vx] == 0 and visited[vy][vx]:
                            distance = (vx - x)**2 + (vy - y)**2
                            if distance < best_distance:
                                best_distance = distance
                                best_point = (vx, vy)
                
                if best_point:
                    # Create a path between the points
                    ax, ay = x, y
                    bx, by = best_point
                    
                    # Mark the start point as visited to avoid infinite loops
                    visited[ay][ax] = True
                    
                    # Limit the number of steps to avoid infinite loops
                    max_steps = size * 2
                    steps = 0
                    
                    while ((ax != bx) or (ay != by)) and steps < max_steps:
                        steps += 1
                        if random.random() < 0.5 and ax != bx:
                            ax += 1 if ax < bx else -1
                        elif ay != by:
                            ay += 1 if ay < by else -1
                        elif ax != bx:  # Ensure we move even if the random choice didn't work
                            ax += 1 if ax < bx else -1
                        
                        if 0 <= ax < size and 0 <= ay < size:  # Bounds check
                            game_map[ay][ax] = 0
                            visited[ay][ax] = True  # Mark as visited

def generate_fallback_map(size):
    """Generate a simple, guaranteed-valid map for fallback cases."""
    # Create a map with walls around the edges and open in the middle
    game_map = [[1 for _ in range(size)] for _ in range(size)]
    
    # Create a simple open area in the middle
    for y in range(1, size-1):
        for x in range(1, size-1):
            # Create a basic grid pattern with some open areas
            if (x % 3 != 1) or (y % 3 != 1):  # Leave some walls for structure
                game_map[y][x] = 0
    
    # Make sure the map is connected
    ensure_safe_connectivity(game_map)
    
    return game_map

def ensure_safe_connectivity(game_map):
    """A simplified, robust version of ensure_connectivity for emergency use."""
    size = len(game_map)
    
    # First make sure there's at least one open path from edge to edge
    middle = size // 2
    
    # Create horizontal and vertical paths
    for x in range(1, size-1):
        game_map[middle][x] = 0
    
    for y in range(1, size-1):
        game_map[y][middle] = 0
        
    # Add a few random connections
    for _ in range(size):
        x = random.randint(1, size-2)
        y = random.randint(1, size-2)
        game_map[y][x] = 0

def get_map_type_info(level_name):
    """
    Return information about the map's type and features based on level name.
    
    Args:
        level_name: The level identifier
        
    Returns:
        tuple: (map_type, features_dict)
    """
    # For procedural levels, determine info based on level number
    if level_name.startswith("proc_"):
        try:
            level_num = int(level_name.split("_")[1])
            map_types = ["Chambers", "Caves", "Labyrinth"]
            
            # Cycle through map types
            map_type = map_types[level_num % len(map_types)]
            
            # Determine special features
            features = {}
            
            # Every third level has special walls
            if level_num % 3 == 0:
                features["special_walls"] = True
            
            # Increasing complexity with level number
            features["complexity"] = min(level_num / 10, 1.0)
            
            return map_type, features
            
        except (IndexError, ValueError):
            pass
    
    # Default for predefined maps
    return "Standard", {"predefined": True}

def validate_map(game_map):
    """Validate that a map is properly formed and has open spaces."""
    if not game_map or not game_map[0]:
        return False
        
    # Check that the map has at least some open spaces
    has_open = False
    for row in game_map:
        if 0 in row:
            has_open = True
            break
            
    return has_open
