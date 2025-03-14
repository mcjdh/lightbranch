"""Configuration settings for the game engine."""

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
DEFAULT_FPS = 60
FULLSCREEN = False

# Player settings
PLAYER_MOVE_SPEED = 0.05
PLAYER_ROT_SPEED = 0.03
PLAYER_COLLISION_BUFFER = 0.2

# Minimap settings
MINIMAP_SIZE = 150
MINIMAP_POSITION = (10, 10)  # (x, y) from top right

# Rendering settings
RENDER_DISTANCE = 20  # Maximum distance to render
WALL_COLORS = {
    1: [(200, 0, 0), (150, 0, 0)],     # Red walls (N/S, E/W)
    2: [(0, 200, 0), (0, 150, 0)],     # Green walls
    3: [(0, 0, 200), (0, 0, 150)],     # Blue walls
}
DEFAULT_WALL_COLOR = [(158, 158, 158), (100, 100, 100)]
CEILING_COLOR = (50, 50, 80)  # Dark blue
FLOOR_COLOR = (80, 80, 80)    # Gray

# Entity settings
ENTITY_INTERACTION_DISTANCE = 3.0
ENTITY_HEIGHT = 0.6
ENTITY_BRIGHTNESS = {
    'normal': (100, 100, 100),
    'bright': (180, 180, 180),
}

# Level transition settings
FADE_SPEED = 5  # Alpha change per frame
