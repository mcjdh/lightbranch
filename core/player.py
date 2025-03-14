import math

class Player:
    def __init__(self):
        # Player position
        self.pos_x = 1.5
        self.pos_y = 1.5
        
        # Player direction vector
        self.dir_x = 1.0
        self.dir_y = 0.0
        
        # Camera plane vector
        self.plane_x = 0.0
        self.plane_y = 0.66
        
        # Movement speed
        self.move_speed = 0.05
        
        # Rotation speed
        self.rot_speed = 0.03

    def rotate(self, angle):
        """Rotate the player direction and camera plane vectors by the given angle."""
        # Store old direction vector components
        old_dir_x = self.dir_x
        old_dir_y = self.dir_y
        
        # Rotate direction vector
        self.dir_x = old_dir_x * math.cos(angle) - old_dir_y * math.sin(angle)
        self.dir_y = old_dir_x * math.sin(angle) + old_dir_y * math.cos(angle)
        
        # Store old plane vector components
        old_plane_x = self.plane_x
        old_plane_y = self.plane_y
        
        # Rotate camera plane vector
        self.plane_x = old_plane_x * math.cos(angle) - old_plane_y * math.sin(angle)
        self.plane_y = old_plane_x * math.sin(angle) + old_plane_y * math.cos(angle)
    
    def move(self, forward, game_map):
        """Move the player forward or backward along the direction vector.
        
        Args:
            forward: Boolean, True to move forward, False to move backward
            game_map: 2D list representing the game map
        """
        # Calculate movement direction and distance
        move_step = self.move_speed if forward else -self.move_speed
        
        # Calculate new position
        new_x = self.pos_x + self.dir_x * move_step
        new_y = self.pos_y + self.dir_y * move_step
        
        # Check for collisions with walls
        # Add a small buffer (0.2) to avoid getting too close to walls
        buffer = 0.2
        
        # Only update position if the new position is not inside a wall
        map_x = int(new_x)
        map_y = int(new_y)
        
        # Check if new position is valid (inside map bounds and not in a wall)
        if (0 <= map_x < len(game_map[0]) and 
            0 <= map_y < len(game_map) and 
            game_map[map_y][map_x] == 0):
            
            # Additional collision checks for corners
            if forward:
                # Check a bit ahead in the direction of movement
                check_x = self.pos_x + self.dir_x * (self.move_speed + buffer)
                check_y = self.pos_y + self.dir_y * (self.move_speed + buffer)
            else:
                # Check a bit behind in the direction of movement
                check_x = self.pos_x - self.dir_x * (self.move_speed + buffer)
                check_y = self.pos_y - self.dir_y * (self.move_speed + buffer)
            
            check_map_x = int(check_x)
            check_map_y = int(check_y)
            
            if (0 <= check_map_x < len(game_map[0]) and 
                0 <= check_map_y < len(game_map) and 
                game_map[check_map_y][check_map_x] == 0):
                self.pos_x = new_x
                self.pos_y = new_y
    
    def strafe(self, right, game_map):
        """Move the player sideways (perpendicular to direction vector).
        
        Args:
            right: Boolean, True to strafe right, False to strafe left
            game_map: 2D list representing the game map
        """
        # Calculate perpendicular direction
        strafe_dir_x = -self.dir_y
        strafe_dir_y = self.dir_x
        
        # Adjust direction if strafing left
        if not right:
            strafe_dir_x = -strafe_dir_x
            strafe_dir_y = -strafe_dir_y
        
        # Calculate new position
        new_x = self.pos_x + strafe_dir_x * self.move_speed
        new_y = self.pos_y + strafe_dir_y * self.move_speed
        
        # Check for collisions with walls
        buffer = 0.2
        
        # Only update position if the new position is not inside a wall
        map_x = int(new_x)
        map_y = int(new_y)
        
        # Check if new position is valid
        if (0 <= map_x < len(game_map[0]) and 
            0 <= map_y < len(game_map) and 
            game_map[map_y][map_x] == 0):
            
            # Additional collision checks for corners
            check_x = self.pos_x + strafe_dir_x * (self.move_speed + buffer)
            check_y = self.pos_y + strafe_dir_y * (self.move_speed + buffer)
            
            check_map_x = int(check_x)
            check_map_y = int(check_y)
            
            if (0 <= check_map_x < len(game_map[0]) and 
                0 <= check_map_y < len(game_map) and 
                game_map[check_map_y][check_map_x] == 0):
                self.pos_x = new_x
                self.pos_y = new_y
