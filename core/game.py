class Game:
    """Main game class that holds game state and map"""
    def __init__(self, game_map, current_level):
        self.map = game_map
        self.current_level = current_level
