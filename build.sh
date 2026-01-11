#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright
playwright install chromium

# Install system dependencies for Playwright
playwright install-deps chromium