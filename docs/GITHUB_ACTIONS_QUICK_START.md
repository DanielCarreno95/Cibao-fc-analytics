# GitHub Actions Quick Start

## 🚀 Get Started in 5 Minutes

### Step 1: Create Workflow File

The workflow file is already created at:
```
.github/workflows/scrape_matches.yml
```

### Step 2: Push to GitHub

```bash
git add .github/workflows/scrape_matches.yml
git commit -m "Add GitHub Actions workflow for match scraping"
git push
```

### Step 3: Enable Permissions

1. Go to: **Repository → Settings → Actions → General**
2. Under **"Workflow permissions"**:
   - Select: **"Read and write permissions"**
   - Check: **"Allow GitHub Actions to create and approve pull requests"**
3. Click **Save**

### Step 4: Test It

1. Go to: **Actions** tab in GitHub
2. Click: **"Scrape Concacaf Matches"** workflow
3. Click: **"Run workflow"** button
4. Select branch: **main** (or your default branch)
5. Click: **"Run workflow"**

### Step 5: Monitor

- Watch the workflow run in real-time
- See logs and progress
- Check if new files were committed

---

## ⚙️ How It Works

**Scheduled:** Runs daily at 2:00 AM UTC automatically

**Manual:** Click "Run workflow" anytime you want

**Result:** New match data is scraped and committed to repository

---

## 🎯 Customize Schedule

Edit `.github/workflows/scrape_matches.yml`:

```yaml
schedule:
  - cron: '0 2 * * *'  # Change this line
```

**Examples:**
- `'0 */6 * * *'` - Every 6 hours
- `'0 22,23,0,1 * * *'` - 10 PM, 11 PM, midnight, 1 AM UTC
- `'0 2 * * 1,3,5'` - Monday, Wednesday, Friday at 2 AM

---

## ✅ That's It!

Your scraping is now automated! 🎉

