#!/usr/bin/env python
"""
Launch script for SolfSound Dispatcher Desktop Application
"""

import sys

try:
    from src.solfsound.desktop_app import main
except ImportError as e:
    print(f"Error importing desktop app: {e}")
    print("\nPlease make sure all dependencies are installed:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error running desktop app: {e}")
        sys.exit(1)
