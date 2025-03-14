import pygame
import weakref

class GameFont:
    """Cache for reusable fonts with memory management."""
    _fonts = {}  # Use regular dictionary instead of weak references for fonts
    
    @classmethod
    def get(cls, size=24, font_name=None, bold=False):
        """Get a cached font or create a new one."""
        key = (font_name, size, bold)
        if key not in cls._fonts:
            cls._fonts[key] = pygame.font.SysFont(font_name, size, bold=bold)
        return cls._fonts[key]

class TextCache:
    """Cache for rendered text surfaces to avoid repeated rendering."""
    _cache = {}  # Use regular dictionary instead of weak references
    _max_size = 100  # Limit cache size
    
    @classmethod
    def get_text_surface(cls, text, font, color):
        """Get a cached text surface or create a new one."""
        key = (text, str(font), color)  # Use str(font) instead of font object for key
        if key not in cls._cache:
            if len(cls._cache) >= cls._max_size:
                # Clear some space if cache is too full
                for old_key in list(cls._cache.keys())[:10]:  # Remove oldest 10 entries
                    del cls._cache[old_key]
            cls._cache[key] = font.render(text, True, color)
        return cls._cache[key]

def draw_text(screen, text, position, color=(255, 255, 255), size=24, font_name=None, centered=False):
    """Draw text efficiently using caching."""
    try:
        font = GameFont.get(size, font_name)
        text_surface = TextCache.get_text_surface(text, font, color)
        
        if centered:
            text_rect = text_surface.get_rect(center=position)
            screen.blit(text_surface, text_rect)
        else:
            screen.blit(text_surface, position)
        
        return text_surface.get_width(), text_surface.get_height()
    except Exception as e:
        # Fallback rendering if caching fails
        print(f"Warning: Font caching failed: {e}")
        fallback_font = pygame.font.SysFont(None, size)
        fallback_surface = fallback_font.render(text, True, color)
        
        if centered:
            text_rect = fallback_surface.get_rect(center=position)
            screen.blit(fallback_surface, text_rect)
        else:
            screen.blit(fallback_surface, position)
        
        return fallback_surface.get_width(), fallback_surface.get_height()

def draw_fade_overlay(screen, alpha):
    """Draw a fade overlay efficiently."""
    # Use static variable instead of attribute checking
    if not hasattr(draw_fade_overlay, 'surfaces'):
        draw_fade_overlay.surfaces = {}
    
    screen_size = (screen.get_width(), screen.get_height())
    
    # Create surface if needed for this size
    if screen_size not in draw_fade_overlay.surfaces:
        draw_fade_overlay.surfaces[screen_size] = pygame.Surface(screen_size)
        draw_fade_overlay.surfaces[screen_size].fill((0, 0, 0))
    
    # Get the cached surface and apply alpha
    fade_surface = draw_fade_overlay.surfaces[screen_size]
    fade_surface.set_alpha(alpha)
    screen.blit(fade_surface, (0, 0))

def get_performance_stats():
    """Return performance-related statistics."""
    import gc
    return {
        "font_cache_size": len(GameFont._fonts),
        "text_cache_size": len(TextCache._cache),
        "fade_surface_count": len(getattr(draw_fade_overlay, 'surfaces', {})),
        "gc_objects": len(gc.get_objects())
    }
