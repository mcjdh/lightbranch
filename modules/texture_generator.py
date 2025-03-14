"""
Procedural texture generator for dream levels.
Uses various noise algorithms to create dreamy textures.
"""
import pygame
import random
import math
import colorsys
from functools import lru_cache

# Texture cache to avoid regenerating textures
texture_cache = {}

# Constants
DEFAULT_TEXTURE_SIZE = 64
MAX_TEXTURES_PER_TYPE = 4

def generate_texture(theme, texture_type, wall_type=1, size=DEFAULT_TEXTURE_SIZE, seed=None):
    """
    Generate a procedural texture for a specific theme and type.
    
    Args:
        theme: Dream theme name (e.g., 'falling', 'labyrinth')
        texture_type: Type of texture ('wall', 'floor', 'ceiling')
        wall_type: Wall type identifier (1-3)
        size: Texture size (width and height)
        seed: Random seed for consistent generation
        
    Returns:
        pygame.Surface: Generated texture
    """
    cache_key = (theme, texture_type, wall_type, size, seed)
    
    # Return cached texture if available
    if cache_key in texture_cache:
        return texture_cache[cache_key]
    
    # Set random seed for consistent generation
    if seed is not None:
        random.seed(seed)
    
    # Create base surface
    texture = pygame.Surface((size, size))
    
    # Choose generation method based on theme
    if theme in ['labyrinth', 'mansion']:
        # Structured patterns for maze-like dreams
        generate_maze_texture(texture, theme, texture_type, wall_type)
    elif theme in ['falling', 'flying', 'floating']:
        # Cloudy, ethereal textures
        generate_cloud_texture(texture, theme, texture_type, wall_type)
    elif theme in ['chase', 'teeth', 'unprepared']:
        # More chaotic, anxiety-inducing textures
        generate_noise_texture(texture, theme, texture_type, wall_type, turbulence=True)
    elif theme in ['water']:
        # Watery, flowing textures
        generate_water_texture(texture, theme, texture_type, wall_type)
    elif theme in ['nature']:
        # Organic, natural textures
        generate_nature_texture(texture, theme, texture_type, wall_type)
    else:
        # Default to basic noise texture
        generate_noise_texture(texture, theme, texture_type, wall_type)
    
    # Cache the generated texture
    texture_cache[cache_key] = texture
    
    # Reset random seed
    if seed is not None:
        random.seed()
    
    return texture

def generate_maze_texture(texture, theme, texture_type, wall_type):
    """Generate a structured maze-like texture."""
    width, height = texture.get_width(), texture.get_height()
    
    # Base color from wall type
    if wall_type == 1:
        base_color = (170, 80, 80)  # Red tones
    elif wall_type == 2:
        base_color = (80, 170, 80)  # Green tones
    elif wall_type == 3:
        base_color = (80, 80, 170)  # Blue tones
    else:
        base_color = (120, 120, 120)  # Gray tones
    
    # Adjust color for floor/ceiling
    if texture_type == 'floor':
        base_color = [max(c - 40, 0) for c in base_color]
    elif texture_type == 'ceiling':
        base_color = [min(c + 20, 255) for c in base_color]
    
    # Create noise grid for the texture
    grid_size = random.randint(4, 8)
    noise_grid = [[random.random() for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Generate texture pixels
    for y in range(height):
        for x in range(width):
            # Calculate grid coordinates
            grid_x = int(x * grid_size / width)
            grid_y = int(y * grid_size / height)
            
            # Get noise value
            noise_value = noise_grid[grid_y][grid_x]
            
            # Create structured pattern
            if theme == 'labyrinth':
                # Maze-like pattern with straight lines
                if (x % (width//8) < width//16) or (y % (height//8) < height//16):
                    noise_value *= 0.7
            elif theme == 'mansion':
                # More regular pattern like wallpaper
                if (x % (width//4) < width//8) ^ (y % (height//4) < height//8):
                    noise_value *= 0.8
            
            # Calculate color based on noise
            color = [int(c * (0.8 + noise_value * 0.4)) for c in base_color]
            
            # Set pixel color
            texture.set_at((x, y), color)
    
    return texture

def generate_cloud_texture(texture, theme, texture_type, wall_type):
    """Generate a cloudy, ethereal texture."""
    width, height = texture.get_width(), texture.get_height()
    
    # Choose base color based on theme and type
    if theme == 'falling':
        if texture_type == 'ceiling':
            base_color = (100, 130, 180)  # Sky blue
        elif texture_type == 'floor':
            base_color = (130, 100, 130)  # Purple ground
        else:
            base_color = (150, 150, 180)  # Light purple-blue
    elif theme == 'flying':
        if texture_type == 'ceiling':
            base_color = (150, 200, 255)  # Bright sky
        elif texture_type == 'floor':
            base_color = (200, 230, 255)  # Cloud floor
        else:
            base_color = (180, 200, 230)  # Light blue
    else:
        # Default floating theme
        if texture_type == 'ceiling':
            base_color = (180, 180, 220)
        elif texture_type == 'floor':
            base_color = (150, 150, 180)
        else:
            base_color = (160, 160, 200)
            
    # Modify color based on wall type
    if wall_type == 1:
        base_color = tuple(min(c * 1.2, 255) for c in base_color)
    elif wall_type == 2:
        # Add green tint
        base_color = (base_color[0], int(base_color[1] * 1.2), base_color[2])
    elif wall_type == 3:
        # Add blue tint
        base_color = (base_color[0], base_color[1], int(base_color[2] * 1.2))
    
    # Generate a few octaves of smooth noise
    octaves = 4
    persistence = 0.5
    
    # Create texture pixels using value noise
    for y in range(height):
        for x in range(width):
            noise_value = 0
            amplitude = 1.0
            frequency = 1.0
            max_value = 0
            
            for i in range(octaves):
                # Scale coordinates for this octave
                nx = x * frequency / width
                ny = y * frequency / height
                
                # Get interpolated noise value
                n = smooth_noise(nx, ny)
                
                # Add weighted noise to total
                noise_value += n * amplitude
                
                # Prepare for next octave
                max_value += amplitude
                amplitude *= persistence
                frequency *= 2
            
            # Normalize noise value
            noise_value /= max_value
            
            # Apply theme-specific modifications
            if theme == 'falling':
                # Add vertical streaking
                noise_value = (noise_value * 0.8) + (y / height * 0.2)
            elif theme == 'flying':
                # Add horizontal banding
                if (y / height * 10) % 1 < 0.5:
                    noise_value = noise_value * 0.9 + 0.1
            
            # Calculate color based on noise
            color = [int(c * (0.7 + noise_value * 0.6)) for c in base_color]
            
            # Set pixel color
            texture.set_at((x, y), color)
    
    return texture

def generate_noise_texture(texture, theme, texture_type, wall_type, turbulence=False):
    """Generate a noise texture with optional turbulence for chaotic dreams."""
    width, height = texture.get_width(), texture.get_height()
    
    # Choose base color based on theme and wall type
    if theme == 'chase':
        base_hue = 0.95  # Purple
        saturation = 0.4
        value_range = (0.2, 0.6)
    elif theme == 'teeth':
        base_hue = 0.05  # Orange-red
        saturation = 0.3
        value_range = (0.5, 0.8)
    elif theme == 'unprepared':
        base_hue = 0.6  # Blue
        saturation = 0.2
        value_range = (0.3, 0.7)
    else:
        # Default
        base_hue = random.random()
        saturation = 0.3
        value_range = (0.4, 0.8)
    
    # Adjust for wall type
    if wall_type == 1:
        base_hue = (base_hue + 0.0) % 1.0  # Red shift
    elif wall_type == 2:
        base_hue = (base_hue + 0.3) % 1.0  # Green shift
    elif wall_type == 3:
        base_hue = (base_hue + 0.6) % 1.0  # Blue shift
    
    # Adjust for texture type
    if texture_type == 'floor':
        value_range = (max(0.1, value_range[0] - 0.2), max(0.4, value_range[1] - 0.1))
    elif texture_type == 'ceiling':
        value_range = (min(0.9, value_range[0] + 0.1), min(1.0, value_range[1] + 0.1))
    
    # Generate fractal noise
    octaves = 4
    persistence = 0.6
    
    for y in range(height):
        for x in range(width):
            noise_value = 0
            amplitude = 1.0
            frequency = 1.0
            max_value = 0
            
            for i in range(octaves):
                # Scale coordinates for this octave
                nx = x * frequency / width
                ny = y * frequency / height
                
                # Add turbulence/distortion for chaotic dreams
                if turbulence:
                    distort_x = math.sin(ny * 5) * 0.1
                    distort_y = math.cos(nx * 5) * 0.1
                    nx += distort_x
                    ny += distort_y
                
                # Get noise value
                n = smooth_noise(nx, ny)
                
                # Add weighted noise to total
                noise_value += n * amplitude
                
                # Prepare for next octave
                max_value += amplitude
                amplitude *= persistence
                frequency *= 2
            
            # Normalize noise value
            noise_value /= max_value
            
            # Map noise to value range
            value = value_range[0] + noise_value * (value_range[1] - value_range[0])
            
            # Convert HSV to RGB
            r, g, b = colorsys.hsv_to_rgb(base_hue, saturation, value)
            color = (int(r * 255), int(g * 255), int(b * 255))
            
            # Set pixel color
            texture.set_at((x, y), color)
    
    return texture

def generate_water_texture(texture, theme, texture_type, wall_type):
    """Generate a watery, flowing texture."""
    width, height = texture.get_width(), texture.get_height()
    
    # Base color for water
    if texture_type == 'ceiling':
        base_color = (130, 200, 230)  # Light blue
    elif texture_type == 'floor':
        base_color = (30, 70, 120)  # Deep blue
    else:
        base_color = (70, 140, 180)  # Medium blue
    
    # Modify color based on wall type
    if wall_type == 1:
        # Reddish water
        base_color = (base_color[0] + 40, base_color[1] - 20, base_color[2] - 20)
    elif wall_type == 2:
        # Greenish water
        base_color = (base_color[0] - 20, base_color[1] + 40, base_color[2] - 20)
    
    # Clamp colors
    base_color = tuple(max(0, min(255, c)) for c in base_color)
    
    # Water wave parameters
    wave_length = random.uniform(3.0, 6.0)
    wave_height = random.uniform(0.2, 0.4)
    time_factor = random.uniform(0, 10)  # Random phase
    
    for y in range(height):
        for x in range(width):
            # Create waves with sine functions
            fx = x / width
            fy = y / height
            
            # Multiple overlapping waves
            wave1 = math.sin(fx * wave_length + time_factor) * wave_height
            wave2 = math.sin((fx + fy) * wave_length * 0.7 + time_factor * 1.3) * wave_height * 0.5
            wave3 = math.sin(fy * wave_length * 1.3 + time_factor * 0.7) * wave_height * 0.3
            
            combined_wave = (wave1 + wave2 + wave3) / 2.0 + 0.5  # Normalize to 0-1
            
            # Add some noise for texture
            noise = smooth_noise(fx * 3, fy * 3) * 0.2
            value = combined_wave * 0.8 + noise
            value = max(0, min(1, value))
            
            # Calculate color based on value
            r = int(base_color[0] * (0.7 + value * 0.6))
            g = int(base_color[1] * (0.7 + value * 0.6))
            b = int(base_color[2] * (0.7 + value * 0.6))
            
            # Add occasional highlights for water surface
            if texture_type == 'ceiling' or texture_type == 'floor':
                if random.random() < 0.01:
                    r = min(255, r + 40)
                    g = min(255, g + 40)
                    b = min(255, b + 40)
            
            # Set pixel color
            texture.set_at((x, y), (r, g, b))
    
    return texture

def generate_nature_texture(texture, theme, texture_type, wall_type):
    """Generate an organic, natural texture."""
    width, height = texture.get_width(), texture.get_height()
    
    # Choose base color based on texture type
    if texture_type == 'ceiling':
        base_color = (150, 200, 100)  # Light green (leaves)
    elif texture_type == 'floor':
        base_color = (100, 70, 40)    # Brown (soil)
    else:
        base_color = (120, 150, 80)   # Moss/vegetation
    
    # Modify color based on wall type
    if wall_type == 1:
        # Reddish tint (autumn)
        base_color = (base_color[0] + 30, base_color[1] - 10, max(base_color[2] - 20, 0))
    elif wall_type == 2:
        # More green (vibrant)
        base_color = (max(base_color[0] - 20, 0), min(base_color[1] + 20, 255), base_color[2])
    elif wall_type == 3:
        # Bluish tint (moonlight)
        base_color = (base_color[0], base_color[1], min(base_color[2] + 40, 255))
    
    # Create organic texture using domain warping
    octaves = 4
    persistence = 0.6
    
    for y in range(height):
        for x in range(width):
            # Basic coordinates
            fx = x / width
            fy = y / height
            
            # Domain warping (coordinates distortion)
            warp_x = smooth_noise(fx * 3, fy * 3) * 0.2
            warp_y = smooth_noise(fx * 3 + 0.5, fy * 3 + 0.5) * 0.2
            
            # Use warped coordinates for noise
            sample_x = fx + warp_x
            sample_y = fy + warp_y
            
            # Generate fractal noise
            noise_value = 0
            amplitude = 1.0
            frequency = 1.0
            max_value = 0
            
            for i in range(octaves):
                # Scale coordinates for this octave
                nx = sample_x * frequency
                ny = sample_y * frequency
                
                # Get noise value
                n = smooth_noise(nx, ny)
                
                # Add weighted noise to total
                noise_value += n * amplitude
                
                # Prepare for next octave
                max_value += amplitude
                amplitude *= persistence
                frequency *= 2
            
            # Normalize noise value
            noise_value /= max_value
            
            # Add vein-like structures for leaves/bark
            if texture_type == 'ceiling' or (texture_type == 'wall' and random.random() < 0.7):
                # Create vein pattern
                vein_x = abs(((fx * 10) % 1) - 0.5) * 2  # 0-1 distance from vein
                vein_y = abs(((fy * 10) % 1) - 0.5) * 2
                vein_value = min(vein_x, vein_y)
                
                # Combine with noise
                if vein_value < 0.1:
                    noise_value = noise_value * 0.8 + 0.2
            
            # For floor, add some texture variation
            if texture_type == 'floor':
                if noise_value > 0.7 and random.random() < 0.2:
                    # Add pebbles/details
                    noise_value = noise_value * 1.2
            
            # Calculate color based on noise
            color = [int(c * (0.7 + noise_value * 0.6)) for c in base_color]
            
            # Set pixel color
            texture.set_at((x, y), color)
    
    return texture

@lru_cache(maxsize=256)
def smooth_noise(x, y):
    """Generate a smooth noise value at the given coordinates."""
    # Get integer and fractional parts
    x_int, x_frac = int(x), x - int(x)
    y_int, y_frac = int(y), y - int(y)
    
    # Get four corner values
    v1 = random_from_coords(x_int, y_int)
    v2 = random_from_coords(x_int + 1, y_int)
    v3 = random_from_coords(x_int, y_int + 1)
    v4 = random_from_coords(x_int + 1, y_int + 1)
    
    # Interpolate
    i1 = lerp(v1, v2, smooth_step(x_frac))
    i2 = lerp(v3, v4, smooth_step(x_frac))
    return lerp(i1, i2, smooth_step(y_frac))

@lru_cache(maxsize=1024)
def random_from_coords(x, y):
    """Generate a deterministic random value from coordinates."""
    # Simple hash function
    return ((x * 12345 + y * 67890) % 65536) / 65536.0

def lerp(a, b, t):
    """Linear interpolation between a and b by factor t."""
    return a + (b - a) * t

def smooth_step(t):
    """Smooth step function for interpolation."""
    return t * t * (3 - 2 * t)

def get_texture_for_level(level_name, texture_type, wall_type=1):
    """
    Get an appropriate texture for the current level.
    
    Args:
        level_name: String identifier for the level
        texture_type: Type of texture ('wall', 'floor', 'ceiling')
        wall_type: Wall type identifier (1-3)
        
    Returns:
        pygame.Surface: Generated texture
    """
    # Get theme information for the level
    from modules.dream_story import get_dream_theme_for_level
    
    # Default theme fallback
    theme = "labyrinth"
    
    try:
        # Try to get the theme associated with this level
        if level_name.startswith("proc_"):
            # For procedural levels, get the theme based on level properties
            theme = get_dream_theme_for_level(level_name)
        elif level_name == "level1":
            theme = "falling"
    except Exception as e:
        print(f"Error getting theme for level: {e}")
    
    # Generate a texture based on the theme
    try:
        # Use level name as seed for consistent textures per level
        seed_value = hash(level_name + texture_type + str(wall_type)) % 10000
        return generate_texture(theme, texture_type, wall_type, seed=seed_value)
    except Exception as e:
        print(f"Error generating texture: {e}")
        # Create fallback texture
        fallback = pygame.Surface((DEFAULT_TEXTURE_SIZE, DEFAULT_TEXTURE_SIZE))
        fallback.fill((150, 150, 150))
        return fallback

def clear_texture_cache():
    """Clear the texture cache to free memory."""
    global texture_cache
    texture_cache.clear()
