# Import section - add config
from core.config import *
import pygame
import sys
from core.player import Player
from core.game import Game
from core.renderer import render_scene, draw_minimap, display_fps
from core.raycast import raycast
from core.entity import Entity, render_entity, generate_entity, is_player_looking_at_entity
from core.interaction import show_interaction_prompt, process_interaction_choice, show_story_interaction, show_story_outcome
from modules.level_loader import load_level, get_level_names, transition_to_new_level
from core.utils import draw_text, draw_fade_overlay
from modules.dream_story import get_story_segment, process_story_choice, get_dream_summary, reset_story

# Initialize Pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Some Dream")  # Updated game title

# Set up clock for controlling frame rate
clock = pygame.time.Clock()
FPS = DEFAULT_FPS

# Initialize with safer defaults
try:
    # Set initial game map and create game instance
    current_level = "proc_0"  # Start with procedural level 0
    game_map = load_level(current_level)
    
    # Verify map is valid
    if not game_map or len(game_map) == 0 or len(game_map[0]) == 0:
        print("Invalid initial map, falling back to level1")
        current_level = "level1"
        game_map = load_level(current_level)
        
    game = Game(game_map, current_level)

    # Create player instance with better position validation
    player = Player()
    player.current_map = game_map
    
    # Ensure player is in a valid position
    from modules.level_loader import place_player_in_valid_position
    place_player_in_valid_position(player, game_map)
    
    # Initialize entity with map reference and validation
    entity = generate_entity(game_map)
except Exception as e:
    print(f"Error during initialization: {e}, using failsafe settings")
    # Failsafe initialization with predefined map
    current_level = "level1"
    game_map = load_level(current_level)
    game = Game(game_map, current_level)
    player = Player()
    player.current_map = game_map
    entity = generate_entity(game_map)

# Game state variables
interaction_mode = False  # Keep for backward compatibility but will be less used
story_mode = False  # New state for story interaction
story_outcome_mode = False  # New state for showing outcome
current_story_segment = None  # Will hold the current story data
current_outcome = None  # Will hold the outcome text
fade_alpha = 0
fading_out = False
fading_in = False
transition_requested = False

# Initialize font
pygame.font.init()

# Initialize dream story system
reset_story()

# Main game loop
running = True
while running:
    # Calculate delta time for frame-independent movement
    dt = clock.tick(FPS) / 1000.0  # Convert milliseconds to seconds
    
    # Extract the event handling to a separate function or reduce repetition
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if story_outcome_mode:
                    story_outcome_mode = False
                elif story_mode:
                    story_mode = False
                elif interaction_mode:
                    interaction_mode = False
                else:
                    running = False
            # Toggle fullscreen with F11
            elif event.key == pygame.K_F11:
                pygame.display.toggle_fullscreen()
            # Handle interaction key press (E)
            elif event.key == pygame.K_e and not interaction_mode and not story_mode and not story_outcome_mode:
                # Optimization: Only perform raycasting if not already done
                if 'wall_data' not in locals():
                    wall_data = raycast(player, game_map, WIDTH, HEIGHT)
                if is_player_looking_at_entity(player, entity, wall_data, WIDTH, HEIGHT):
                    # Enter story mode first instead of direct interaction
                    story_mode = True
                    current_story_segment = get_story_segment(current_level, game_map)
            # Process Y/N choices during story mode
            elif story_mode and (event.key == pygame.K_y or event.key == pygame.K_n):
                choice = process_interaction_choice(event.key)
                if choice:  # If yes or no was pressed
                    # Process the choice and get outcome
                    theme = current_story_segment["theme"]
                    question_index = current_story_segment["questions"].index(current_story_segment["question"]) if "questions" in current_story_segment else 0
                    current_outcome = process_story_choice(choice, theme, question_index)
                    
                    # Switch to outcome mode
                    story_mode = False
                    story_outcome_mode = True
            # Handle continuing after outcome is shown - UPDATED to auto-transition
            elif story_outcome_mode and event.key == pygame.K_SPACE:
                # After seeing outcome, directly begin transition to next level
                story_outcome_mode = False
                fading_out = True
                transition_requested = True
            # Keep this section for backward compatibility
            elif interaction_mode and (event.key == pygame.K_y or event.key == pygame.K_n):
                choice = process_interaction_choice(event.key)
                if choice == 'yes':
                    # Begin transition to new level
                    interaction_mode = False
                    fading_out = True
                    transition_requested = True
                elif choice == 'no':
                    interaction_mode = False
    
    # Skip movement processing during interaction modes
    if not interaction_mode and not story_mode and not story_outcome_mode and not fading_out and not fading_in:
        # Handle player movement with frame rate independence
        keys = pygame.key.get_pressed()
        
        # Process movement with dt (60 is the target FPS for normalization)
        adjusted_dt = FPS * dt  # Normalize to target FPS
        
        # Combine key checks for more efficient processing - updated controls
        move_keys = (keys[pygame.K_UP] or keys[pygame.K_w], 
                    keys[pygame.K_DOWN] or keys[pygame.K_s])
        rotation_keys = (keys[pygame.K_LEFT], keys[pygame.K_RIGHT])  # Only arrow keys for rotation
        strafe_keys = (keys[pygame.K_a], keys[pygame.K_d])  # A and D for strafing
        
        # Handle movement in groups
        if move_keys[0]:
            player.move_frame_independent(True, game_map, adjusted_dt)
        if move_keys[1]:
            player.move_frame_independent(False, game_map, adjusted_dt)
            
        if rotation_keys[0]:
            player.rotate_frame_independent(-player.rot_speed, adjusted_dt)
        if rotation_keys[1]:
            player.rotate_frame_independent(player.rot_speed, adjusted_dt)
            
        if strafe_keys[0]:
            player.strafe_frame_independent(False, game_map, adjusted_dt)
        if strafe_keys[1]:
            player.strafe_frame_independent(True, game_map, adjusted_dt)
    
    # Perform raycasting once per frame
    wall_data = raycast(player, game_map, WIDTH, HEIGHT)
    
    # Fill the screen with a color
    screen.fill((0, 0, 0))
    
    # Render the scene using the wall data
    render_scene(screen, wall_data, WIDTH, HEIGHT)
    
    # Render the entity
    render_entity(screen, player, entity, wall_data, WIDTH, HEIGHT)
    
    # Update entity interaction state - AFTER rendering to use accurate screen position
    if not interaction_mode and not story_mode:
        entity.is_looked_at = is_player_looking_at_entity(player, entity, wall_data, WIDTH, HEIGHT)
    
    # Draw minimap with entity
    draw_minimap(screen, player, game_map, WIDTH, HEIGHT, [entity])
    
    # Display FPS counter
    display_fps(screen, clock)
    
    # Display dream journey summary
    dream_summary = get_dream_summary()
    draw_text(screen, dream_summary, (WIDTH // 2, 30), 
             centered=True, size=18, color=(200, 200, 255))
    
    # Show interaction gaze indicator when looking at entity but not in interaction mode
    if entity.is_looked_at and not interaction_mode and not story_mode and not story_outcome_mode:
        # Draw a small indicator dot at the center of the screen
        pygame.draw.circle(screen, (255, 255, 255), (WIDTH // 2, HEIGHT // 2), 5)
        # Show interaction hint
        draw_text(screen, "Press 'E' to interact", (WIDTH // 2, HEIGHT // 2 + 20), 
                 centered=True)
    
    # Handle the different interaction modes
    if story_mode and current_story_segment:
        show_story_interaction(screen, current_story_segment, WIDTH, HEIGHT)
    elif story_outcome_mode and current_outcome:
        # Updated prompt to indicate automatic level transition
        show_story_outcome(screen, current_outcome, WIDTH, HEIGHT)
    elif interaction_mode:
        # This should rarely be used now but keep for backward compatibility
        show_interaction_prompt(screen, "Enter the next dream?", ["Y - Yes", "N - No"], WIDTH, HEIGHT)
    
    # Handle level transition with fade effect
    if fading_out or fading_in:
        # Update fade alpha
        fade_alpha += FADE_SPEED if fading_out else -FADE_SPEED
        
        # Check for fade completion
        if fading_out and fade_alpha >= 255:
            fade_alpha = 255
            fading_out = False
            
            if transition_requested:
                # Transition to new level
                print(f"Transitioning from {current_level} to next procedural level...")
                try:
                    game_map, current_level, player, entity = transition_to_new_level(current_level)
                except Exception as e:
                    print(f"Error during level transition: {e}, using fallback level")
                    current_level = "level1" if current_level != "level1" else "proc_0"
                    game_map = load_level(current_level)
                    player = Player()
                    player.current_map = game_map
                    place_player_in_valid_position(player, game_map)
                    entity = generate_entity(game_map)
                
                # Update references
                player.current_map = game_map
                entity.current_map = game_map
                game.map = game_map
                game.current_level = current_level
                
                # Ensure entity is visible
                if not entity.color[0] > 180:
                    entity.color = (255, 200, 100)
                
                # Check path to entity
                from modules.level_loader import is_path_between
                path_exists = is_path_between(game_map, player.pos_x, player.pos_y, entity.x, entity.y)
                print(f"Entity is {'reachable' if path_exists else 'NOT reachable'} from player position")
                
                transition_requested = False
                fading_in = True
        
        elif fading_in and fade_alpha <= 0:
            fade_alpha = 0
            fading_in = False
        
        # Draw fade overlay
        draw_fade_overlay(screen, fade_alpha)
    
    # Update the display
    pygame.display.flip()

# Quit Pygame properly
pygame.quit()
sys.exit()
