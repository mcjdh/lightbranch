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

def show_story_interaction(screen, story_segment, width, height):
    """Display a story interaction with narrative and choice."""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))  # Darker for better text readability
    screen.blit(overlay, (0, 0))
    
    # Get the narrative and question from story segment
    narrative = story_segment["narrative"]
    question = story_segment["question"]
    choices = story_segment["choices"]
    
    # Display narrative text (wrapping if needed)
    lines = wrap_text(narrative, width - 100, 24)
    y_offset = height // 2 - 120
    for line in lines:
        draw_text(screen, line, (width // 2, y_offset), 
                  size=24, centered=True)
        y_offset += 30
    
    # Display question text
    draw_text(screen, question, (width // 2, height // 2 - 30), 
              size=36, centered=True)
    
    # Display choices
    for i, choice in enumerate(choices):
        draw_text(screen, choice, (width // 2, height // 2 + 20 + i * 40),
                 size=30, centered=True)

def show_story_outcome(screen, outcome_text, width, height):
    """Display the outcome of a story choice."""
    # Create a semi-transparent overlay
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    # Display outcome text (wrapping if needed)
    lines = wrap_text(outcome_text, width - 100, 28)
    y_offset = height // 2 - 60
    for line in lines:
        draw_text(screen, line, (width // 2, y_offset), 
                  size=28, centered=True)
        y_offset += 40
    
    # Updated continue prompt to indicate transition
    draw_text(screen, "Press SPACE to continue to the next dream", (width // 2, height // 2 + 100), 
              size=24, centered=True)

def process_interaction_choice(key):
    """Process player's choice from keyboard input."""
    return 'yes' if key == pygame.K_y else 'no' if key == pygame.K_n else None

def wrap_text(text, max_width, font_size):
    """Wrap text to fit within a specified width."""
    # First try to use pygame's font rendering to calculate
    font = pygame.font.SysFont(None, font_size)
    words = text.split(' ')
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        # Get width of the test line
        width = font.size(test_line)[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            # Current line is full, start a new one
            if current_line:  # Avoid empty lines
                lines.append(' '.join(current_line))
            current_line = [word]
    
    # Add the last line
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines
