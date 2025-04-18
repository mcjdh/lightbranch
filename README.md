# Some Dream — Game Design Overview

**Some Dream** is a first‑person, procedurally generated “dream” exploration game built with Pygame. You navigate mazelike levels, encounter a roaming entity, and unlock narrative fragments that shape a custom dream story.

## Core Features

- **Procedural Levels**  
  - Uses [`modules.level_loader.load_level`](modules/level_loader.py) to fetch predefined maps or call  
    [`modules.procedural_generator.generate_procedural_map`](modules/procedural_generator.py).  
  - Ensures connectivity (`ensure_connectivity` / `ensure_safe_connectivity`) and validates map shape.

- **Player Movement & Collision**  
  - Walk, rotate, and strafe with frame‑independent controls in [`core.player.Player`](core/player.py).  
  - Collision buffer prevents clipping through walls.

- **Entity Placement & Interaction**  
  - Spawns a colored entity via [`core.entity.generate_entity`](core/entity.py).  
  - Raycasts (`core.raycast.raycast`) to detect when you look at it, then press `E` to trigger a dream interaction.

- **Dream Story System**  
  - Managed by [`modules.dream_story.DreamManager`](modules/dream_story.py).  
  - Chooses themes based on map features (`_analyze_map_features`) and level number, presents narrative+question, then processes Y/N choices.  
  - Summarizes dream progression via `get_dream_summary`.

- **Rendering**  
  - 3D wall rendering in [`core.renderer.render_scene`](core/renderer.py).  
  - Minimap (`draw_minimap`) in the top‑right corner.  
  - FPS counter via `display_fps`.

- **Textures & Visuals**  
  - Toggle textures on/off with `F5`.  
  - Textures loaded per level by `modules.texture_generator.get_texture_for_level`.

- **Level Transition & Fading**  
  - After story outcome, auto‑fade out/in and call [`modules.level_loader.transition_to_new_level`](modules/level_loader.py).  
  - Fallback to predefined maps on error.

## Controls

- Movement: ↑/W forward, ↓/S back, A/D strafe  
- Rotate: ←/→  
- Interact: `E` when looking at entity  
- Choose story options: `Y` / `N`  
- Continue after outcome: `SPACE`  
- Fullscreen toggle: `F11`  
- Textures toggle: `F5`  
- Quit: `ESC`

## Project Structure

- core/  
  ├─ config.py        ← game constants (SCREEN_WIDTH, FPS, colors…)  
  ├─ player.py        ← movement & collision  
  ├─ entity.py        ← spawn & render entities  
  ├─ raycast.py       ← world sampling for rendering & interaction  
  ├─ renderer.py      ← draw walls, minimap, FPS  
  └─ interaction.py   ← UI overlays for story & choices  

- modules/  
  ├─ level_loader.py       ← map loading & level transitions  
  ├─ procedural_generator.py ← room/cellular/maze generators  
  ├─ dream_story.py        ← procedural narrative and state  
  ├─ dream_themes_builtin.py ← built‑in dream content  
  └─ texture_generator.py  ← per‑level texture loading  

Enjoy exploring your own dreamscape!  