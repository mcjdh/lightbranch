"""
Dream story generation module for Some Dream game.
Provides procedurally generated dream narratives and tracks story progression.
"""
import random
import os
import json
from collections import defaultdict

# Story state - kept for backwards compatibility
story_state = {
    "visited_dreams": set(),  # Tracks which dream types player has seen
    "choices_made": {},       # Tracks choices player has made
    "dream_depth": 0,         # How deep into the dream narrative
    "recurring_elements": [], # Elements that recur throughout the dream
    "emotional_state": "neutral", # Current emotional state of the dream
}

# Create a DreamManager class to handle dream story generation
class DreamManager:
    """Manages dream narratives and story progression."""
    
    def __init__(self):
        # Initialize with existing story state for backward compatibility
        self.state = story_state
        self.themes = {}
        # Add dream summary cache to fix glitchy text
        self._dream_summary_cache = "The dream begins..."
        self._last_summary_state = {
            "dream_depth": 0,
            "emotional_state": "neutral",
            "recurring_elements": [],
            "visited_dreams": set()
        }
        self._load_theme_data()
    
    def _load_theme_data(self):
        """Load theme data from built-in themes and external JSON files."""
        from . import dream_themes_builtin
        
        # First load built-in themes from the module
        self.themes = dream_themes_builtin.DREAM_THEMES.copy()
        
        # Then try to load additional themes from files if they exist
        theme_dir = os.path.join(os.path.dirname(__file__), 'dream_themes')
        if os.path.exists(theme_dir):
            for filename in os.listdir(theme_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(theme_dir, filename), 'r') as f:
                            new_theme = json.load(f)
                            theme_id = filename.split('.')[0]
                            
                            # Validate theme structure
                            if self._validate_theme(new_theme):
                                self.themes[theme_id] = new_theme
                                print(f"Loaded dream theme: {theme_id}")
                            else:
                                print(f"Invalid theme structure in {filename}")
                    except Exception as e:
                        print(f"Error loading dream theme {filename}: {e}")
        
        print(f"Total dream themes loaded: {len(self.themes)}")
    
    def _validate_theme(self, theme):
        """Validate that a theme has the required structure."""
        required_keys = ["narratives", "questions", "outcomes"]
        outcome_keys = ["yes", "no"]
        
        # Check basic structure
        if not all(key in theme for key in required_keys):
            return False
            
        # Check that outcomes contains yes/no
        if not all(key in theme["outcomes"] for key in outcome_keys):
            return False
            
        # Check that lists have content and matching lengths
        if (len(theme["narratives"]) == 0 or
            len(theme["questions"]) == 0 or
            len(theme["outcomes"]["yes"]) != len(theme["questions"]) or
            len(theme["outcomes"]["no"]) != len(theme["questions"])):
            return False
            
        return True
    
    # Add the missing _analyze_map_features method
    def _analyze_map_features(self, game_map):
        """Analyze map features to determine appropriate themes."""
        features = {
            "corridors": 0,
            "open_spaces": 0,
            "enclosed_areas": 0,
            "verticality": 0
        }
        
        # Skip if map is too small
        if len(game_map) <= 5 or len(game_map[0]) <= 5:
            return features
            
        # Sample the map to determine its nature
        for y in range(1, len(game_map)-1, 2):
            for x in range(1, len(game_map[0])-1, 2):
                if game_map[y][x] == 0:  # If it's an open space
                    # Count adjacent open spaces
                    adjacent_open = 0
                    for dx, dy in [(0,1), (1,0), (0,-1), (-1,0)]:
                        nx, ny = x+dx, y+dy
                        if (0 <= nx < len(game_map[0]) and 
                            0 <= ny < len(game_map) and 
                            game_map[ny][nx] == 0):
                            adjacent_open += 1
                    
                    if adjacent_open <= 1:
                        features["enclosed_areas"] += 1
                    elif adjacent_open == 2:
                        features["corridors"] += 1
                    else:
                        features["open_spaces"] += 1
        
        return features
    
    def get_theme_for_level(self, level_name, game_map=None):
        """Select an appropriate dream theme based on level characteristics."""
        themes = list(self.themes.keys())
        if not themes:
            print("WARNING: No dream themes available!")
            return None
        
        # Extract level number if procedural
        level_num = 0
        if level_name.startswith("proc_"):
            try:
                level_num = int(level_name.split("_")[1])
            except (ValueError, IndexError):
                pass
        
        # Use map structure to influence theme selection
        if game_map:
            map_features = self._analyze_map_features(game_map)
            
            # Choose theme based on map features
            if map_features["corridors"] > map_features["open_spaces"] * 1.5:
                labyrinthine_themes = [t for t in themes if t in ["labyrinth", "chase", "mansion"]]
                if labyrinthine_themes:
                    return self._weighted_theme_choice(labyrinthine_themes, base_weight=0.7)
            elif map_features["open_spaces"] > map_features["corridors"] * 1.5:
                open_themes = [t for t in themes if t in ["flying", "falling", "floating", "water"]]
                if open_themes:
                    return self._weighted_theme_choice(open_themes, base_weight=0.7)
            elif map_features["enclosed_areas"] > map_features["corridors"]:
                enclosed_themes = [t for t in themes if t in ["teeth", "unprepared", "nature", "classroom"]]
                if enclosed_themes:
                    return self._weighted_theme_choice(enclosed_themes, base_weight=0.7)
        
        # For specific levels
        if level_name == "level1":
            if "falling" in themes:
                return "falling"
            else:
                return random.choice(themes)
        
        # Avoid repeating recent themes
        if len(self.state["visited_dreams"]) > 0:
            recent_themes = list(self.state["visited_dreams"])[-2:]
            available_themes = [t for t in themes if t not in recent_themes]
            
            if available_themes:
                # Group themes by emotional tone for smarter selection
                theme_categories = self._categorize_themes()
                
                # Select based on emotional state
                if self.state["emotional_state"] == "positive":
                    positive_themes = theme_categories.get("positive", [])
                    if positive_themes and random.random() < 0.6:  # 60% chance to match emotion
                        return self._weighted_theme_choice(
                            [t for t in positive_themes if t in available_themes] or available_themes
                        )
                elif self.state["emotional_state"] == "negative":
                    negative_themes = theme_categories.get("negative", [])
                    if negative_themes and random.random() < 0.6:
                        return self._weighted_theme_choice(
                            [t for t in negative_themes if t in available_themes] or available_themes
                        )
                
                # Otherwise select from all available
                return self._weighted_theme_choice(available_themes)
        
        # Use procedural selection based on level number
        if level_name.startswith("proc_"):
            # Use level number to seed the selection, but add randomness
            base_index = level_num % len(themes)
            
            # For some levels, pick completely randomly for variety
            if level_num > 0 and random.random() < 0.3:
                return random.choice(themes)
            
            # Otherwise use a weighted selection around the base index
            weights = {}
            for i, theme in enumerate(themes):
                # Higher weight for the base theme, lower for others
                distance = min(abs(i - base_index), len(themes) - abs(i - base_index))
                weights[theme] = 1.0 - (distance * 0.2)
            
            return self._weighted_theme_choice(themes, weights=weights)
        else:
            # For non-procedural levels, use random selection
            return random.choice(themes)
            
    # Add the missing _weighted_theme_choice method
    def _weighted_theme_choice(self, themes, weights=None, base_weight=0.5):
        """Make a weighted random choice from available themes."""
        if not themes:
            return random.choice(list(self.themes.keys()))
        
        # Use provided weights or equal weighting
        theme_weights = {}
        
        # Check if weights is a number (backward compatibility) or a dict
        if isinstance(weights, (int, float)):
            base_weight = weights
            weights = None
        
        for theme in themes:
            if weights and theme in weights:
                theme_weights[theme] = weights[theme]
            else:
                theme_weights[theme] = base_weight
        
        # Normalize weights
        total = sum(theme_weights.values())
        if total > 0:  # Avoid division by zero
            for theme in theme_weights:
                theme_weights[theme] /= total
        else:
            # If all weights are zero, use equal weights
            for theme in theme_weights:
                theme_weights[theme] = 1.0 / len(theme_weights)
        
        # Make weighted choice
        r = random.random()
        cumulative = 0
        for theme, weight in theme_weights.items():
            cumulative += weight
            if r <= cumulative:
                return theme
        
        # Fallback
        return random.choice(themes)
    
    def _categorize_themes(self):
        """Categorize themes by emotional tone for more coherent selection."""
        categories = {
            "positive": ["flying", "nature", "floating", "water"],
            "negative": ["chase", "teeth", "unprepared"],
            "neutral": ["labyrinth", "falling", "classroom", "mansion"]
        }
        
        # Ensure all themes are categorized
        all_themes = set(self.themes.keys())
        categorized = set()
        for themes in categories.values():
            categorized.update(themes)
        
        # Add uncategorized themes to neutral
        uncategorized = all_themes - categorized
        categories["neutral"].extend(uncategorized)
        
        return categories
    
    def _enhance_narrative(self, base_narrative, theme):
        """Add procedural enhancements to the narrative."""
        narrative = base_narrative
        
        # Add recurring elements from previous dreams
        if self.state["recurring_elements"] and random.random() < 0.3:
            element = random.choice(self.state["recurring_elements"])
            
            # Use varied phrasing for recurring elements
            phrases = [
                f"{element} appears again in the distance.",
                f"{element} seems familiar to you.",
                f"You recognize {element} from a previous dream.",
                f"{element} follows you through the dreamscape."
            ]
            narrative += f" {random.choice(phrases)}"
        
        # Add depth indicators
        if self.state["dream_depth"] > 3:
            depth_phrases = [
                "Deeper in the dream:",
                "As you sink further into sleep:",
                "The dream intensifies:",
                "Reality grows more distant:",
                "The veil between dreams thins:",
                "Dream logic strengthens:"
            ]
            narrative = f"{random.choice(depth_phrases)} {narrative}"
        
        # Adjust tone based on emotional state
        if self.state["emotional_state"] == "positive" and random.random() < 0.3:
            positive_modifiers = [
                "A sense of calm pervades the scene.",
                "There's an unusual clarity to everything.",
                "You feel oddly at peace here.",
                "A pleasant warmth surrounds you.",
                "Colors seem more vibrant here."
            ]
            narrative += f" {random.choice(positive_modifiers)}"
        elif self.state["emotional_state"] == "negative" and random.random() < 0.3:
            negative_modifiers = [
                "An undercurrent of anxiety flows beneath the surface.",
                "Something feels wrong about this place.",
                "Unease settles in your chest.",
                "Shadows seem to move at the edge of your vision.",
                "A faint sense of dread accompanies you."
            ]
            narrative += f" {random.choice(negative_modifiers)}"
        
        return narrative
    
    def _enhance_outcome(self, base_outcome, theme, choice):
        """Add procedural enhancements to the outcome text."""
        outcome = base_outcome
        
        # Add depth-based reflections
        if self.state["dream_depth"] >= 3 and random.random() < 0.4:
            reflections = [
                "Something about this feels significant.",
                "A pattern seems to be forming in your dreams.",
                "The meaning just eludes your grasp.",
                "This choice will echo in later dreams.",
                "Deep meaning resonates beneath the surface.",
                "This moment feels connected to something larger."
            ]
            outcome += f" {random.choice(reflections)}"
        
        # Add emotional coloring occasionally
        if random.random() < 0.3:
            if choice == 'yes':
                yes_reflections = [
                    "There's a sense of rightness to your decision.",
                    "You feel you've chosen well.",
                    "Something aligns within you.",
                    "This path feels meant to be."
                ]
                outcome += f" {random.choice(yes_reflections)}"
            else:
                no_reflections = [
                    "You wonder what would have happened if you chose differently.",
                    "A path not taken lingers in your thoughts.",
                    "The alternative choice echoes in your mind.",
                    "You feel a moment of hesitation about your decision."
                ]
                outcome += f" {random.choice(no_reflections)}"
        
        # Hint at future dreams rarely
        if self.state["dream_depth"] >= 2 and random.random() < 0.2:
            foreshadowing = [
                "You sense this isn't the last time you'll face such a choice.",
                "This moment will recur in different forms.",
                "The dream remembers your decision.",
                "Future dreams will build upon this moment."
            ]
            outcome += f" {random.choice(foreshadowing)}"
        
        return outcome
    
    def _update_recurring_elements(self, theme, choice):
        """Update recurring elements based on theme and choice."""
        new_element = None
        
        # Dictionary of elements by theme and choice
        theme_elements = {
            "falling": {"yes": "The sensation of weightlessness", 
                       "no": "The fear of impact"},
            "chase": {"yes": "The face of your pursuer", 
                     "no": "The sound of distant footsteps"},
            "flying": {"yes": "A glimpse of something beyond the clouds", 
                      "no": "The fear of falling"},
            "labyrinth": {"yes": "A mysterious door", 
                         "no": "The feeling of being lost"},
            "teeth": {"yes": "The feeling of transformation", 
                     "no": "The feeling of something missing"},
            "unprepared": {"yes": "An unexpected supporter", 
                          "no": "The weight of judgment"},
            "nature": {"yes": "The language of plants", 
                      "no": "Eyes watching from the foliage"},
            "water": {"yes": "The freedom of breathing underwater", 
                     "no": "The depths below"},
            "mansion": {"yes": "A familiar room", 
                       "no": "A locked door"},
            "classroom": {"yes": "An important lesson", 
                         "no": "A crucial test"}
        }
        
        # Get element if theme and choice match
        if theme in theme_elements and choice in theme_elements[theme]:
            new_element = theme_elements[theme][choice]
        
        # Add procedurally generated elements occasionally
        if not new_element and random.random() < 0.2:
            procedural_elements = [
                "A symbol you can't quite remember",
                "A familiar voice calling your name",
                "The scent of something from your childhood",
                "A color that seems to have meaning",
                "The sensation of being watched",
                "A melody that feels important",
                "An object that shouldn't exist",
                "A phrase repeated in whispers",
                "A figure glimpsed in periphery",
                "A clock showing impossible time"
            ]
            new_element = random.choice(procedural_elements)
        
        # Add the element if one was selected
        if new_element:
            if new_element in self.state["recurring_elements"]:
                # Move to the end if already present
                self.state["recurring_elements"].remove(new_element)
            self.state["recurring_elements"].append(new_element)
            
            # Limit recurring elements
            if len(self.state["recurring_elements"]) > 3:
                self.state["recurring_elements"] = self.state["recurring_elements"][-3:]
    
    def get_story_segment(self, level_name, game_map=None):
        """Generate a story segment for the current level."""
        # Determine the dream theme
        theme = self.get_theme_for_level(level_name, game_map)
        
        # Get theme data
        theme_data = self.themes[theme]
        
        # Update state
        self.state["visited_dreams"].add(theme)
        self.state["dream_depth"] += 1
        
        # Select narrative and question
        visits = list(self.state["visited_dreams"]).count(theme)
        narrative_index = (visits - 1) % len(theme_data["narratives"])
        question_index = (visits - 1) % len(theme_data["questions"])
        
        # Get narrative text with procedural enhancements
        narrative = self._enhance_narrative(
            theme_data["narratives"][narrative_index],
            theme
        )
        
        # Get question with procedural enhancements
        question = theme_data["questions"][question_index]
        
        # Get outcomes
        yes_outcome = theme_data["outcomes"]["yes"][question_index]
        no_outcome = theme_data["outcomes"]["no"][question_index]
        
        # Return formatted story segment (matching original format)
        return {
            "theme": theme,
            "narrative": narrative,
            "question": question,
            "yes_outcome": yes_outcome,
            "no_outcome": no_outcome,
            "choices": ["Y - Yes", "N - No"]
        }

    def process_choice(self, choice, theme, question_index):
        """Process player choice and update story state."""
        # Record the choice
        if theme not in self.state["choices_made"]:
            self.state["choices_made"][theme] = []
        
        self.state["choices_made"][theme].append(choice)
        
        # Update emotional state
        yes_count = sum(1 for c in self.state["choices_made"].get(theme, []) if c == 'yes')
        no_count = sum(1 for c in self.state["choices_made"].get(theme, []) if c == 'no')
        
        if yes_count > no_count:
            self.state["emotional_state"] = "positive"
        elif no_count > yes_count:
            self.state["emotional_state"] = "negative"
        else:
            self.state["emotional_state"] = "neutral"
        
        # Update recurring elements based on theme and choices
        self._update_recurring_elements(theme, choice)
        
        # Get the appropriate outcome
        theme_data = self.themes[theme]
        outcome_text = theme_data["outcomes"]["yes" if choice == 'yes' else "no"][question_index]
        
        # Add procedural enhancements to the outcome
        enhanced_outcome = self._enhance_outcome(outcome_text, theme, choice)
        
        return enhanced_outcome

    def get_dream_summary(self):
        """Generate a summary of the dream journey."""
        # Check if state has changed since last summary generation
        if (self.state["dream_depth"] == self._last_summary_state["dream_depth"] and
            self.state["emotional_state"] == self._last_summary_state["emotional_state"] and
            self.state["recurring_elements"] == self._last_summary_state["recurring_elements"] and
            self.state["visited_dreams"] == self._last_summary_state["visited_dreams"]):
            # Return cached summary if state hasn't changed
            return self._dream_summary_cache
        
        # Generate new summary if state has changed
        if self.state["dream_depth"] <= 0:
            summary = "The dream begins..."
        else:
            themes_seen = len(self.state["visited_dreams"])
            
            if themes_seen == 0:
                summary = "Your dream journey is just beginning..."
            else:
                # Create a richer summary
                parts = []
                
                # Depth indicator - use fixed text based on depth range to avoid random changes
                if self.state["dream_depth"] < 3:
                    if self.state["dream_depth"] == 1:
                        depth_text = "You are still near the surface of your dream."
                    else:
                        depth_text = "The dreaming has just begun."
                elif self.state["dream_depth"] < 6:
                    if self.state["dream_depth"] <= 4:
                        depth_text = "You are descending deeper into your subconscious."
                    else:
                        depth_text = "Layers of dreaming enfold you."
                else:
                    if self.state["dream_depth"] < 8:
                        depth_text = "You have journeyed deep into the dream world."
                    else:
                        depth_text = "The logic of dreams has replaced reality."
                parts.append(depth_text)
                
                # Emotional state - fixed mapping instead of random choice
                emotion_mapping = {
                    "positive": "Your journey has been mostly hopeful.",
                    "negative": "Your path has been filled with anxiety.",
                    "neutral": "Your dream has been a balance of light and dark."
                }
                emotion_text = emotion_mapping[self.state["emotional_state"]]
                parts.append(emotion_text)
                
                # Add recurring elements if any - use the most recent one for stability
                if self.state["recurring_elements"]:
                    element = self.state["recurring_elements"][-1]  # Use last/most recent element
                    parts.append(f"{element} seems significant.")
                
                summary = " ".join(parts)
        
        # Update cache and last state
        self._dream_summary_cache = summary
        self._last_summary_state = {
            "dream_depth": self.state["dream_depth"],
            "emotional_state": self.state["emotional_state"],
            "recurring_elements": self.state["recurring_elements"].copy(),
            "visited_dreams": self.state["visited_dreams"].copy()
        }
        
        return self._dream_summary_cache
    
# Create a singleton instance
_dream_manager = DreamManager()

# Compatibility functions that use the DreamManager instance
def get_dream_theme_for_level(level_name, game_map=None):
    """Compatibility wrapper for DreamManager.get_theme_for_level."""
    return _dream_manager.get_theme_for_level(level_name, game_map)

def get_story_segment(level_name, game_map=None):
    """Compatibility wrapper for DreamManager.get_story_segment."""
    return _dream_manager.get_story_segment(level_name, game_map)

def process_story_choice(choice, theme, question_index):
    """Compatibility wrapper for DreamManager.process_choice."""
    return _dream_manager.process_choice(choice, theme, question_index)

def get_dream_summary():
    """Compatibility wrapper for DreamManager.get_dream_summary."""
    return _dream_manager.get_dream_summary()

def reset_story():
    """Reset the story state for a new game."""
    global story_state, _dream_manager
    story_state = {
        "visited_dreams": set(),
        "choices_made": {},
        "dream_depth": 0,
        "recurring_elements": [],
        "emotional_state": "neutral",
    }
    # Recreate the dream manager to reset its state
    _dream_manager = DreamManager()
