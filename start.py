#!/usr/bin/env python3
import subprocess
import sys
import os

def install_playwright_browsers():
    """Install Playwright browsers if not already installed"""
    try:
        print("Installing Playwright browsers...")
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)
        print("Playwright browsers installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install Playwright browsers: {e}")
        sys.exit(1)

def main():
    # Install browsers first
    install_playwright_browsers()
    
    # Import and run the main application
    from main import app
    import uvicorn
    
    port = int(os.environ.get("PORT", 8001))
    print(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()