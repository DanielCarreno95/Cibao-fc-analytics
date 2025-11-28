# API Configuration and Parameters

## ✅ Solution: Page Size Parameter

The PerformFeeds API endpoint supports a `_pgSz` (page size) parameter that controls how many matches are returned.

### Correct Usage
- **API Endpoint**: `https://api.performfeeds.com/soccerdata/match/{SDAPI_OUTLET_KEY}/?_rt=c&tmcl={TOURNAMENT_CALENDAR_ID}&_pgSz=400`
- **With `_pgSz=400`**: Returns **all matches** including August (28 matches total)
- **Without `_pgSz`**: Returns only **20 matches** (September onwards)

### Discovery
This parameter was discovered by inspecting the Scoresway website's network requests, which showed `_pgSz=400` in the API calls.

### Previous Issue (Now Resolved)

**Before discovering `_pgSz` parameter:**

#### 1. **Hard Result Limit (Most Likely)**
- The endpoint returns **exactly 20 matches** - this is likely a hard-coded limit
- Common API design pattern to prevent large response payloads
- Performance optimization to reduce server load and response times

#### 2. **Date-Based Filtering (Very Likely)**
- API returns matches from **September 2025 onwards** (71+ days old)
- August matches are **87+ days old** and excluded
- Suggests a "recent matches only" design (last ~2-3 months)
- May be designed for "active" or "current" tournament phase

#### 3. **Performance & Resource Management**
- Limiting results reduces:
  - Database query time
  - Network bandwidth
  - Response parsing time
  - Server resource usage

#### 4. **API Tier/Plan Limitations**
- Free or basic API tiers often have result limits
- Enterprise plans may have higher limits or pagination
- The `_rt=c` parameter might indicate a "compact" response type with limits

#### 5. **Tournament Stage Filtering**
- May only return matches from "active" or "recent" stages
- August matches were in Group Stage (completed)
- API might prioritize current/upcoming stages

#### 6. **Data Archival**
- Older matches might be archived in a different database/partition
- Historical data may require different endpoints or parameters
- August matches accessible individually but not in list queries

#### 7. **Business Logic**
- Designed for "current season" or "active matches"
- Historical data may be considered "archived" and excluded from list queries
- Individual match access still works (matches exist, just not in lists)

### Evidence
- ✅ Same tournament calendar ID for August and September matches
- ✅ Individual August matches ARE accessible via direct API calls
- ✅ Exactly 20 matches returned (hard limit, not pagination)
- ✅ All returned matches are September+ (date cutoff)
- ✅ No pagination parameters or metadata in response
- ✅ No alternative endpoints found (stage, series, competition all 404)

### Current Solution

**With `_pgSz=400` parameter:**
- ✅ API returns **all 28 matches** including August
- ✅ No need for separate handling of historical vs new matches
- ✅ Automation script works seamlessly for all matches
- ✅ Complete coverage from tournament start to present

### Expected Match Counts

**Concacaf Caribbean Cup 2025:**
- **Total Results**: 26 matches (as of November 2025)
- **Future Fixtures**: 2 matches
- **API Returns**: ~20 matches (September onwards)
- **Historical (August)**: 8 matches (already in files, not in API)

### Verification

To verify you have all matches:

```bash
# Count total match files
ls data/raw/concacaf/matchstats/*.json | wc -l

# Should show ~26 result files + any future fixtures that were scraped
```

### Manual Scraping for Historical Matches

If you need to re-scrape historical matches, you can:

1. **Use individual match scraping**:
   ```bash
   python3 src/data_processing/scrape_scoresway_match.py <match_id>
   ```

2. **Get match IDs from existing files**:
   ```bash
   python3 -c "
   import json
   from pathlib import Path
   for f in Path('data/raw/concacaf/matchstats').glob('*.json'):
       with open(f) as file:
           data = json.load(file)
           print(f\"{data['matchInfo']['id']}: {data['matchInfo'].get('description', 'Unknown')}\")
   "
   ```

### Future Improvements

Possible solutions for getting all historical matches:
1. **Check Scoresway website directly** - May have all matches listed
2. **Use different API endpoint** - May need competition-specific endpoint
3. **Scrape by stage** - Try fetching matches by tournament stage
4. **Date range parameters** - Check if API supports date range queries

---

**Last Updated**: November 2025

