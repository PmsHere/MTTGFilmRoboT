#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Set the default repository if UPSTREAM_REPO is not set
: ${UPSTREAM_REPO:="https://github.com/PmsHere/MTTGFilmRoboT"}

# Clone the repository
echo "Cloning Repository from $UPSTREAM_REPO"
git clone $UPSTREAM_REPO /MTTGFilmRoboT

# Change directory to the cloned repository
cd /MTTGFilmRoboT

# Install dependencies
pip3 install -U -r requirements.txt

# Start the bot
echo "Bot Started...."
python3 bot.py
