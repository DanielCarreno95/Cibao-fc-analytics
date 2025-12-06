# ===========================================
# SIMPLE WYSCOUT UPLOADER - Clean & Working
# ===========================================
# Flow: Upload Excel → Clean Headers → Convert to Per90 → Save JSON → Done
# ===========================================

import streamlit as st
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import sys

# Add src to path
REPO_ROOT = Path(__file__).parents[1]
sys.path.insert(0, str(REPO_ROOT))

# Import required functions
from src.data_processing.fix_wyscout_headers import fix_team_headers
from src.data_processing.convert_to_per90_stats import convert_df_to_per90

# Directories
PROCESSED_DIR = REPO_ROOT / "data" / "processed" / "Wyscout"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

st.set_page_config(page_title="Upload Wyscout Data", page_icon="📊", layout="wide")

st.title("📊 Upload Wyscout Data")
st.markdown("Upload Excel files → Clean headers → Convert to per90 → Save JSON")

# Upload files
uploaded_files = st.file_uploader(
    "Select Excel files from Wyscout",
    type=["xlsx", "xls"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("🔄 Process Files", type="primary"):
        results = {"success": 0, "errors": []}
        
        for uploaded_file in uploaded_files:
            try:
                st.write(f"📄 Processing: {uploaded_file.name}")
                
                # Step 1: Load Excel
                df = pd.read_excel(uploaded_file)
                
                # Step 2: Clean headers
                df = fix_team_headers(df)
                st.write("✅ Headers cleaned")
                
                # Step 3: Convert to per90 (if Duration exists)
                if "Duration" in df.columns:
                    df = convert_df_to_per90(df)
                    st.write("✅ Converted to per90")
                
                # Step 4: Extract team name and save JSON
                if "Team" in df.columns:
                    # Process each team separately
                    for team in df["Team"].unique():
                        if pd.notna(team):
                            team_df = df[df["Team"] == team].copy()
                            
                            # Verify it has required columns
                            if "Passes" not in team_df.columns or "Shots" not in team_df.columns:
                                st.error(f"❌ {team}: Missing 'Passes' or 'Shots' columns")
                                continue
                            
                            # Save JSON
                            team_name_clean = str(team).replace(" ", "_").replace("/", "_")
                            json_path = PROCESSED_DIR / f"{team_name_clean}_per_90.json"
                            
                            with open(json_path, "w", encoding="utf-8") as f:
                                json.dump(team_df.to_dict(orient="records"), f, indent=2, ensure_ascii=False, default=str)
                            
                            st.success(f"✅ Saved: {json_path.name} ({len(team_df)} rows, {len(team_df.columns)} columns)")
                            results["success"] += 1
                else:
                    st.error(f"❌ {uploaded_file.name}: No 'Team' column found")
                    results["errors"].append(f"{uploaded_file.name}: No 'Team' column")
                    
            except Exception as e:
                st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                results["errors"].append(f"{uploaded_file.name}: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
        
        # Summary
        st.markdown("---")
        st.markdown(f"### ✅ Processed: {results['success']} team(s)")
        if results["errors"]:
            st.markdown("### ❌ Errors:")
            for error in results["errors"]:
                st.error(error)
        
        # Clear cache and refresh
        st.cache_data.clear()
        st.success("✅ Processing complete! Data is now available on analytics pages.")
        st.info("💡 The app will refresh automatically...")
        st.rerun()

