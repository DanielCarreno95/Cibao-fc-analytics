#!/usr/bin/env python3
"""
Get All Match IDs from Scoresway Results Page
==============================================

This script scrapes the Scoresway results page to get ALL match IDs,
including historical matches that aren't available via the API.

Usage:
    python3 get_all_match_ids_from_scoresway.py
"""

import asyncio
import re
import json
from pathlib import Path
from playwright.async_api import async_playwright
from typing import List, Dict, Set

# Scoresway results URL
RESULTS_URL = 'https://www.scoresway.com/en_GB/soccer/concacaf-caribbean-cup-2025/bygi47fmsxgbzysjdf9u481lg/results'


async def extract_all_match_ids():
    """Extract all match IDs from Scoresway results page by intercepting API calls."""
    print("🌐 Loading Scoresway results page...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        # Capture all responses
        captured_responses = []
        
        async def handle_response(response):
            """Capture API responses that might contain match data."""
            url = response.url
            # Check if this is a match-related API call
            if any(keyword in url.lower() for keyword in ['match', 'performfeeds', 'soccerdata']):
                try:
                    # Try to get JSON response
                    if 'application/json' in response.headers.get('content-type', ''):
                        data = await response.json()
                        captured_responses.append((url, data))
                    # Or XML
                    elif 'xml' in response.headers.get('content-type', ''):
                        text = await response.text()
                        captured_responses.append((url, text))
                except:
                    pass
        
        page.on('response', handle_response)
        
        try:
            await page.goto(RESULTS_URL, wait_until='networkidle', timeout=60000)
            await page.wait_for_timeout(5000)  # Wait for all API calls to complete
            
            print("📄 Page loaded, analyzing captured responses...")
            print(f"   Captured {len(captured_responses)} API responses")
            
            all_match_ids = []
            
            # Parse captured responses for match data
            import xml.etree.ElementTree as ET
            
            for url, data in captured_responses:
                try:
                    # If it's XML (from PerformFeeds)
                    if isinstance(data, str) and data.strip().startswith('<'):
                        root = ET.fromstring(data)
                        for match_elem in root.findall('.//match'):
                            match_info = match_elem.find('matchInfo')
                            if match_info is not None:
                                match_id = match_info.get('id')
                                if match_id:
                                    desc = match_info.find('description')
                                    description = desc.text if desc is not None else 'Unknown'
                                    date = match_info.get('date', 'Unknown')
                                    
                                    if match_id not in [m['id'] for m in all_match_ids]:
                                        all_match_ids.append({
                                            'id': match_id,
                                            'description': description,
                                            'date': date,
                                            'source': 'api_xml'
                                        })
                    
                    # If it's JSON
                    elif isinstance(data, dict):
                        # Look for match structures
                        def find_matches(obj, path=""):
                            matches = []
                            if isinstance(obj, dict):
                                if 'id' in obj and 'description' in obj and len(obj.get('id', '')) > 15:
                                    # Might be a match
                                    matches.append(obj)
                                for key, value in obj.items():
                                    matches.extend(find_matches(value, f"{path}.{key}"))
                            elif isinstance(obj, list):
                                for item in obj:
                                    matches.extend(find_matches(item, path))
                            return matches
                        
                        found_matches = find_matches(data)
                        for match_obj in found_matches:
                            match_id = match_obj.get('id')
                            if match_id and len(match_id) > 15:
                                if match_id not in [m['id'] for m in all_match_ids]:
                                    all_match_ids.append({
                                        'id': match_id,
                                        'description': match_obj.get('description', 'Unknown'),
                                        'date': match_obj.get('date', 'Unknown'),
                                        'source': 'api_json'
                                    })
                except Exception as e:
                    continue
            
            # Also try to extract from page content as fallback
            page_content = await page.content()
            match_ids_from_page = re.findall(r'match/view/([a-z0-9]{20,})', page_content)
            for match_id in match_ids_from_page:
                if match_id not in [m['id'] for m in all_match_ids]:
                    all_match_ids.append({
                        'id': match_id,
                        'description': 'Unknown',
                        'date': 'Unknown',
                        'source': 'page_content'
                    })
            
            await browser.close()
            
            # Remove duplicates
            seen_ids = set()
            unique_matches = []
            for match in all_match_ids:
                if match['id'] not in seen_ids:
                    seen_ids.add(match['id'])
                    unique_matches.append(match)
            
            return unique_matches
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            await browser.close()
            return []


async def main():
    """Main function."""
    print("🔍 Extracting All Match IDs from Scoresway")
    print("=" * 60)
    
    matches = await extract_all_match_ids()
    
    if not matches:
        print("❌ No matches found")
        return
    
    print(f"\n✅ Found {len(matches)} unique match IDs")
    
    # Save to file
    output_file = Path(__file__).parent.parent / 'output' / 'all_match_ids.json'
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        json.dump(matches, f, indent=2)
    
    print(f"💾 Saved to: {output_file}")
    
    # Show breakdown
    print(f"\n📊 Match breakdown:")
    print(f"   Total matches: {len(matches)}")
    
    # Group by source
    by_source = {}
    for match in matches:
        source = match.get('source', 'unknown')
        by_source[source] = by_source.get(source, 0) + 1
    
    for source, count in by_source.items():
        print(f"   From {source}: {count}")
    
    # Show first 10
    print(f"\n📋 First 10 matches:")
    for i, match in enumerate(matches[:10], 1):
        desc = match.get('description', 'Unknown')
        if desc == 'Unknown':
            desc = f"Match {match['id'][:20]}..."
        print(f"   {i}. {desc} ({match['id'][:20]}...)")


if __name__ == "__main__":
    asyncio.run(main())

