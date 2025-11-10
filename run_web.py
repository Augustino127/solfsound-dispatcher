#!/usr/bin/env python
"""
Launch script for SolfSound Dispatcher Web Interface
"""

import sys
import argparse
from src.solfsound.web_server import start_server


def main():
    parser = argparse.ArgumentParser(description="SolfSound Dispatcher Web Server")
    parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0 - all interfaces)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to listen on (default: 8000)"
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development"
    )

    args = parser.parse_args()

    try:
        start_server(host=args.host, port=args.port, reload=args.reload)
    except KeyboardInterrupt:
        print("\n\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"\nError starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
