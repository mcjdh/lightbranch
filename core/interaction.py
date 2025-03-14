import pygame

def show_interaction_prompt(screen, prompt_text, choices, width, height):
    """
    Display an interaction prompt with choices.
    
    Args:
        screen: Pygame surface to draw on
        prompt_text: The main prompt text
        choices: List of choices (strings)
        width: Screen width
        height: Screen height
    
    Returns:
        None
    """
    # Create a semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Semi-transparent black
    screen.blit(overlay, (0, 0))
    
    # Create fonts
    prompt_font = pygame.font.SysFont(None, 48)
    choice_font = pygame.font.SysFont(None, 36)
    
    # Render prompt text
    prompt_surface = prompt_font.render(prompt_text, True, (255, 255, 255))
    prompt_rect = prompt_surface.get_rect(center=(width // 2, height // 2 - 50))
    screen.blit(prompt_surface, prompt_rect)
    
    # Render choices
    choice_spacing = 40
    for i, choice in enumerate(choices):
        choice_surface = choice_font.render(choice, True, (255, 255, 255))
        choice_rect = choice_surface.get_rect(
            center=(width // 2, height // 2 + 20 + i * choice_spacing)
        )
        screen.blit(choice_surface, choice_rect)
    
    # Update display immediately to show prompt
    pygame.display.flip()

def process_interaction_choice(key):
    """
    Process the player's choice from keyboard input.
    
    Args:
        key: The pressed key
    
    Returns:
        str: 'yes', 'no', or None if no valid choice made
    """
    if key == pygame.K_y:
        return 'yes'
    elif key == pygame.K_n:
        return 'no'
    else:
        return None
