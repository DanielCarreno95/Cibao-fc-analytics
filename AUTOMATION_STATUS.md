# Scoresway Automation Status

## ✅ Current Automation Level: **FULLY AUTOMATED**

We can now fully automate the entire process from discovering matches to scraping them!

## What We Have

### 1. **Match Discovery** ✅
- **Script**: `src/data_processing/scrape_all_concacaf_matches.py`
- **Method**: Calls PerformFeeds API to get list of all matches
- **Endpoint**: `https://api.performfeeds.com/soccerdata/match/{SDAPI_OUTLET_KEY}/?_rt=c&tmcl={TOURNAMENT_ID}`
- **Returns**: XML with all matches in the tournament
- **Automation**: ✅ Fully automatic - no manual match ID entry needed

### 2. **Match Scraping** ✅
- **Script**: `src/data_processing/scrape_scoresway_match.py`
- **Method**: Uses PerformFeeds matchstats API with credentials
- **Endpoint**: `https://api.performfeeds.com/soccerdata/matchstats/{SDAPI_OUTLET_KEY}/{match_id}?_rt=c&_lcl=en&_fmt=jsonp&sps=widgets&_clbk={CALLBACK_ID}`
- **Credentials**: 
  - `SDAPI_OUTLET_KEY`: `ft1tiv1inq7v1sk3y9tv12yh5`
  - `CALLBACK_ID`: `W34bead4c41ca9fb2b9da261f6a64f68abed1d2172`
- **Automation**: ✅ Fully automatic - works with just match ID

### 3. **Incremental Scraping** ✅
- **Feature**: Automatically detects which matches are already scraped
- **Method**: Checks existing JSON files in `data/raw/concacaf/matchstats/`
- **Result**: Only scrapes new matches
- **Automation**: ✅ Fully automatic - no manual tracking needed

## How to Use

### Option 1: Scrape All New Matches (Recommended)
```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
source .venv/bin/activate
python3 src/data_processing/scrape_all_concacaf_matches.py
```

### Option 2: Dry Run (See What Would Be Scraped)
```bash
python3 src/data_processing/scrape_all_concacaf_matches.py --dry-run
```

### Option 3: Force Re-scrape All Matches
```bash
python3 src/data_processing/scrape_all_concacaf_matches.py --force
```

### Option 4: Scrape Single Match (Manual)
```bash
python3 src/data_processing/scrape_scoresway_match.py <match_id>
```

## Scheduling (Fully Automated)

### macOS (launchd)
Create `~/Library/LaunchAgents/com.cibao.scrape_matches.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cibao.scrape_matches</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics/src/data_processing/scrape_all_concacaf_matches.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics</string>
    <key>StartInterval</key>
    <integer>3600</integer>
    <key>RunAtLoad</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics/logs/scrape_matches.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics/logs/scrape_matches_error.log</string>
</dict>
</plist>
```

Load it:
```bash
launchctl load ~/Library/LaunchAgents/com.cibao.scrape_matches.plist
```

### Linux/Unix (cron)
Add to crontab (`crontab -e`):
```bash
# Run every hour
0 * * * * cd "/path/to/Cibao-fc-analytics" && /usr/bin/python3 src/data_processing/scrape_all_concacaf_matches.py >> logs/scrape_matches.log 2>&1
```

## What Happens Automatically

1. **Discovery**: Script fetches list of all matches from PerformFeeds API
2. **Comparison**: Compares with already scraped matches (checks JSON files)
3. **Filtering**: Identifies new matches that haven't been scraped
4. **Scraping**: Automatically scrapes each new match
5. **Saving**: Saves JSON files to `data/raw/concacaf/matchstats/`
6. **Logging**: Reports success/failure for each match

## Manual Steps Required

**NONE!** 🎉

The entire process is fully automated. The only manual step would be:
- Setting up the schedule (one-time setup)
- Monitoring logs if something goes wrong

## Next Steps for Full Pipeline

1. ✅ **Match Discovery** - DONE
2. ✅ **Match Scraping** - DONE
3. ⏳ **JSON to Excel Conversion** - Already have scripts (`convert_all_json_to_excel.py`)
4. ⏳ **Excel Processing** - Already have scripts
5. ⏳ **Streamlit Refresh** - Add refresh button to Streamlit app

## Limitations

- **Credentials**: The API credentials are hardcoded. If they expire, they'll need to be updated.
- **Rate Limiting**: We add 1-second delays between requests to be respectful.
- **Error Handling**: If a match fails to scrape, it's logged but the script continues.

## Summary

**Yes, this is as automated as we can get!** 🚀

The process is:
- ✅ Fully automatic match discovery
- ✅ Fully automatic scraping
- ✅ Fully automatic incremental updates (only new matches)
- ✅ Can be scheduled to run automatically
- ✅ No manual intervention needed

The only thing left is to:
1. Set up the schedule (cron/launchd)
2. Integrate with the Excel conversion pipeline
3. Add Streamlit refresh mechanism

