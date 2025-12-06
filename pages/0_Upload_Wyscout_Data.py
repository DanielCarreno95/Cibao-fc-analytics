# ===========================================
# SIMPLE WYSCOUT UPLOADER - Clean & Working
# ===========================================
# Flow: Upload Excel → Clean Headers → Convert to Per90 → Save JSON → Done
# ===========================================

import streamlit as st
import pandas as pd
import json
from pathlib import Path
import sys

# Add src to path - try multiple methods for Streamlit Cloud
REPO_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Also add src/data_processing to path for direct imports
src_data_processing = REPO_ROOT / "src" / "data_processing"
if str(src_data_processing) not in sys.path:
    sys.path.insert(0, str(src_data_processing))

# Import required functions with multiple fallbacks for Streamlit Cloud
fix_team_headers = None
convert_df_to_per90 = None

# Try importing fix_team_headers
try:
    from src.data_processing.fix_wyscout_headers import fix_team_headers
except ImportError:
    try:
        from fix_wyscout_headers import fix_team_headers
    except ImportError:
        # Last resort: use importlib to load directly
        try:
            import importlib.util
            fix_path = src_data_processing / "fix_wyscout_headers.py"
            if fix_path.exists():
                spec = importlib.util.spec_from_file_location("fix_wyscout_headers", fix_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    fix_team_headers = module.fix_team_headers
            else:
                raise ImportError(f"File not found: {fix_path}")
        except Exception as e:
            st.error(f"❌ CRITICAL: Could not import fix_team_headers: {e}")
            st.stop()

# Try importing convert_df_to_per90
try:
    from src.data_processing.convert_to_per90_stats import convert_df_to_per90
except ImportError:
    try:
        from convert_to_per90_stats import convert_df_to_per90
    except ImportError:
        # Last resort: use importlib to load directly
        try:
            import importlib.util
            convert_path = src_data_processing / "convert_to_per90_stats.py"
            if convert_path.exists():
                spec = importlib.util.spec_from_file_location("convert_to_per90_stats", convert_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    convert_df_to_per90 = module.convert_df_to_per90
            else:
                raise ImportError(f"File not found: {convert_path}")
        except Exception as e:
            st.error(f"❌ CRITICAL: Could not import convert_df_to_per90: {e}")
            st.stop()

# Try importing theme
try:
    from src.utils.global_dark_theme import inject_dark_theme
except ImportError:
    def inject_dark_theme():
        pass  # No theme if can't import

# Directories
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "Wyscout"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Upload Wyscout Data", page_icon="📊", layout="wide")
inject_dark_theme()

st.title("📊 Upload Wyscout Data")
st.markdown("**Simple flow:** Upload Excel → Clean headers → Convert to per90 → Save JSON")

# Upload files
uploaded_files = st.file_uploader(
    "Select Excel files from Wyscout",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🔄 Process Files", type="primary", use_container_width=True):
        progress_bar = st.progress(0)
        results = {"success": 0, "errors": []}
        
        for idx, uploaded_file in enumerate(uploaded_files):
            try:
                progress_bar.progress((idx + 1) / len(uploaded_files))
                st.write(f"📄 **Processing:** {uploaded_file.name}")
                
                # Step 1: Extract team name from filename
                # Format: "Team Stats Cibao.xlsx" → "Cibao"
                filename = uploaded_file.name
                team_name = filename.replace("Team Stats ", "").replace(".xlsx", "").replace(".xls", "").strip()
                st.write(f"  📋 Team from filename: {team_name}")
                
                # Step 2: Load Excel (handle multiple sheets)
                xls = pd.ExcelFile(uploaded_file)
                
                # Check if it's TeamStats format (single sheet with all teams)
                if "TeamStats" in xls.sheet_names:
                    df = pd.read_excel(xls, sheet_name="TeamStats")
                else:
                    # Multiple sheets - combine them
                    all_sheets = []
                    for sheet_name in xls.sheet_names:
                        df_sheet = pd.read_excel(xls, sheet_name=sheet_name)
                        all_sheets.append(df_sheet)
                    df = pd.concat(all_sheets, ignore_index=True)
                
                # Step 3: Add Team column from filename (if not already present)
                if "Team" not in df.columns:
                    df["Team"] = team_name
                else:
                    # If Team column exists but is empty or has wrong values, use filename
                    if df["Team"].isna().all() or (df["Team"].iloc[0] if len(df) > 0 else None) in ["TeamStats", "Team", ""]:
                        df["Team"] = team_name
                
                # Step 4: Clean headers
                df = fix_team_headers(df)
                st.write("  ✅ Headers cleaned")
                
                # Step 5: Convert to per90 (if Duration exists)
                if "Duration" in df.columns:
                    df = convert_df_to_per90(df)
                    st.write("  ✅ Converted to per90")
                else:
                    st.warning("  ⚠️ No 'Duration' column - skipping per90 conversion")
                
                # Step 6: Save JSON (Team column is now guaranteed to exist from filename)
                # All rows are for the same team (from filename)
                team_df = df.copy()
                
                # Verify it has required columns
                if "Passes" not in team_df.columns or "Shots" not in team_df.columns:
                    st.error(f"  ❌ {team_name}: Missing 'Passes' or 'Shots' columns after processing")
                    results["errors"].append(f"{team_name}: Missing required columns")
                else:
                    # Save JSON
                    team_name_clean = team_name.replace(" ", "_").replace("/", "_").replace("\\", "_")
                    json_path = PROCESSED_DIR / f"{team_name_clean}_per_90.json"
                    
                    with open(json_path, "w", encoding="utf-8") as f:
                        json.dump(team_df.to_dict(orient="records"), f, indent=2, ensure_ascii=False, default=str)
                    
                    st.success(f"  ✅ Saved: `{json_path.name}` ({len(team_df)} rows, {len(team_df.columns)} columns)")
                    results["success"] += 1
                    
            except Exception as e:
                st.error(f"  ❌ Error processing {uploaded_file.name}: {str(e)}")
                results["errors"].append(f"{uploaded_file.name}: {str(e)}")
                import traceback
                with st.expander("Error details", expanded=False):
                    st.code(traceback.format_exc())
        
        progress_bar.empty()
        
        # Summary
        st.markdown("---")
        st.markdown(f"### 📊 Summary")
        st.success(f"✅ **{results['success']} team(s) processed successfully**")
        
        if results["errors"]:
            st.markdown("### ❌ Errors:")
            for error in results["errors"]:
                st.error(f"  - {error}")
        
        # Clear cache and refresh
        st.cache_data.clear()
        st.markdown("---")
        st.success("✅ **Processing complete!** Data is now available on analytics pages.")
        
        if st.button("🔄 Refresh App", type="primary"):
            st.rerun()
