#!/usr/bin/env python3
"""
Get Tournament ID for a Specific Competition (TEST VERSION)
============================================================

This is a test version that doesn't interfere with production scripts.
Use this to test competition filtering functionality.

Usage:
    python3 get_tournament_id_test.py "Concacaf Caribbean Cup"
    python3 get_tournament_id_test.py --list  # List all available competitions
"""

import sys
from pathlib import Path

# Add the parent data_processing directory to path to import from production
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src' / 'data_processing'))

# Import from the production script
from get_tournament_id import main

if __name__ == "__main__":
    print("🧪 TEST MODE - Competition Filtering")
    print("=" * 60)
    main()

