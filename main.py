import pygame
import sys
from core.player import Player
from core.game import Game
from core.renderer import render_scene, draw_minimap, display_fps
from core.raycast import raycast
from core.entity import Entity, render_entity, generate_entity, is_player_looking_at_entity
from core.interaction import show_interaction_prompt, process_interaction_choice
from modules.level_loader import load_level, get_level_names, transition_to_new_level

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pygame Setup")

# Set up clock for controlling frame rate
clock = pygame.time.Clock()
FPS = 60

# Set initial game map and create game instance
current_level = "level1"
game_map = load_level(current_level)
game = Game(game_map, current_level)

# Create player instance
player = Player()
player.current_map = game_map  # Add this line to track current map in player

# Initialize entity with map reference
entity = generate_entity(game_map)

# Game state variables
interaction_mode = False
fade_alpha = 0
fading_out = False
fading_in = False
transition_requested = False

# Initialize font
pygame.font.init()

# Main game loop
running = True
while running:
    # Calculate delta time for frame-independent movement
    dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if interaction_mode:
                    interaction_mode = False
                else:
                    running = False
            # Toggle fullscreen with F11
            elif event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            # Handle interaction key press (E)
            elif event.key == pygame.K_e and not interaction_mode:
                # Perform raycasting to check if player is looking at entity
                wall_data = raycast(player, game_map, WIDTH, HEIGHT)
                if is_player_looking_at_entity(player, entity, wall_data, WIDTH, HEIGHT):
                    interaction_mode = True
            # Process Y/N choices during interaction
            elif interaction_mode:
                choice = process_interaction_choice(event.key)
                if choice == 'yes':
                    # Begin transition to new level
                    interaction_mode = False
                    fading_out = True
                    transition_requested = True
                elif choice == 'no':
                    interaction_mode = False
    
    # Skip movement processing during interaction mode
    if not interaction_mode and not fading_out and not fading_in:
        # Handle player movement with frame rate independence
        keys = pygame.key.get_pressed()
        move_speed_adjusted = player.move_speed * 60 * dt  # Adjust for framerate
        rot_speed_adjusted = player.rot_speed * 60 * dt
        
        # Temporarily store original speeds
        orig_move_speed = player.move_speed
        orig_rot_speed = player.rot_speed
        
        # Update speeds for this frame
        player.move_speed = move_speed_adjusted
        player.rot_speed = rot_speed_adjusted
        
        # Handle forward/backward movement
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.move(True, game_map)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.move(False, game_map)
        
        # Handle rotation - FIXED: swapped rotation directions
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.rotate(-player.rot_speed)  # Changed from positive to negative
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.rotate(player.rot_speed)   # Changed from negative to positive
        
        # Handle strafing (added feature)
        if keys[pygame.K_q]:
            player.strafe(False, game_map)
        if keys[pygame.K_e]:
            player.strafe(True, game_map)
        
        # Reset to original speeds
        player.move_speed = orig_move_speed
        player.rot_speed = orig_rot_speed
    
    # Perform raycasting to get wall data
    wall_data = raycast(player, game_map, WIDTH, HEIGHT)
    
    # Fill the screen with a color
    screen.fill((0, 0, 0))
    
    # Render the scene using the wall data
    render_scene(screen, wall_data, WIDTH, HEIGHT)
    
    # Render the entity
    render_entity(screen, player, entity, wall_data, WIDTH, HEIGHT)
    
    # Update entity interaction state - AFTER rendering to use accurate screen position
    if not interaction_mode:
        entity.is_looked_at = is_player_looking_at_entity(player, entity, wall_data, WIDTH, HEIGHT)
    
    # Draw minimap with entity
    draw_minimap(screen, player, game_map, WIDTH, HEIGHT, [entity])
    
    # Display FPS counter
    display_fps(screen, clock)
    
    # Show interaction gaze indicator when looking at entity but not in interaction mode
    if entity.is_looked_at and not interaction_mode:
        # Draw a small indicator dot or text at the center of the screen
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 5)
        # Show interaction hint
        font = pygame.font.SysFont(None, 24)
        hint_text = font.render("Press 'E' to interact", True, (255, 255, 255))
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, HEIGHT // 2 + 20))
    
    # Handle interaction mode
    if interaction_mode:
        show_interaction_prompt(screen, "Enter portal?", ["Y - Yes", "N - No"], WIDTH, HEIGHT)
    
    # Handle level transition with fade effect
    if fading_out:
        fade_alpha += 5
        if fade_alpha >= 255:
            fade_alpha = 255
            fading_out = False
            
            if transition_requested:
                # Transition to new level
                print(f"Transitioning from {current_level} to next level...")
                game_map, current_level, player, entity = transition_to_new_level(current_level)
                print(f"Loaded level: {current_level}")
                print(f"Entity position: ({entity.x}, {entity.y})")
                
                # Update references
                player.current_map = game_map
                entity.current_map = game_map
                game.map = game_map
                game.current_level = current_level
                
                # Give the entity a bright color to make it more visible for debugging
                if not entity.color[0] > 180:  # Only if not already bright
                    entity.color = (255, 200, 100)  # Bright orange-yellow
                
                # Check if entity is reachable from player position
                from modules.level_loader import is_path_between
                if is_path_between(game_map, player.pos_x, player.pos_y, entity.x, entity.y):
                    print("Entity is reachable from player position - path confirmed!")
                else:
                    print("WARNING: Entity might not be reachable!")
                
                transition_requested = False
                fading_in = True
        
        # Draw fade overlay
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
    
    if fading_in:
        fade_alpha -= 5
        if fade_alpha <= 0:
            fade_alpha = 0
            fading_in = False
        
        # Draw fade overlay
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        fade_surface.fill((0, 0, 0))
        fade_surface.set_alpha(fade_alpha)
        screen.blit(fade_surface, (0, 0))
    
    # Update the display
    pygame.display.flip()

# Quit Pygame properly
pygame.quit()
sys.exit()
