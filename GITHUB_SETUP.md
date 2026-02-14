# GitHub Repository Setup Guide

This guide will help you create and push this project to GitHub.

## Prerequisites

1. **Git installed**
   ```bash
   git --version
   ```
   If not installed: `sudo apt-get install git` (Linux) or download from https://git-scm.com/

2. **GitHub account**
   - Create one at https://github.com if you don't have it

3. **GitHub CLI (optional but recommended)**
   ```bash
   gh --version
   ```
   If not installed: https://cli.github.com/

## Method 1: Using GitHub CLI (Easiest)

### Step 1: Authenticate with GitHub
```bash
gh auth login
```
Follow the prompts to authenticate.

### Step 2: Create Repository and Push
```bash
cd /path/to/minipro-gui-project

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: MiniPro GUI v1.3.3

- Complete PyQt6 frontend for minipro CLI tool
- Real-time progress bar with stderr parsing
- Searchable device dropdown (13,000+ devices)
- Persistent settings with QSettings
- Debug mode for troubleshooting
- Dark theme UI with color-coded console
- Support for T48, TL866A/CS, TL866II+ programmers"

# Create GitHub repo and push
gh repo create minipro-gui --public --source=. --push

# Or for private repo:
# gh repo create minipro-gui --private --source=. --push
```

Done! Your repository is now on GitHub.

## Method 2: Manual Setup (Traditional)

### Step 1: Create Repository on GitHub
1. Go to https://github.com/new
2. Repository name: `minipro-gui`
3. Description: `PyQt6 GUI for T48 MiniPro device programmer with real-time progress and 13K+ device support`
4. Choose Public or Private
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

### Step 2: Initialize Local Repository
```bash
cd /path/to/minipro-gui-project

# Initialize git repository
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: MiniPro GUI v1.3.3

- Complete PyQt6 frontend for minipro CLI tool
- Real-time progress bar with stderr parsing
- Searchable device dropdown (13,000+ devices)
- Persistent settings with QSettings
- Debug mode for troubleshooting
- Dark theme UI with color-coded console
- Support for T48, TL866A/CS, TL866II+ programmers"
```

### Step 3: Connect to GitHub and Push
```bash
# Add remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/minipro-gui.git

# Verify remote
git remote -v

# Push to GitHub
git branch -M main
git push -u origin main
```

## Method 3: Using SSH (For Advanced Users)

If you have SSH keys set up with GitHub:

```bash
cd /path/to/minipro-gui-project

git init
git add .
git commit -m "Initial commit: MiniPro GUI v1.3.3"

# Add remote with SSH
git remote add origin git@github.com:YOUR_USERNAME/minipro-gui.git

git branch -M main
git push -u origin main
```

## Verify Everything Worked

1. Visit your repository: `https://github.com/YOUR_USERNAME/minipro-gui`
2. You should see:
   - ✅ README.md displaying as the main page
   - ✅ All files listed
   - ✅ License file recognized
   - ✅ Initial commit message

## Next Steps

### Add Topics/Tags
On your GitHub repository page:
1. Click "⚙️ Settings" (top right of About section)
2. Add topics: `python`, `pyqt6`, `t48`, `programmer`, `gui`, `minipro`, `eeprom`, `firmware`
3. Add description: "PyQt6 GUI for T48 MiniPro device programmer with real-time progress and 13K+ device support"
4. Add website (if you have one)

### Create a Release (v1.3.3)
```bash
# Tag the current commit
git tag -a v1.3.3 -m "Release v1.3.3: Real-time progress updates"

# Push the tag
git push origin v1.3.3
```

Then on GitHub:
1. Go to "Releases"
2. Click "Draft a new release"
3. Choose tag: v1.3.3
4. Release title: "v1.3.3 - Real-Time Progress Updates"
5. Description: Copy from CHANGELOG.md
6. Publish release

### Enable GitHub Features

**Issues:**
- Already enabled by default
- Users can report bugs and request features

**Discussions:**
- Go to Settings → Features
- Enable "Discussions"
- Great for Q&A and community

**GitHub Pages (Optional):**
- Can host documentation
- Settings → Pages → Source: gh-pages branch

**GitHub Actions (Future):**
- Can add automated testing
- PyQt tests, linting, etc.

## Troubleshooting

### "fatal: not a git repository"
Make sure you're in the right directory:
```bash
cd /path/to/minipro-gui-project
pwd
```

### Authentication Issues
If you get authentication errors:
```bash
# Configure git credentials
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Use GitHub CLI for auth
gh auth login
```

### Push Rejected
If remote has changes:
```bash
git pull origin main --rebase
git push origin main
```

### Wrong Remote URL
To change remote:
```bash
git remote set-url origin https://github.com/YOUR_USERNAME/minipro-gui.git
```

## Repository Settings Recommendations

### Branch Protection
Once you have collaborators:
- Settings → Branches → Add rule for `main`
- Require pull request reviews
- Require status checks

### Security
- Settings → Security → Enable Dependabot alerts
- Review security advisories regularly

### Collaborators
- Settings → Collaborators
- Add contributors as needed

## Making Future Changes

```bash
# Make your changes to files

# Check status
git status

# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add support for custom device profiles"

# Push to GitHub
git push origin main
```

## Getting Help

- GitHub Docs: https://docs.github.com
- Git Docs: https://git-scm.com/doc
- GitHub CLI Docs: https://cli.github.com/manual/

---

**Ready to go?** Choose Method 1 (GitHub CLI) for the easiest experience!
