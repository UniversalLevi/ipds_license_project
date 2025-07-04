#!/usr/bin/env python3
"""
ZAYONA License Management Client (CLI Only)
Entry point for the CLI-based license management tool.
"""

import sys
import os

# Ensure agent_cli.py is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agent'))

from agent_cli import main

if __name__ == "__main__":
    main() 