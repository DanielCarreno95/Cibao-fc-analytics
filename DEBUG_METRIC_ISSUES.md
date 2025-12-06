# Debug Guide: Missing Metrics (totalPass, Passes, Shots, etc.)

## Problem
The app is showing `NOT FOUND` for:
- `totalPass`
- `Passes`
- `Passes Accurate`
- `totalScoringAtt`
- `Shots`

But it IS finding:
- `accuratePass: 298.6` (from `'Passes / accurate'`)
- `'Passes / accurate': 298.6`
- `'Shots / on target': 12.4`

## Root Cause
The data still has **OLD FORMAT** columns (before `fix_wyscout_headers` was applied):
- `'Passes / accurate'` instead of `'Passes'` + `'Passes Accurate'`
- `'Shots / on target'` instead of `'Shots'` + `'Shots On Target'`

The `fix_wyscout_headers` function should split these, but the JSON files were created BEFORE the fix was applied.

## Files to Check Manually

### 1. Check the Consolidated JSON File
**Location:** `data/processed/Wyscout/Liga_Mayor_Clean_Per_90_Consolidated.json`

**What to check:**
- Open the file and look at the first record
- Check if it has:
  - ❌ OLD FORMAT: `"Passes / accurate": 298.6` (single column)
  - ✅ NEW FORMAT: `"Passes": 350.0` and `"Passes Accurate": 298.6` (separate columns)

**If you see OLD FORMAT:**
- The JSON file needs to be regenerated
- Delete the JSON file and re-upload your Excel files

### 2. Check the Excel Files (Source Data)
**Location:** `data/raw/wyscout/Teams/` or wherever you upload from

**What to check:**
- Open one of the Excel files (e.g., `Team Stats Delfines Del Este.xlsx`)
- Look at the column headers
- Check if you see:
  - ❌ OLD FORMAT: Column named `"Passes / accurate"` (with a slash)
  - ✅ NEW FORMAT: Separate columns `"Passes"` and `"Passes Accurate"`

**If Excel has OLD FORMAT:**
- The `fix_wyscout_headers` function should fix this during upload
- But if the JSON was created before, it won't help

### 3. Check if fix_wyscout_headers is Being Applied
**Location:** Upload page (`pages/0_Upload_Wyscout_Data.py`)

**What to check:**
- When you upload files, look for messages like:
  - ✅ `"Headers limpiados para hoja 'TeamStats'"`
  - ✅ `"Métricas convertidas a per 90"`

**If you don't see these messages:**
- The `fix_wyscout_headers` might not be running
- Check the upload page logs/errors

## Solution Steps

### Step 1: Delete Old JSON Files
1. Go to Upload page
2. Click "🗑️ Eliminar Archivos JSON Antiguos"
3. This deletes all JSON files in `data/processed/Wyscout/`

### Step 2: Re-upload Excel Files
1. Upload your Excel files again
2. Make sure you see success messages about header cleaning
3. The app will regenerate JSON files with NEW FORMAT columns

### Step 3: Verify the Fix
1. Go to "Análisis del Rival — Liga Mayor" page
2. Select a team
3. Go to "Comparison" tab
4. Expand "🔍 DEBUG: Data Flow Check"
5. Check if you now see:
   - ✅ `totalPass: [number]` (not "NOT FOUND")
   - ✅ `Passes: [number]` (not "NOT FOUND")
   - ✅ `Shots: [number]` (not "NOT FOUND")

## Quick Python Check Script

You can also run this in Python to check the JSON file:

```python
import json
import pandas as pd

# Load the consolidated JSON
with open('data/processed/Wyscout/Liga_Mayor_Clean_Per_90_Consolidated.json', 'r') as f:
    data = json.load(f)

# Convert to DataFrame
df = pd.DataFrame(data)

# Check columns
print("Columns in JSON file:")
print(df.columns.tolist())

# Check for OLD vs NEW format
has_old_format = 'Passes / accurate' in df.columns
has_new_format = 'Passes' in df.columns and 'Passes Accurate' in df.columns

print(f"\nHas OLD format ('Passes / accurate'): {has_old_format}")
print(f"Has NEW format ('Passes' + 'Passes Accurate'): {has_new_format}")

if has_old_format and not has_new_format:
    print("\n❌ PROBLEM: JSON has OLD format. Need to regenerate!")
    print("Solution: Delete JSON files and re-upload Excel files")
elif has_new_format:
    print("\n✅ GOOD: JSON has NEW format")
```

## Expected Column Names (NEW FORMAT)

After `fix_wyscout_headers` is applied, you should see:
- `Passes` (total passes)
- `Passes Accurate` (accurate passes count)
- `Passes Accurate %` (pass accuracy percentage)
- `Shots` (total shots)
- `Shots On Target` (shots on target count)
- `Shots On Target %` (shot accuracy percentage)

## Expected Column Names (OLD FORMAT - PROBLEM)

If you see these, the JSON needs to be regenerated:
- `Passes / accurate` (merged column - can't get total passes from this)
- `Shots / on target` (merged column - can't get total shots from this)

