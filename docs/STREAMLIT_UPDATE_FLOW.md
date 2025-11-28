# How Streamlit Gets Updated After API Calls

## 📊 Complete Data Flow

### Step 1: API Call Saves Files to Disk

**Script**: `scrape_all_concacaf_matches.py`

1. **Makes API call** to get match list:
   ```
   GET api.performfeeds.com/soccerdata/match/{KEY}/?_rt=c&tmcl={ID}&_pgSz=400
   → Returns: List of 28 matches (IDs, dates, descriptions)
   ```

2. **For each match**, calls `scrape_match(match_id)`:
   ```
   GET api.performfeeds.com/soccerdata/matchstats/{KEY}/{match_id}
   → Returns: Full match JSON (stats, events, lineups, etc.)
   ```

3. **Saves JSON file to disk**:
   ```python
   # In scrape_scoresway_match.py, line ~572
   output_path = output_dir / filename  # e.g., "20250820_Cibao_vs_Cavalier.json"
   with open(output_path, 'w', encoding='utf-8') as f:
       json.dump(match_data, f, ensure_ascii=False, indent=2)
   ```
   
   **Location**: `data/raw/concacaf/matchstats/20250820_Cibao_vs_Cavalier.json`

---

### Step 2: Streamlit Reads Files from Disk

**File**: `pages/5_Analisis_del_Rival_-_Copa.py`

**Function**: `load_all_matches()` (line 387-403)

```python
@st.cache_data  # ← This caches the result!
def load_all_matches() -> List[Dict]:
    """Carga todos los partidos desde los archivos JSON."""
    matches = []
    
    # Cargar desde matchstats
    if MATCHSTATS_DIR.exists():
        for json_file in MATCHSTATS_DIR.glob("*.json"):  # ← Reads ALL .json files
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    matches.append(data)
            except Exception as e:
                st.warning(f"⚠️ Error cargando {json_file.name}: {e}")
                continue
    
    return matches
```

**What happens:**
- Streamlit calls `load_all_matches()` when the page loads
- Function reads **all** `.json` files from `data/raw/concacaf/matchstats/`
- Returns a list of all match dictionaries
- **First time**: Reads files, caches result
- **Subsequent times**: Returns cached result (doesn't re-read files)

---

### Step 3: The Caching Mechanism

**Key Point**: `@st.cache_data` decorator

```python
@st.cache_data  # No TTL = cache never expires automatically
def load_all_matches() -> List[Dict]:
    # ...
```

**How caching works:**
1. **First call**: Function executes, reads all files, caches result in memory
2. **Subsequent calls**: Returns cached result (FAST! No file I/O)
3. **Cache persists** until:
   - Streamlit app restarts (automatic clear)
   - Manual cache clear (Settings → Clear cache)
   - TTL expires (if `@st.cache_data(ttl=3600)` was used)

---

## ⚠️ Important: It's NOT Fully Automatic!

### Current Behavior:
- ✅ **Files are saved immediately** when API call completes
- ✅ **Files are on disk** and ready to be read
- ❌ **Streamlit cache needs to be cleared** to see new files
- ❌ **Cache doesn't automatically detect new files**

### Why?
Streamlit's `@st.cache_data` caches the **function result**, not the files. It doesn't monitor the file system for changes. The cache is based on:
- Function name
- Function arguments (none in this case)
- Function code (if it changes, cache invalidates)

**It does NOT check:**
- File modification times
- New files added to directory
- Files deleted from directory

---

## 🔄 How to Update Streamlit After API Call

### Option 1: Restart Streamlit (Easiest)
```bash
# Stop the app (Ctrl+C)
# Restart
streamlit run app.py
```
- Cache is automatically cleared on restart
- Function runs fresh, reads all files including new ones

### Option 2: Clear Cache in App
- Click: **☰ → Settings → Clear cache**
- Function runs again, reads all files

### Option 3: Set TTL (Time-To-Live)
```python
@st.cache_data(ttl=3600)  # Cache expires after 1 hour
def load_all_matches() -> List[Dict]:
    # ...
```
- Cache automatically expires after 1 hour
- Function re-runs, picks up new files
- **Trade-off**: Slower (re-reads files every hour)

---

## 🚀 Making It More Automatic

### Option A: Add File Monitoring (Advanced)
Could use file watchers to detect new files and clear cache automatically, but this is complex.

### Option B: Use TTL (Simple)
Set a TTL so cache expires periodically:
```python
@st.cache_data(ttl=300)  # 5 minutes
def load_all_matches() -> List[Dict]:
    # ...
```

### Option C: Manual Refresh Button
Add a button in Streamlit to manually clear cache:
```python
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()
    st.rerun()
```

### Option D: Integrate Scraper into Streamlit
Run the scraper from within Streamlit, then automatically clear cache:
```python
if st.button("🔄 Update Match Data"):
    # Run scraper
    asyncio.run(scrape_new_matches())
    # Clear cache
    st.cache_data.clear()
    st.rerun()
```

---

## 📋 Current Workflow

1. **Run scraper** (separate terminal/script):
   ```bash
   python3 src/data_processing/scrape_all_concacaf_matches.py
   ```
   → Saves files to `data/raw/concacaf/matchstats/`

2. **Restart Streamlit** OR **Clear cache**:
   → Streamlit re-reads all files, including new ones

3. **New data appears** in the app!

---

## 💡 Summary

**The Connection:**
- API call → Saves JSON files to disk ✅
- Streamlit → Reads JSON files from disk ✅
- **The gap**: Streamlit cache doesn't auto-detect new files ⚠️

**Solution:**
- Restart Streamlit (clears cache automatically)
- OR Clear cache manually (Settings → Clear cache)
- OR Set TTL for automatic expiration

**It's file-based, not database-based:**
- No database connection needed
- Files are the "source of truth"
- Streamlit reads files directly
- Cache just speeds up repeated reads

