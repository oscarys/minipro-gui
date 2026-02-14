# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.3.3] - 2026-02-14

### Fixed
- **Progress bar now updates in real-time!** This was the major fix everyone was waiting for.
- Read progress from stderr where minipro actually outputs it (not stdout)
- Implemented character-by-character reading with select() multiplexing
- Proper ANSI escape sequence stripping (handles `[K` codes)
- Debug output now actually appears when Debug Mode is enabled

### Technical
- Use `select.select()` on Linux/macOS for efficient stream reading
- Fallback to threading approach on Windows
- Character-by-character reading catches all `\r` updates
- Separate stdout/stderr streams instead of combining them

## [1.3.2] - 2026-02-14

### Added
- Debug Mode checkbox for troubleshooting progress parsing
- Purple console output for debug messages
- Improved progress parsing with more patterns

### Changed
- Attempted unbuffered output (partial solution)
- Enhanced progress detection algorithms

## [1.3.1] - 2026-02-14

### Fixed
- Strip ANSI escape sequences before parsing
- Better operation detection (specific patterns)
- Improved completion detection

## [1.3.0] - 2026-02-14

### Added
- Erase button directly in Read/Write tab (no more tab switching!)
- Persistent settings with QSettings
  - Remembers last device selection
  - Remembers file paths (read/write files)
  - Remembers last directory for file browser
  - Remembers window geometry (position and size)
  - Remembers memory type and file format selections
- Settings automatically save on close and restore on launch

### Changed
- Improved workflow: Erase → Write → Verify all in one tab

## [1.2.1] - 2026-02-14

### Fixed
- Device list loading now includes devices without @ package suffix (e.g., GAL16V8D)
- Improved device name parsing from minipro output

### Added
- GAL/PAL devices to common device list (GAL16V8, GAL16V8D, GAL20V8, GAL22V10, etc.)

## [1.2.0] - 2026-02-14

### Added
- Searchable device dropdown with autocomplete
- Pre-loaded 40+ common devices (EEPROM, EPROM, SPI Flash, GAL/PAL, MCUs, Logic ICs)
- "Load Device List" button for on-demand loading of all 13,000+ devices
- Background device list loading (non-blocking UI)
- Smart filtering (type to search, matches anywhere in device name)

### Changed
- Replaced separate search field and "List All" button with single dropdown
- Cleaner device selection interface
- No more console spam from device listings

### Removed
- Separate device search text box
- "Search" button
- "List All Devices" button
- Duplicate "Selected Device" field

## [1.1.0] - 2026-02-14

### Added
- Real-time progress bar showing operation progress
- Progress parsing from minipro output
- Auto-hide progress bar after completion (2-second delay)
- Progress label showing current operation and percentage

### Technical
- Smart parsing of minipro output for progress indicators
- Pattern matching for percentages, byte counts, addresses
- Operation detection (Reading, Writing, Verifying, Erasing)
- Completion detection

## [1.0.1] - 2026-02-14

### Fixed
- QColor TypeError in console output (now uses QColor objects instead of strings)
- Wayland platform warning on Linux (force XCB backend)

### Technical
- Added QColor import to fix setTextColor() calls
- Set QT_QPA_PLATFORM environment variable

## [1.0.0] - 2026-02-14

### Added
- Initial release of MiniPro GUI
- Complete PyQt6 frontend for minipro CLI tool
- Device management (detection, search, information)
- Read/Write operations with multiple formats (binary, Intel HEX, Motorola S-Record)
- Memory type selection (code, data, config, user, calibration)
- Firmware management (blank check, erase, firmware update)
- Voltage configuration (VPP, VDD, VCC)
- SPI settings (clock speed)
- Programming options (pulse delay, protection, ICSP)
- Logic/RAM IC testing
- Advanced features (auto-detect, custom commands)
- Dark theme UI
- Color-coded console output
- Real-time command execution in separate thread
- Tabbed interface (Device Info, Read/Write, Firmware, Configuration, Advanced)
- Status bar with messages
- Comprehensive error handling

### Supported Hardware
- T48 programmer (primary target)
- TL866A/CS, TL866II+ (compatible)
- T56, T76 (experimental)

### Documentation
- Comprehensive README with installation and usage guide
- Quick Reference card
- Troubleshooting guide
- Best practices and tips

---

## Version History Summary

- **1.3.3** - Real-time progress (THE BIG FIX!)
- **1.3.0-1.3.2** - Persistent settings, debug mode, progress improvements
- **1.2.x** - Searchable dropdown, device loading
- **1.1.0** - Progress bar
- **1.0.1** - Bug fixes
- **1.0.0** - Initial release

[1.3.3]: https://github.com/yourusername/minipro-gui/releases/tag/v1.3.3
[1.3.2]: https://github.com/yourusername/minipro-gui/releases/tag/v1.3.2
[1.3.1]: https://github.com/yourusername/minipro-gui/releases/tag/v1.3.1
[1.3.0]: https://github.com/yourusername/minipro-gui/releases/tag/v1.3.0
[1.2.1]: https://github.com/yourusername/minipro-gui/releases/tag/v1.2.1
[1.2.0]: https://github.com/yourusername/minipro-gui/releases/tag/v1.2.0
[1.1.0]: https://github.com/yourusername/minipro-gui/releases/tag/v1.1.0
[1.0.1]: https://github.com/yourusername/minipro-gui/releases/tag/v1.0.1
[1.0.0]: https://github.com/yourusername/minipro-gui/releases/tag/v1.0.0
