#!/usr/bin/env python3
"""
Scrape Missing Matches from Scoresway Results Page
==================================================

This script scrapes match IDs from the Scoresway results page for matches
that aren't available via the API (typically historical matches).

Usage:
    python3 scrape_missing_matches_from_scoresway.py
"""

import asyncio
import re
import sys
from pathlib import Path
from playwright.async_api import async_playwright
from typing import List, Dict, Optional

# Add parent directories to path
TEST_DIR = Path(__file__).parent.parent
REPO_ROOT = TEST_DIR.parent
sys.path.insert(0, str(REPO_ROOT / 'src' / 'data_processing'))

from scrape_scoresway_match import scrape_match

# Test output directory
DATA_DIR = TEST_DIR / 'output' / 'matchstats'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Scoresway URLs for different stages
SCORESWAY_URLS = {
    'group_stage': 'https://www.scoresway.com/en_GB/soccer/concacaf-caribbean-cup-2025/bygi47fmsxgbzysjdf9u481lg/results',
    'semi_finals': 'https://www.scoresway.com/en_GB/soccer/concacaf-caribbean-cup-2025/bygi47fmsxgbzysjdf9u481lg/results',
    'third_place': 'https://www.scoresway.com/en_GB/soccer/concacaf-caribbean-cup-2025/bygi47fmsxgbzysjdf9u481lg/results',
    'final': 'https://www.scoresway.com/en_GB/soccer/concacaf-caribbean-cup-2025/bygi47fmsxgbzysjdf9u481lg/results',
}


async def extract_match_ids_from_page(page, url: str) -> List[Dict]:
    """
    Extract match IDs from a Scoresway results page.
    
    Returns:
        List of dictionaries with match_id, description, and date
    """
    print(f"🌐 Loading: {url}")
    await page.goto(url, wait_until='networkidle', timeout=30000)
    await page.wait_for_timeout(2000)  # Wait for page to fully load
    
    match_ids = []
    
    try:
        # Look for match links - Scoresway uses /match/view/{match_id} pattern
        # We can extract match IDs from href attributes
        match_links = await page.query_selector_all('a[href*="/match/view/"]')
        
        print(f"   Found {len(match_links)} potential match links")
        
        for link in match_links:
            try:
                href = await link.get_attribute('href')
                if href:
                    # Extract match ID from URL: /match/view/{match_id}
                    match = re.search(r'/match/view/([a-z0-9]+)', href)
                    if match:
                        match_id = match.group(1)
                        
                        # Try to get match description (team names)
                        description = await link.text_content()
                        description = description.strip() if description else 'Unknown'
                        
                        # Try to get date from nearby elements
                        # Dates are usually in a parent container
                        parent = await link.evaluate_handle('(el) => el.closest("tr, .match-row, .result-item")')
                        date_text = None
                        if parent:
                            try:
                                date_elem = await parent.query_selector('.date, [class*="date"], time')
                                if date_elem:
                                    date_text = await date_elem.text_content()
                            except:
                                pass
                        
                        if match_id not in [m['id'] for m in match_ids]:
                            match_ids.append({
                                'id': match_id,
                                'description': description,
                                'date': date_text or 'Unknown',
                                'url': f"https://www.scoresway.com{href}" if href.startswith('/') else href
                            })
            except Exception as e:
                continue
        
        # Alternative: Extract from page JavaScript/data attributes
        # Some pages store match data in JavaScript variables
        try:
            page_content = await page.content()
            # Look for match IDs in JavaScript
            js_match_ids = re.findall(r'match/view/([a-z0-9]{20,})', page_content)
            for match_id in js_match_ids:
                if match_id not in [m['id'] for m in match_ids]:
                    match_ids.append({
                        'id': match_id,
                        'description': 'Unknown',
                        'date': 'Unknown',
                        'url': f"https://www.scoresway.com/en_GB/soccer/concacaf-caribbean-cup-2025/bygi47fmsxgbzysjdf9u481lg/match/view/{match_id}"
                    })
        except:
            pass
        
    except Exception as e:
        print(f"   ⚠️  Error extracting match IDs: {e}")
    
    return match_ids


async def scrape_missing_matches():
    """Main function to scrape missing matches from Scoresway."""
    print("🧪 Scraping Missing Matches from Scoresway")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        all_match_ids = []
        
        # Scrape from results page
        results_url = SCORESWAY_URLS['group_stage']
        match_ids = await extract_match_ids_from_page(page, results_url)
        all_match_ids.extend(match_ids)
        
        print(f"\n✅ Found {len(all_match_ids)} matches from Scoresway page")
        
        # Remove duplicates
        seen_ids = set()
        unique_matches = []
        for match in all_match_ids:
            if match['id'] not in seen_ids:
                seen_ids.add(match['id'])
                unique_matches.append(match)
        
        print(f"📋 Unique matches: {len(unique_matches)}")
        print("\nMatches found:")
        for i, match in enumerate(unique_matches[:20], 1):
            print(f"   {i}. {match['description']} ({match['date']}) - {match['id'][:20]}...")
        if len(unique_matches) > 20:
            print(f"   ... and {len(unique_matches) - 20} more")
        
        await browser.close()
        
        # Now scrape the matches
        if unique_matches:
            print(f"\n📥 Scraping {len(unique_matches)} matches...")
            success_count = 0
            fail_count = 0
            
            for i, match in enumerate(unique_matches, 1):
                match_id = match['id']
                description = match['description']
                print(f"\n[{i}/{len(unique_matches)}] {description} ({match_id})")
                
                try:
                    result = await scrape_match(match_id, output_dir=DATA_DIR)
                    if result:
                        success_count += 1
                        print(f"   ✅ Success")
                    else:
                        fail_count += 1
                        print(f"   ❌ Failed")
                except Exception as e:
                    fail_count += 1
                    print(f"   ❌ Error: {e}")
                
                await asyncio.sleep(1)
            
            print("\n" + "=" * 60)
            print(f"✅ Scraping complete!")
            print(f"   Success: {success_count}")
            print(f"   Failed: {fail_count}")


if __name__ == "__main__":
    asyncio.run(scrape_missing_matches())

