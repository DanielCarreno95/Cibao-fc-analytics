# Wyscout Data Upload Process Flow

## User's Desired Process

1. User logs into app
2. User uploads new Wyscout raw Excel files and presses process button
3. App creates JSON file per team by running:
   - Script to clean Wyscout headers (`fix_wyscout_headers.py`)
   - Script that converts non-standardized metrics to Per 90 (`convert_to_per90_stats.py`)
4. Once this process has finished, each team's charts and data uploads on all of the pages and tabs

## Current Implementation Order

### Step 1: Upload Excel File
- User uploads Excel file(s) via Streamlit file uploader
- Files are saved to `data/raw/wyscout/`

### Step 2: Process Each Sheet/File
For each sheet in the uploaded Excel file:

1. **Read Excel Sheet**
   - Load sheet into pandas DataFrame
   - Extract team names from filename or sheet name

2. **Clean Basic Column Names**
   - Remove extra whitespace, newlines
   - Normalize column names

3. **Apply `fix_wyscout_headers` (Header Cleaning)**
   - Check if OLD format columns exist (e.g., `"Passes / accurate"`)
   - If OLD format detected:
     - Apply `fix_team_headers()` or `fix_player_headers()`
     - Split merged columns:
       - `"Passes / accurate"` → `"Passes"`, `"Passes Accurate"`, `"Passes Accurate %"`
       - `"Shots / on target"` → `"Shots"`, `"Shots On Target"`, `"Shots On Target %"`
   - Verify fix worked (check for NEW format columns)
   - Add success/warning message to results

4. **Apply `convert_to_per90_stats` (Per 90 Conversion)**
   - Check if `"Duration"` column exists
   - If available:
     - Apply `convert_df_to_per90()` to convert metrics to per 90 minutes
     - Verify conversion worked (check for "Per 90" columns)
     - Add success/warning message to results

5. **Clean Data**
   - Remove rows with missing Team names
   - Convert Date column to datetime
   - Derive `is_home` from Match string if needed

### Step 3: Create JSON Files

#### For Multi-Team Files (TeamStats sheet):
- Group data by Team column
- For each team:
  - Create individual JSON file: `{team_name}_per_90.json`
  - Save to `data/processed/Wyscout/`
  - Add to `results["files_created"]`

#### For Single-Team Files (one sheet per team):
- Create individual JSON file: `{team_name}_per_90.json`
- Save to `data/processed/Wyscout/`
- Add to `results["files_created"]`

#### Consolidated File:
- Combine all processed data into one DataFrame
- Create consolidated JSON file: `Liga_Mayor_Clean_Per_90_Consolidated.json`
- Save to `data/processed/Wyscout/`
- Add to `results["files_created"]`

### Step 4: Clear Cache and Refresh
- Call `st.cache_data.clear()` to invalidate all cached data
- Store processing results in `st.session_state.processing_results`
- Call `st.rerun()` to refresh the app

### Step 5: Display Results
- After rerun, display processing summary:
  - Success message
  - Number of teams processed
  - Files created
  - Warnings (header cleaning, per90 conversion)
  - Errors (if any)

## Key Points

✅ **Headers are cleaned BEFORE per90 conversion**
✅ **Per90 conversion happens BEFORE JSON creation**
✅ **Individual JSON files are created per team**
✅ **Consolidated JSON file is also created**
✅ **Cache is cleared and app refreshes automatically**
✅ **All data uses NEW format (after fix_wyscout_headers)**

## File Locations

- **Raw files:** `data/raw/wyscout/Teams/` or `data/raw/wyscout/Global/`
- **Processed JSON files:** `data/processed/Wyscout/`
  - Individual: `{Team_Name}_per_90.json`
  - Consolidated: `Liga_Mayor_Clean_Per_90_Consolidated.json`

## Verification

After processing, check:
1. Individual JSON files exist for each team
2. Consolidated JSON file exists
3. JSON files have NEW format columns (`"Passes"`, `"Shots"`, not `"Passes / accurate"`)
4. JSON files have Per 90 columns where applicable
5. Charts on all pages update with new data

