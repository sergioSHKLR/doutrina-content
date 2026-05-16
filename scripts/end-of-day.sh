#!/bin/bash
# Navigate to your project directory
cd "$HOME/doutrina-content" || exit

# Ensure you are on the dev branch
git checkout dev

# Stage all changes made today
git add .

# Commit with a timestamped message
git commit -m "Automated daily snapshot: $(date +'%Y-%m-%d %H:%M:%S')"

# Push safely to the cloud sandbox
git push origin dev