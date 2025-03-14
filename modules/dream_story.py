"""
Dream story generation module for Some Dream game.
Provides procedurally generated dream narratives and tracks story progression.
"""
import random
from collections import defaultdict

# Story state
story_state = {
    "visited_dreams": set(),  # Tracks which dream types player has seen
    "choices_made": {},       # Tracks choices player has made
    "dream_depth": 0,         # How deep into the dream narrative
    "recurring_elements": [], # Elements that recur throughout the dream
    "emotional_state": "neutral", # Current emotional state of the dream
}

# Dream themes with associated narratives and choices
DREAM_THEMES = {
    "falling": {
        "narratives": [
            "You're falling through an endless sky, clouds rushing past you.",
            "The ground approaches rapidly, but you feel strangely calm.",
            "You plummet from a great height, the wind rushing through your hair.",
            "The sensation of falling wakes you with a jolt, but you're still here.",
        ],
        "questions": [
            "Do you try to fly?",
            "Do you accept the fall?",
            "Do you close your eyes?",
            "Do you reach out for something to grab?",
        ],
        "outcomes": {
            "yes": [
                "You spread your arms and begin to glide, the falling transforms into flying.",
                "Your acceptance brings a strange peace as you continue descending.",
                "Darkness envelops you, creating a cocoon of calm in the chaos.",
                "Your hand catches something invisible, stopping your descent instantly.",
            ],
            "no": [
                "You struggle against the inevitable pull downward, tumbling wildly.",
                "Panic sets in as you fight against the fall, your heart racing.",
                "Your eyes remain fixed on the approaching ground, terror mounting.",
                "You curl into yourself, becoming smaller as you continue to fall.",
            ]
        }
    },
    "chase": {
        "narratives": [
            "Something is pursuing you through endless corridors.",
            "Your legs feel heavy as you try to escape what's behind you.",
            "No matter how fast you run, the footsteps behind you stay close.",
            "You hide, holding your breath, as something searches for you.",
        ],
        "questions": [
            "Do you turn to face it?",
            "Do you try to run faster?",
            "Do you call for help?",
            "Do you find a place to hide?",
        ],
        "outcomes": {
            "yes": [
                "You turn, ready to confront your pursuer, but see only shadows.",
                "You push yourself beyond your limits, gaining distance from the threat.",
                "Your voice echoes but someone—or something—responds in the distance.",
                "You discover a perfect hiding spot, tucked away from prying eyes.",
            ],
            "no": [
                "You continue fleeing, the presence behind you growing ever closer.",
                "Your limbs grow heavier, movements becoming sluggish and difficult.",
                "Silence is your only companion as you continue your desperate flight.",
                "Exposed and vulnerable, you keep moving as quietly as possible.",
            ]
        }
    },
    "flying": {
        "narratives": [
            "You're soaring above a landscape of impossible geography.",
            "The sensation of weightlessness fills you with exhilaration.",
            "Wind rushes past as you navigate between towers of cloud.",
            "You hover above your sleeping body, free from physical constraints.",
        ],
        "questions": [
            "Do you fly higher?",
            "Do you look down?",
            "Do you try to reach the horizon?",
            "Do you test your new abilities?",
        ],
        "outcomes": {
            "yes": [
                "You ascend toward the stratosphere, the world becoming tiny below.",
                "Vertigo grips you as you see how far you've come from the ground.",
                "The horizon approaches but seems to extend endlessly before you.",
                "You perform impossible aerial maneuvers, free from physical limitations.",
            ],
            "no": [
                "You maintain your altitude, gliding peacefully through the air.",
                "Your gaze remains fixed ahead, afraid of what looking down might bring.",
                "You circle aimlessly, enjoying the sensation without direction.",
                "You fly cautiously, unsure of the rules governing this strange ability.",
            ]
        }
    },
    "unprepared": {
        "narratives": [
            "You suddenly realize you're in public without proper clothes.",
            "You're taking a test for a class you never attended.",
            "You're performing on stage but don't know any of the lines.",
            "You've arrived at an important meeting completely unprepared.",
        ],
        "questions": [
            "Do you pretend everything is normal?",
            "Do you try to escape the situation?",
            "Do you admit your unpreparedness?",
            "Do you look for help around you?",
        ],
        "outcomes": {
            "yes": [
                "You act with confidence and no one seems to notice anything amiss.",
                "You find an exit, a way out of this embarrassing predicament.",
                "Your honesty is met with unexpected understanding and support.",
                "A friendly face in the crowd nods, offering silent assistance.",
            ],
            "no": [
                "Your discomfort is painfully obvious to everyone around you.",
                "You remain trapped in the situation as anxiety builds.",
                "You fumble forward, trying to hide your lack of preparation.",
                "You stand alone, the weight of expectations crushing you.",
            ]
        }
    },
    "labyrinth": {
        "narratives": [
            "You wander through rooms that impossibly connect to one another.",
            "Doors lead to places that shouldn't exist in the same building.",
            "The hallway extends and contracts as you walk through it.",
            "You recognize this place, but everything is slightly wrong.",
        ],
        "questions": [
            "Do you try to map the impossible space?",
            "Do you follow the strange logic of this place?",
            "Do you look for someone else caught in this maze?",
            "Do you close your eyes and trust intuition?",
        ],
        "outcomes": {
            "yes": [
                "Patterns emerge in the chaos, revealing a hidden order to the space.",
                "By accepting the dream logic, the pathways begin to make sense to you.",
                "You spot another figure in the distance, also searching for a way out.",
                "With eyes closed, your feet carry you confidently forward.",
            ],
            "no": [
                "The more you try to apply reason, the more chaotic the space becomes.",
                "You fight against the dream's rules, becoming more disoriented.",
                "Isolation presses in as you wander the shifting corridors alone.",
                "You stumble forward, eyes open but unseeing of the true path.",
            ]
        }
    },
    "teeth": {
        "narratives": [
            "Your teeth begin to crumble and fall out one by one.",
            "You feel a loose tooth, then another, and another.",
            "Something is wrong with your mouth—teeth shifting and breaking.",
            "You run your tongue over your teeth and feel them disintegrating.",
        ],
        "questions": [
            "Do you try to save the remaining teeth?",
            "Do you seek a mirror to examine yourself?",
            "Do you ask someone nearby for help?",
            "Do you accept this transformation?",
        ],
        "outcomes": {
            "yes": [
                "You cup your hands, collecting the fallen pieces of yourself.",
                "Your reflection reveals something unexpected about your true nature.",
                "A stranger approaches, offering mysterious advice about your condition.",
                "The discomfort fades as you allow yourself to change and transform.",
            ],
            "no": [
                "More teeth loosen and fall, an unstoppable cascade of loss.",
                "You avoid your reflection, afraid of what you might see.",
                "You suffer in isolation, unwilling to reveal your vulnerability.",
                "You fight the change, causing greater pain and discomfort.",
            ]
        }
    }
}

def get_dream_theme_for_level(level_name, game_map=None):
    """
    Determine appropriate dream theme based on level characteristics.
    
    Args:
        level_name: Current level identifier
        game_map: The current game map (for additional analysis)
        
    Returns:
        string: Theme identifier
    """
    themes = list(DREAM_THEMES.keys())
    
    # Extract level number if procedural
    level_num = 0
    if level_name.startswith("proc_"):
        try:
            level_num = int(level_name.split("_")[1])
        except (ValueError, IndexError):
            pass
    
    # If we have a map, try to determine theme from structure
    if game_map:
        # Detect labyrinthine maps
        if level_name.startswith("proc_") and len(game_map) > 12:
            corridors = 0
            open_spaces = 0
            
            # Sample the map to determine its nature
            for y in range(1, len(game_map)-1, 2):
                for x in range(1, len(game_map[0])-1, 2):
                    if game_map[y][x] == 0:
                        # Count adjacent open spaces
                        adjacent_open = 0
                        for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                            nx, ny = x+dx, y+dy
                            if (0 <= nx < len(game_map[0]) and 
                                0 <= ny < len(game_map) and 
                                game_map[ny][nx] == 0):
                                adjacent_open += 1
                        
                        if adjacent_open <= 2:
                            corridors += 1
                        else:
                            open_spaces += 1
            
            if corridors > open_spaces * 2:
                return "labyrinth"
            elif open_spaces > corridors * 2:
                return "flying"
    
    # For specific levels
    if level_name == "level1":
        return "falling"
    
    # Otherwise select based on level number or random if not procedural
    if level_name.startswith("proc_"):
        index = level_num % len(themes)
        theme = themes[index]
        
        # For variety, occasionally override with random theme
        if level_num > 0 and level_num % 3 == 0:
            # Exclude the theme we just used
            available_themes = [t for t in themes if t != theme]
            theme = random.choice(available_themes)
        
        return theme
    else:
        return random.choice(themes)

def get_story_segment(level_name, game_map=None):
    """
    Get a story segment for the current level.
    
    Args:
        level_name: Current level identifier
        game_map: The current game map
        
    Returns:
        dict: Story segment with narrative, question and choices
    """
    global story_state
    
    # Determine the dream theme
    theme = get_dream_theme_for_level(level_name, game_map)
    
    # Track that we've visited this dream theme
    story_state["visited_dreams"].add(theme)
    
    # Increase dream depth
    story_state["dream_depth"] += 1
    
    # Get the theme data
    theme_data = DREAM_THEMES[theme]
    
    # Select narrative and question based on how many times we've seen this theme
    visits = list(story_state["visited_dreams"]).count(theme)
    
    # Get indices, wrapping around if needed
    narrative_index = (visits - 1) % len(theme_data["narratives"])
    question_index = (visits - 1) % len(theme_data["questions"])
    
    # Get the narrative and question
    narrative = theme_data["narratives"][narrative_index]
    question = theme_data["questions"][question_index]
    
    # Extract outcomes for this question
    yes_outcome = theme_data["outcomes"]["yes"][question_index]
    no_outcome = theme_data["outcomes"]["no"][question_index]
    
    # Add recurring elements and adapt based on emotional state
    if story_state["recurring_elements"]:
        element = random.choice(story_state["recurring_elements"])
        if random.random() < 0.3:  # 30% chance to include recurring element
            narrative += f" {element} appears again in the distance."
    
    if story_state["dream_depth"] > 3:
        # Add sense of increasing depth
        narrative = f"Deeper in the dream: {narrative}"
    
    # Format the story segment
    return {
        "theme": theme,
        "narrative": narrative,
        "question": question,
        "yes_outcome": yes_outcome,
        "no_outcome": no_outcome,
        "choices": ["Y - Yes", "N - No"]
    }

def process_story_choice(choice, theme, question_index):
    """
    Process the player's choice and update story state.
    
    Args:
        choice: 'yes' or 'no' 
        theme: Current dream theme
        question_index: Index of the question that was asked
        
    Returns:
        string: Brief response based on choice
    """
    global story_state
    
    # Record the choice
    if theme not in story_state["choices_made"]:
        story_state["choices_made"][theme] = []
    
    story_state["choices_made"][theme].append(choice)
    
    # Update emotional state based on choices pattern
    yes_count = sum(1 for c in story_state["choices_made"].get(theme, []) if c == 'yes')
    no_count = sum(1 for c in story_state["choices_made"].get(theme, []) if c == 'no')
    
    if yes_count > no_count:
        story_state["emotional_state"] = "positive"
    elif no_count > yes_count:
        story_state["emotional_state"] = "negative"
    else:
        story_state["emotional_state"] = "neutral"
    
    # Add recurring elements based on theme and choices
    if theme == "falling" and choice == 'yes':
        story_state["recurring_elements"].append("The sensation of weightlessness")
    elif theme == "chase" and choice == 'no':
        story_state["recurring_elements"].append("The sound of distant footsteps")
    elif theme == "labyrinth" and choice == 'yes':
        story_state["recurring_elements"].append("A mysterious door")
    
    # Limit recurring elements to prevent clutter
    if len(story_state["recurring_elements"]) > 3:
        story_state["recurring_elements"] = story_state["recurring_elements"][-3:]
    
    # Get the appropriate outcome
    theme_data = DREAM_THEMES[theme]
    if choice == 'yes':
        return theme_data["outcomes"]["yes"][question_index]
    else:
        return theme_data["outcomes"]["no"][question_index]

def get_dream_summary():
    """
    Generate a summary of the dream journey so far.
    
    Returns:
        string: Summary of the dream journey
    """
    if story_state["dream_depth"] <= 0:
        return "The dream begins..."
    
    # Generate summary based on visited dreams and choices
    themes_seen = len(story_state["visited_dreams"])
    
    if themes_seen == 0:
        return "Your dream journey is just beginning..."
    
    # Create a summary based on emotional state and depth
    if story_state["emotional_state"] == "positive":
        emotion_text = "Your journey has been mostly hopeful."
    elif story_state["emotional_state"] == "negative":
        emotion_text = "Your path has been filled with anxiety."
    else:
        emotion_text = "Your dream has been a balance of light and dark."
    
    # Add depth indicator
    if story_state["dream_depth"] < 3:
        depth_text = "You are still near the surface of your dream."
    elif story_state["dream_depth"] < 6:
        depth_text = "You are descending deeper into your subconscious."
    else:
        depth_text = "You have journeyed deep into the dream world."
    
    # Add recurring elements if any
    recurring_text = ""
    if story_state["recurring_elements"]:
        recurring_text = f" {random.choice(story_state['recurring_elements'])} seems significant."
    
    return f"{depth_text} {emotion_text}{recurring_text}"

def reset_story():
    """Reset the story state for a new game."""
    global story_state
    story_state = {
        "visited_dreams": set(),
        "choices_made": {},
        "dream_depth": 0,
        "recurring_elements": [],
        "emotional_state": "neutral",
    }
