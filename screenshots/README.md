# Screenshots Folder

This folder contains screenshots of the MiniPro GUI application.

## Current Placeholders

The following placeholder images need to be replaced with actual screenshots:

### main-window.png
- **What to capture:** Full application window showing the Device Info tab
- **Recommended size:** 1200x800 pixels
- **Shows:** Device dropdown, programmer detection, main interface

### read-write-tab.png
- **What to capture:** Read/Write tab with a device selected
- **Recommended size:** 1200x800 pixels
- **Shows:** File browser, memory type selection, read/write/erase buttons

### progress-bar.png
- **What to capture:** Operation in progress with progress bar visible
- **Recommended size:** 1200x800 pixels
- **Shows:** Real-time progress bar at 50-75%, console output, debug mode enabled

### device-dropdown.png
- **What to capture:** Device dropdown expanded showing search/filter
- **Recommended size:** 800x600 pixels (cropped)
- **Shows:** Searchable dropdown with filtered results

### configuration-tab.png
- **What to capture:** Configuration tab showing voltage settings
- **Recommended size:** 1200x800 pixels
- **Shows:** Voltage controls, SPI settings, protection options

## How to Take Screenshots

### Linux
```bash
# Full window
gnome-screenshot -w

# Select area
gnome-screenshot -a

# Or use Flameshot (recommended)
flameshot gui
```

### macOS
```bash
# Full window: Cmd + Shift + 4, then Space, then click window
# Select area: Cmd + Shift + 4
```

### Windows
```bash
# Use Snipping Tool or Win + Shift + S
```

## Screenshot Guidelines

1. **Clean desktop** - Close unnecessary windows
2. **Full application** - Show the complete interface
3. **Realistic data** - Use actual device names and files
4. **Good lighting** - Dark theme shows best on light backgrounds
5. **High resolution** - At least 1200x800 for main screenshots
6. **PNG format** - Best for UI screenshots

## After Taking Screenshots

Replace the placeholder images:
```bash
cp your-screenshot.png screenshots/main-window.png
```

Then update the repository:
```bash
git add screenshots/
git commit -m "docs: Add application screenshots"
git push
```

## Optional: Animated GIFs

Consider adding animated demos:
- `progress-animation.gif` - Show progress bar in action
- `device-search.gif` - Show typing to filter devices
- `quick-workflow.gif` - Erase → Write → Verify workflow

Use tools like:
- **Linux:** Peek (https://github.com/phw/peek)
- **macOS:** Gifox (https://gifox.app/)
- **Windows:** ScreenToGif (https://www.screentogif.com/)

---

**Note:** The placeholder images are simple SVG-based placeholders. Replace them with actual screenshots for a professional appearance!
