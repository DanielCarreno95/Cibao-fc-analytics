#!/usr/bin/env python3
"""
Automated Concacaf Caribbean Cup Match Scraper
===============================================

This script automatically discovers and scrapes all matches from the Concacaf Caribbean Cup.
It:
1. Fetches the list of all matches from PerformFeeds API
2. Compares with already scraped matches
3. Scrapes only new matches
4. Can be run on a schedule (cron/launchd) for full automation

Usage:
    python3 scrape_all_concacaf_matches.py [--force] [--dry-run]
"""

import asyncio
import json
import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
import argparse

# Add parent directory to path to import scrape_scoresway_match
sys.path.insert(0, str(Path(__file__).parent))
from scrape_scoresway_match import scrape_match

# Configuration
SDAPI_OUTLET_KEY = 'ft1tiv1inq7v1sk3y9tv12yh5'
TOURNAMENT_CALENDAR_ID = 'bygi47fmsxgbzysjdf9u481lg'
DATA_DIR = Path(__file__).parent.parent.parent / 'data' / 'raw' / 'concacaf' / 'matchstats'
MATCHES_LIST_URL = f"https://api.performfeeds.com/soccerdata/match/{SDAPI_OUTLET_KEY}/?_rt=c&tmcl={TOURNAMENT_CALENDAR_ID}"


def get_scraped_match_ids() -> Set[str]:
    """Get set of already scraped match IDs from existing JSON files."""
    scraped_ids = set()
    if DATA_DIR.exists():
        for json_file in DATA_DIR.glob('*.json'):
            # Extract match ID from filename (format: YYYYMMDD_Team1_vs_Team2.json)
            # Or try to read the JSON and get matchInfo.id
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'matchInfo' in data and 'id' in data['matchInfo']:
                        scraped_ids.add(data['matchInfo']['id'])
            except:
                # If we can't read it, try to extract from filename
                # Filename might contain match ID somewhere
                pass
    return scraped_ids


def parse_matches_xml(xml_content: str) -> List[Dict]:
    """Parse the XML response to extract match information."""
    matches = []
    try:
        root = ET.fromstring(xml_content)
        
        # Find all match elements
        for match_elem in root.findall('.//match'):
            match_info = match_elem.find('matchInfo')
            if match_info is not None:
                match_id = match_info.get('id')
                description = match_info.find('description')
                date_elem = match_info.get('date', '')
                
                if match_id:
                    matches.append({
                        'id': match_id,
                        'description': description.text if description is not None else 'Unknown',
                        'date': date_elem,
                        'status': match_elem.find('.//matchDetails') is not None
                    })
    except ET.ParseError as e:
        print(f"❌ Error parsing XML: {e}")
    except Exception as e:
        print(f"❌ Error extracting matches: {e}")
    
    return matches


def fetch_all_matches() -> List[Dict]:
    """Fetch the list of all matches from PerformFeeds API."""
    import requests
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36',
        'Referer': 'https://www.scoresway.com/',
        'Origin': 'https://www.scoresway.com',
    }
    
    try:
        response = requests.get(MATCHES_LIST_URL, headers=headers, timeout=30)
        if response.status_code == 200:
            matches = parse_matches_xml(response.text)
            return matches
        else:
            print(f"❌ Failed to fetch matches list: HTTP {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Error fetching matches: {e}")
        return []


async def scrape_new_matches(force: bool = False, dry_run: bool = False):
    """Main function to discover and scrape new matches."""
    print("🚀 Concacaf Caribbean Cup - Automated Match Scraper")
    print("=" * 60)
    
    # Ensure data directory exists
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Get already scraped match IDs
    scraped_ids = get_scraped_match_ids()
    print(f"📋 Already scraped: {len(scraped_ids)} matches")
    
    # Fetch all matches from API
    print(f"🔍 Fetching all matches from PerformFeeds API...")
    all_matches = fetch_all_matches()
    
    if not all_matches:
        print("❌ No matches found or failed to fetch")
        return
    
    print(f"✅ Found {len(all_matches)} total matches")
    
    # Filter for new matches
    if force:
        new_matches = all_matches
        print(f"🔄 Force mode: will scrape all {len(new_matches)} matches")
    else:
        new_matches = [m for m in all_matches if m['id'] not in scraped_ids]
        print(f"🆕 New matches to scrape: {len(new_matches)}")
    
    if not new_matches:
        print("✅ All matches already scraped!")
        return
    
    if dry_run:
        print("\n🔍 DRY RUN - Would scrape these matches:")
        for match in new_matches[:10]:  # Show first 10
            print(f"   - {match['id']}: {match['description']} ({match['date']})")
        if len(new_matches) > 10:
            print(f"   ... and {len(new_matches) - 10} more")
        return
    
    # Scrape new matches
    print(f"\n📥 Scraping {len(new_matches)} new matches...")
    success_count = 0
    fail_count = 0
    
    for i, match in enumerate(new_matches, 1):
        match_id = match['id']
        description = match['description']
        print(f"\n[{i}/{len(new_matches)}] {description} ({match_id})")
        
        try:
            result = await scrape_match(match_id)
            if result:
                success_count += 1
                print(f"   ✅ Success")
            else:
                fail_count += 1
                print(f"   ❌ Failed")
        except Exception as e:
            fail_count += 1
            print(f"   ❌ Error: {e}")
        
        # Small delay between requests
        await asyncio.sleep(1)
    
    print("\n" + "=" * 60)
    print(f"✅ Scraping complete!")
    print(f"   Success: {success_count}")
    print(f"   Failed: {fail_count}")
    print(f"   Total scraped: {len(scraped_ids) + success_count}")


def main():
    parser = argparse.ArgumentParser(
        description='Automatically discover and scrape Concacaf Caribbean Cup matches'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='Scrape all matches, even if already scraped'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be scraped without actually scraping'
    )
    
    args = parser.parse_args()
    
    asyncio.run(scrape_new_matches(force=args.force, dry_run=args.dry_run))


if __name__ == "__main__":
    main()

