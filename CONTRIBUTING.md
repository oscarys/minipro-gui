# Contributing to MiniPro GUI

Thank you for considering contributing to MiniPro GUI! This document provides guidelines for contributing to the project.

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- **Clear title** describing the problem
- **Steps to reproduce** the issue
- **Expected behavior** vs actual behavior
- **Environment details**: OS, Python version, PyQt6 version, minipro version
- **Console output** if relevant (enable Debug Mode)
- **Screenshots** if applicable

### Suggesting Features

Feature requests are welcome! Please:
- Check existing issues first to avoid duplicates
- Describe the feature and use case clearly
- Explain why it would be useful
- Consider how it fits with existing features

### Submitting Pull Requests

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/your-feature-name`
3. **Make your changes**
4. **Test thoroughly**:
   - Test with actual hardware if possible
   - Enable Debug Mode to check console output
   - Test on your platform (Linux/Windows/macOS)
5. **Follow code style**:
   - Use existing code style (PEP 8 generally)
   - Add docstrings for new functions
   - Comment complex logic
6. **Commit with clear messages**:
   - Use present tense: "Add feature" not "Added feature"
   - Reference issues: "Fix #123: Resolve progress bar bug"
7. **Push and create PR**
8. **Describe your changes** in the PR description

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/minipro-gui.git
cd minipro-gui

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python3 minipro_gui.py
```

## Code Guidelines

### Python Style
- Follow PEP 8 generally
- Use meaningful variable names
- Keep functions focused and single-purpose
- Add type hints where helpful

### PyQt6 Conventions
- Use signal/slot connections properly
- Keep UI updates in main thread
- Use QThread for long-running operations
- Follow Qt naming conventions for UI elements

### Git Commit Messages
Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

Examples:
- `feat: Add support for T56 programmer`
- `fix: Resolve progress bar buffering issue`
- `docs: Update installation instructions`

## Testing

### Manual Testing Checklist
- [ ] Programmer detection works
- [ ] Device selection from dropdown
- [ ] Read operation completes successfully
- [ ] Write operation completes successfully
- [ ] Progress bar updates in real-time
- [ ] Settings persist between sessions
- [ ] Debug mode shows parsing output
- [ ] Erase button works correctly
- [ ] Console colors display correctly
- [ ] No errors in terminal output

### Testing with Hardware
If you have access to hardware:
- Test with different chip types (EEPROM, SPI Flash, GAL, etc.)
- Verify voltage settings work correctly
- Test with different file formats (binary, ihex, srec)
- Try various programmer operations

### Testing Without Hardware
- UI functionality should work without hardware
- Device list loading should work
- File dialogs should work
- Settings persistence should work

## Areas for Contribution

### High Priority
- Windows compatibility testing
- macOS compatibility testing
- Support for other programmers (T56, T76)
- Unit tests for core functions
- Automated UI tests

### Medium Priority
- Device-specific progress patterns
- Batch operations (multiple chips)
- Hex editor integration
- Custom chip database
- Import/export settings

### Nice to Have
- Themes (light mode option)
- Internationalization (i18n)
- Keyboard shortcuts
- Command history
- Operation presets

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Reach out to maintainers

## License

By contributing, you agree that your contributions will be licensed under the GNU General Public License v3.0, the same license as the project.

Thank you for contributing! 🎉
