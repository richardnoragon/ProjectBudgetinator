# Window Positioning System Guide

## Overview

The ProjectBudgetinator now includes a comprehensive window positioning system that allows users to customize how the main window and dialogs are positioned on screen. This system provides both preset options for common positioning preferences and custom coordinate support for advanced users.

## Features

### Main Window Positioning

The main window can be positioned using several modes:

#### Preset Positions
- **Center of Screen** (default) - Centers the window on the primary monitor
- **Top-Left Corner** - Positions window at top-left with 50px offset from edges
- **Top-Right Corner** - Positions window at top-right corner
- **Bottom-Left Corner** - Positions window at bottom-left corner
- **Bottom-Right Corner** - Positions window at bottom-right corner
- **Remember Last Position** - Saves and restores window position between sessions

#### Custom Positioning
- **Custom Coordinates** - Allows precise X,Y coordinate specification
- **Size Memory** - Optionally remembers window size between sessions
- **Default Size** - Configurable default window dimensions

### Dialog Positioning

Dialogs opened from the main window can be positioned using various alignment options:

#### Horizontal Alignment
- **Centered** (default) - Centers dialog over main window
- **Left-Aligned** - Aligns dialog's left edge with main window's left edge
- **Right-Aligned** - Aligns dialog's right edge with main window's right edge
- **Top-Left Corner** - Positions dialog at main window's top-left corner
- **Top-Right Corner** - Positions dialog at main window's top-right corner
- **Bottom-Left Corner** - Positions dialog at main window's bottom-left corner
- **Bottom-Right Corner** - Positions dialog at main window's bottom-right corner
- **Custom Offset** - User-defined X,Y offset from main window

#### Vertical Alignment
- **Centered** (default) - Centers dialog vertically over main window
- **Top-Aligned** - Aligns dialog top with main window top
- **Bottom-Aligned** - Aligns dialog bottom with main window bottom

#### Advanced Options
- **Screen Boundary Respect** - Ensures dialogs stay within screen bounds
- **Cascade Multiple Dialogs** - Offsets multiple dialogs to prevent overlap

## Configuration

### Accessing Preferences

1. Open the main application
2. Go to **Preferences** → **Preferences**
3. Click **Configure Window Positioning...**

### Configuration Structure

The window positioning preferences are stored in the user configuration file with the following structure:

```json
{
  "window_positioning": {
    "main_window": {
      "mode": "center_screen",
      "custom_x": 100,
      "custom_y": 100,
      "last_position": {
        "x": 200,
        "y": 150,
        "width": 800,
        "height": 600
      },
      "remember_size": true,
      "default_size": {
        "width": 800,
        "height": 600
      }
    },
    "dialogs": {
      "horizontal_alignment": "center",
      "vertical_alignment": "center",
      "custom_offset": {
        "x": 0,
        "y": 0
      },
      "respect_screen_bounds": true,
      "cascade_multiple_dialogs": false
    }
  }
}
```

## Usage Examples

### Example 1: Productivity Setup
For users who prefer side-by-side workflows:
- Main Window: Top-Left Corner
- Dialogs: Left-Aligned, Top-Aligned
- This keeps dialogs from covering the main window content

### Example 2: Focus Mode
For minimal distraction:
- Main Window: Center of Screen
- Dialogs: Centered over Main Window
- This provides a traditional, focused interface

### Example 3: Multi-Monitor Setup
For users with multiple monitors:
- Main Window: Custom Coordinates (positioned on secondary monitor)
- Dialogs: Centered with Screen Boundary Respect enabled
- This ensures dialogs stay on the same monitor as the main window

### Example 4: Power User Setup
For advanced users:
- Main Window: Remember Last Position with Size Memory
- Dialogs: Custom Offset with Cascade enabled
- This provides maximum flexibility and efficiency

## Technical Implementation

### Core Components

1. **WindowPositionManager** (`src/utils/window_positioning.py`)
   - Central positioning logic
   - Preference integration
   - Multi-monitor support

2. **PositionCalculator** (`src/utils/window_positioning.py`)
   - Screen dimension detection
   - Position validation
   - Boundary checking

3. **PreferencesExtension** (`src/core/preferences.py`)
   - Extended configuration schema
   - Preference persistence
   - Migration support

4. **DialogPositioner** (`src/gui/window_manager.py`)
   - Unified dialog positioning
   - Fallback mechanisms
   - Integration with existing dialogs

### Integration Points

The positioning system integrates with:
- Main window creation in `src/main.py`
- All dialog classes via `src/gui/window_manager.py`
- Preferences system in `src/core/preferences.py`
- Configuration management in `src/utils/config_utils.py`

## Multi-Monitor Support

The system includes basic multi-monitor awareness:
- Detects primary screen dimensions
- Validates positions are on-screen
- Provides fallback positioning for invalid coordinates
- Keeps dialogs on the same monitor as the main window

## Error Handling

The positioning system includes robust error handling:
- Graceful fallback to default positioning if preferences are invalid
- Screen boundary validation to prevent off-screen windows
- Import error handling for missing positioning modules
- Logging of positioning operations for debugging

## Migration and Compatibility

The system is designed to be backward compatible:
- Existing configurations are automatically migrated
- Missing positioning preferences are filled with defaults
- Old dialog positioning methods are preserved as fallbacks
- No breaking changes to existing functionality

## Troubleshooting

### Common Issues

1. **Window appears off-screen**
   - Solution: Reset positioning preferences to defaults
   - The system should auto-detect and correct this

2. **Dialogs not positioning correctly**
   - Check that "Respect Screen Bounds" is enabled
   - Verify custom offsets are reasonable values

3. **Position not remembered between sessions**
   - Ensure "Remember Last Position" is enabled
   - Check that the application has write permissions to config directory

4. **Multi-monitor issues**
   - The system uses primary monitor dimensions
   - Custom coordinates may need adjustment for multi-monitor setups

### Debug Information

Enable verbose logging to see positioning operations:
- Set `startup_diagnostic` to `verbose` in preferences
- Check application logs for positioning debug messages
- Use the preview function in positioning preferences to test settings

## Future Enhancements

Potential future improvements:
- Full multi-monitor support with monitor selection
- Per-dialog-type positioning preferences
- Animation and transition effects
- Workspace-based positioning profiles
- Integration with OS window management features

## API Reference

### Main Functions

```python
# Position main window according to preferences
from utils.window_positioning import position_main_window
position_main_window(window, preferences_manager)

# Position dialog according to preferences
from utils.window_positioning import position_dialog
position_dialog(dialog, parent, dialog_type)

# Save main window position
from utils.window_positioning import save_main_window_position
save_main_window_position(window)
```

### Configuration Access

```python
# Get positioning preferences
prefs = preferences_manager.get_preference('window_positioning')

# Set positioning preferences
preferences_manager.set_preference('window_positioning', new_prefs)
```

This comprehensive window positioning system provides users with the flexibility to customize their workspace while maintaining ease of use through sensible defaults and preset options.