# Automation Testing Folder

This folder is for testing automation scripts **without interfering** with production data and scripts.

## 📁 Folder Structure

```
Automation Testing/
├── scripts/              # Test versions of automation scripts
├── output/               # Test outputs (separate from production)
│   ├── matchstats/      # Test match statistics JSON files
│   └── matches/         # Test match data JSON files
├── logs/                 # Test execution logs
└── README.md            # This file
```

## 🧪 Test Scripts

### 1. `get_tournament_id_test.py`
Test version of the competition filtering script.

**Usage:**
```bash
cd "Automation Testing/scripts"
python3 get_tournament_id_test.py "Concacaf Caribbean Cup"
python3 get_tournament_id_test.py --list
```

### 2. `scrape_all_concacaf_matches_test.py`
Test version of the match scraper that saves to test directories.

**Usage:**
```bash
cd "Automation Testing/scripts"
python3 scrape_all_concacaf_matches_test.py
python3 scrape_all_concacaf_matches_test.py --dry-run
python3 scrape_all_concacaf_matches_test.py --competition "Liga Mayor"
```

## 🔒 Safety Features

- ✅ **Separate Output Directory**: All test outputs go to `Automation Testing/output/`
- ✅ **No Production Interference**: Test scripts don't touch production data
- ✅ **Independent Logs**: Test logs are separate from production logs
- ✅ **Easy Cleanup**: Can delete entire `Automation Testing/` folder without affecting production

## 📊 What Gets Tested

1. **Competition Filtering**: Test finding tournament IDs by competition name
2. **Match Discovery**: Test fetching match lists from API
3. **Match Scraping**: Test downloading match data
4. **Data Processing**: Test processing scraped data

## 🧹 Cleanup

To remove all test data:
```bash
rm -rf "Automation Testing/output/*"
```

To remove everything:
```bash
rm -rf "Automation Testing/"
```

## ⚠️ Important Notes

- Test scripts use the **same API credentials** as production (SDAPI Outlet Key)
- Test scripts make **real API calls** to Scoresway
- Test outputs are **separate** from production data
- Production scripts in `src/data_processing/` are **not affected**

## 🚀 Moving to Production

Once testing is complete and verified:
1. Review test outputs in `Automation Testing/output/`
2. If everything looks good, the production scripts are already updated
3. Production scripts will use the same logic but save to production directories

---

**Last Updated**: November 2025

