import pygame
from core.utils import draw_text

def show_interaction_prompt(screen, prompt_text, choices, width, height):
    """Display an interaction prompt with choices."""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))
    screen.blit(overlay, (0, 0))
    
    # Render prompt text
    draw_text(screen, prompt_text, (width // 2, height // 2 - 50), 
              size=48, centered=True)
    
    # Render choices
    for i, choice in enumerate(choices):
        draw_text(screen, choice, (width // 2, height // 2 + 20 + i * 40),
                 size=36, centered=True)

def process_interaction_choice(key):
    """Process player's choice from keyboard input."""
    return 'yes' if key == pygame.K_y else 'no' if key == pygame.K_n else None
