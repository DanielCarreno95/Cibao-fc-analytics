# 📊 How to Update Match Data in Streamlit

## Quick Guide for Coaching Staff

---

## 🎯 The Process (3 Simple Steps)

### Step 1: Run the Scraping Script
```bash
python3 src/data_processing/scrape_all_concacaf_matches.py
```
**What it does:** Downloads new match data and saves it to the database

**Time:** ~2-5 minutes (depending on number of new matches)

---

### Step 2: Update Streamlit (Choose One Option)

#### **Option A: Automatic (Recommended)**
- ⏰ **Wait 5 minutes**
- ✅ Data updates automatically
- 🎯 **Best for:** When you're not in a hurry

#### **Option B: Manual (Immediate)**
- 🔄 **Click the "Update Data" button** (below the page title)
- ✅ Data updates immediately
- 🎯 **Best for:** When you need data right away

---

### Step 3: View Updated Data
- ✅ New matches appear in the app
- ✅ All statistics are updated
- ✅ Ready to analyze!

---

## 📍 Where to Find the Update Button

**Location:** On the "Análisis del Rival - Copa" page

**Look for:** Orange button labeled **"🔄 Actualizar Datos"**

**Position:** Directly below the page title

---

## ⚡ Quick Reference

| Action | Time | When to Use |
|-------|------|-------------|
| **Automatic Update** | 5 minutes | Normal workflow, not urgent |
| **Manual Update** | Immediate | Just ran scraping, need data now |

---

## ❓ Common Questions

**Q: Do I need to restart Streamlit?**  
A: **No!** Just wait 5 minutes or click the update button.

**Q: How do I know if data is updated?**  
A: Check the match list - new matches will appear. Or click the update button to force refresh.

**Q: What if the button doesn't work?**  
A: Try clicking it again. If it still doesn't work, restart Streamlit as a last resort.

**Q: How often should I run the scraping script?**  
A: After each match or whenever you need the latest data.

---

## 🎬 Example Workflow

**After a match finishes:**

1. ✅ Run: `python3 src/data_processing/scrape_all_concacaf_matches.py`
2. ✅ Wait for script to complete (~2-5 minutes)
3. ✅ Go to Streamlit app
4. ✅ Click "🔄 Actualizar Datos" button (or wait 5 minutes)
5. ✅ New match data appears!

**Total time:** ~5-10 minutes from match finish to updated data

---

## 💡 Pro Tips

- **Run scraping during halftime** if you want data ready right after the match
- **Use automatic update** if you're doing other work - it will refresh on its own
- **Use manual update** when you're actively analyzing and need data immediately
- **Check the sidebar** for information about the selected team and upcoming matches

---

## 📞 Need Help?

If something doesn't work:
1. Check that the scraping script completed successfully
2. Verify files are in: `data/raw/concacaf/matchstats/`
3. Try clicking the update button again
4. As last resort: Restart Streamlit

---

**Last Updated:** January 2025  
**Version:** 1.0

