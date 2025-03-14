from core.player import Player
from core.entity import generate_entity

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
    
    # Generate a new entity for the new level
    new_entity = generate_entity(new_game_map)
    
    return new_game_map, next_level, new_player, new_entity
