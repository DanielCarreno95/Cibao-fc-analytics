# How to Update Streamlit App with New Match Data

## Quick Summary

The Streamlit app automatically reads from `data/raw/concacaf/matchstats/` directory. After scraping new matches, you need to:

1. **Copy new files** from Automation Testing to main data directory
2. **Clear Streamlit cache** (restart app or use cache button)

---

## Step-by-Step Process

### Option 1: Automated Copy Script (Recommended)

Run this command to copy new files:

```bash
cd "/Users/daniel/Documents/Smart Sports Lab/Football/Sports Data Campus/Cibao/Cibao-fc-analytics"
python3 -c "
from pathlib import Path
import shutil

source_dir = Path('Automation Testing/output/matchstats')
target_dir = Path('data/raw/concacaf/matchstats')
target_dir.mkdir(parents=True, exist_ok=True)

copied = 0
for json_file in source_dir.glob('*.json'):
    shutil.copy2(json_file, target_dir / json_file.name)
    copied += 1

print(f'✅ Copied {copied} files to Streamlit data directory')
"
```

### Option 2: Manual Copy

1. Open Finder
2. Navigate to: `Automation Testing/output/matchstats/`
3. Copy all JSON files
4. Paste into: `data/raw/concacaf/matchstats/`

---

## Clear Streamlit Cache

The Streamlit app uses `@st.cache_data` to cache match data. After copying new files:

### Method 1: Restart Streamlit (Easiest)
- Stop the Streamlit app (Ctrl+C)
- Restart it: `streamlit run app.py`
- Cache is automatically cleared on restart

### Method 2: Clear Cache Button
- In the Streamlit app, go to: **☰ → Settings → Clear cache**
- Click "Clear cache"
- The page will reload with fresh data

### Method 3: Delete Cache Files
```bash
# Delete Streamlit cache directory
rm -rf ~/.streamlit/cache/
```

---

## Verification

After updating, verify the data is loaded:

1. Open the Streamlit app
2. Navigate to "Análisis del Rival - Copa"
3. Check that August matches appear in the opponent dropdown
4. Verify match counts match expected totals (28 matches)

---

## Automation Workflow

For future automation, you can:

1. **Run the scraper**:
   ```bash
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```

2. **Copy to Streamlit directory** (automated):
   ```bash
   # Add this to the scraper script or run separately
   python3 -c "from pathlib import Path; import shutil; [shutil.copy2(f, Path('data/raw/concacaf/matchstats') / f.name) for f in Path('Automation Testing/output/matchstats').glob('*.json')]"
   ```

3. **Restart Streamlit** (or it will pick up new files on next page load if cache expires)

---

## Current Status

- ✅ **Data Directory**: `data/raw/concacaf/matchstats/`
- ✅ **Total Files**: 46 JSON files
- ✅ **August Matches**: 8 files present
- ✅ **All 28 matches**: Available in directory

---

**Last Updated**: November 2025

