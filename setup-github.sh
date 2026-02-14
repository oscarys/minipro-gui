#!/bin/bash
# GitHub Repository Setup Script for MiniPro GUI
# This script automates the initial repository setup

set -e  # Exit on error

echo "=========================================="
echo "MiniPro GUI - GitHub Setup Script"
echo "=========================================="
echo ""

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo "❌ Error: git is not installed"
    echo "Install it with: sudo apt-get install git"
    exit 1
fi

echo "✓ Git is installed"

# Check if we're in the right directory
if [ ! -f "minipro_gui.py" ]; then
    echo "❌ Error: minipro_gui.py not found"
    echo "Please run this script from the minipro-gui-project directory"
    exit 1
fi

echo "✓ Found project files"

# Check if already a git repository
if [ -d ".git" ]; then
    echo "⚠️  Warning: This is already a git repository"
    read -p "Do you want to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
else
    echo "✓ Not yet a git repository"
fi

echo ""
echo "Choose setup method:"
echo "1) GitHub CLI (gh) - Recommended, easiest"
echo "2) Manual - You'll create repo on GitHub website"
echo "3) Exit"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        # GitHub CLI method
        echo ""
        echo "Using GitHub CLI method..."
        
        # Check if gh is installed
        if ! command -v gh &> /dev/null; then
            echo "❌ Error: GitHub CLI (gh) is not installed"
            echo "Install it from: https://cli.github.com/"
            echo "Or use Method 2 (manual setup)"
            exit 1
        fi
        
        echo "✓ GitHub CLI is installed"
        
        # Check if authenticated
        if ! gh auth status &> /dev/null; then
            echo ""
            echo "You need to authenticate with GitHub..."
            gh auth login
        fi
        
        echo "✓ Authenticated with GitHub"
        
        # Ask for repo name
        echo ""
        read -p "Repository name (default: minipro-gui): " repo_name
        repo_name=${repo_name:-minipro-gui}
        
        # Ask for public/private
        echo ""
        echo "Repository visibility:"
        echo "1) Public (recommended for open source)"
        echo "2) Private"
        read -p "Choose (1-2): " visibility
        
        if [ "$visibility" = "2" ]; then
            visibility_flag="--private"
        else
            visibility_flag="--public"
        fi
        
        # Initialize git if needed
        if [ ! -d ".git" ]; then
            echo ""
            echo "Initializing git repository..."
            git init
            echo "✓ Git repository initialized"
        fi
        
        # Configure git if needed
        if [ -z "$(git config user.name)" ]; then
            echo ""
            read -p "Enter your name for git commits: " git_name
            git config user.name "$git_name"
        fi
        
        if [ -z "$(git config user.email)" ]; then
            echo ""
            read -p "Enter your email for git commits: " git_email
            git config user.email "$git_email"
        fi
        
        # Add and commit files
        echo ""
        echo "Adding files to git..."
        git add .
        
        echo "Creating initial commit..."
        git commit -m "Initial commit: MiniPro GUI v1.3.3

- Complete PyQt6 frontend for minipro CLI tool
- Real-time progress bar with stderr parsing
- Searchable device dropdown (13,000+ devices)
- Persistent settings with QSettings
- Debug mode for troubleshooting
- Dark theme UI with color-coded console
- Support for T48, TL866A/CS, TL866II+ programmers"
        
        echo "✓ Initial commit created"
        
        # Create repository and push
        echo ""
        echo "Creating GitHub repository and pushing..."
        gh repo create "$repo_name" $visibility_flag --source=. --push
        
        echo ""
        echo "=========================================="
        echo "✅ SUCCESS!"
        echo "=========================================="
        echo ""
        echo "Your repository is now on GitHub!"
        echo "View it at: https://github.com/$(gh api user -q .login)/$repo_name"
        echo ""
        echo "Next steps:"
        echo "1. Add topics/tags to your repo"
        echo "2. Create a release for v1.3.3"
        echo "3. Enable Discussions (optional)"
        echo ""
        echo "See GITHUB_SETUP.md for detailed instructions"
        ;;
        
    2)
        # Manual method
        echo ""
        echo "Using manual method..."
        echo ""
        echo "Follow these steps:"
        echo ""
        echo "1. Go to: https://github.com/new"
        echo "2. Repository name: minipro-gui"
        echo "3. Description: PyQt6 GUI for T48 MiniPro device programmer"
        echo "4. Choose Public or Private"
        echo "5. DO NOT initialize with README, .gitignore, or license"
        echo "6. Click 'Create repository'"
        echo ""
        read -p "Press Enter when you've created the repository..."
        
        # Get GitHub username
        echo ""
        read -p "Enter your GitHub username: " github_user
        
        # Initialize git if needed
        if [ ! -d ".git" ]; then
            echo ""
            echo "Initializing git repository..."
            git init
            echo "✓ Git repository initialized"
        fi
        
        # Configure git if needed
        if [ -z "$(git config user.name)" ]; then
            echo ""
            read -p "Enter your name for git commits: " git_name
            git config user.name "$git_name"
        fi
        
        if [ -z "$(git config user.email)" ]; then
            echo ""
            read -p "Enter your email for git commits: " git_email
            git config user.email "$git_email"
        fi
        
        # Add and commit files
        echo ""
        echo "Adding files to git..."
        git add .
        
        echo "Creating initial commit..."
        git commit -m "Initial commit: MiniPro GUI v1.3.3

- Complete PyQt6 frontend for minipro CLI tool
- Real-time progress bar with stderr parsing
- Searchable device dropdown (13,000+ devices)
- Persistent settings with QSettings
- Debug mode for troubleshooting
- Dark theme UI with color-coded console
- Support for T48, TL866A/CS, TL866II+ programmers"
        
        echo "✓ Initial commit created"
        
        # Add remote and push
        echo ""
        echo "Adding remote repository..."
        git remote add origin "https://github.com/$github_user/minipro-gui.git"
        
        echo "Setting main branch..."
        git branch -M main
        
        echo "Pushing to GitHub..."
        git push -u origin main
        
        echo ""
        echo "=========================================="
        echo "✅ SUCCESS!"
        echo "=========================================="
        echo ""
        echo "Your repository is now on GitHub!"
        echo "View it at: https://github.com/$github_user/minipro-gui"
        echo ""
        echo "Next steps:"
        echo "1. Add topics/tags to your repo"
        echo "2. Create a release for v1.3.3"
        echo "3. Enable Discussions (optional)"
        echo ""
        echo "See GITHUB_SETUP.md for detailed instructions"
        ;;
        
    3)
        echo "Exiting..."
        exit 0
        ;;
        
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac

# Offer to create initial tag
echo ""
read -p "Create v1.3.3 tag for releases? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git tag -a v1.3.3 -m "Release v1.3.3: Real-time progress updates"
    git push origin v1.3.3
    echo "✓ Tag v1.3.3 created and pushed"
    echo "Now go to GitHub → Releases to publish the release!"
fi

echo ""
echo "Setup complete! Happy coding! 🚀"
