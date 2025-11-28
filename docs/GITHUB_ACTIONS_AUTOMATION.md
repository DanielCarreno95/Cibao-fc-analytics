# GitHub Actions Automation Guide

## Automating Match Data Scraping

This guide explains how to set up GitHub Actions to automatically run your scraping script.

---

## 🎯 What is GitHub Actions?

GitHub Actions is a CI/CD platform that allows you to:
- **Run scripts automatically** on a schedule (cron)
- **Trigger scripts manually** from GitHub UI
- **Run scripts on events** (push, pull request, etc.)
- **Run scripts in the cloud** (no need for your local machine)

---

## 📋 Automation Options

### Option 1: Scheduled Automation (Recommended)
**Run automatically on a schedule** (e.g., daily, after matches)

**Best for:** Regular updates, set-and-forget

**Example:** Run every day at 2 AM, or every 6 hours

---

### Option 2: Manual Trigger
**Run on-demand** from GitHub UI

**Best for:** When you want control over when it runs

**Example:** Click a button in GitHub to run the script

---

### Option 3: Event-Based Trigger
**Run when code is pushed** or other events occur

**Best for:** Development/testing workflows

**Example:** Run when you push new code to main branch

---

## 🚀 Setup Instructions

### Step 1: Create GitHub Actions Workflow File

Create the directory structure:
```bash
mkdir -p .github/workflows
```

Create file: `.github/workflows/scrape_matches.yml`

---

### Step 2: Choose Your Trigger Type

See examples below for each option.

---

## 📝 Workflow Examples

### Example 1: Scheduled (Daily at 2 AM)

```yaml
name: Scrape Concacaf Matches

on:
  schedule:
    # Run daily at 2:00 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:  # Also allow manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install Playwright
      run: |
        pip install playwright
        playwright install chromium
        playwright install-deps
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run scraping script
      run: |
        python3 src/data_processing/scrape_all_concacaf_matches.py
    
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/raw/concacaf/matchstats/
        git diff --staged --quiet || (git commit -m "Auto-update: Scrape new matches [skip ci]" && git push)
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### Example 2: Manual Trigger Only

```yaml
name: Scrape Concacaf Matches (Manual)

on:
  workflow_dispatch:  # Only manual trigger

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install Playwright
      run: |
        pip install playwright
        playwright install chromium
        playwright install-deps
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run scraping script
      run: |
        python3 src/data_processing/scrape_all_concacaf_matches.py
    
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/raw/concacaf/matchstats/
        git diff --staged --quiet || (git commit -m "Manual update: Scrape new matches [skip ci]" && git push)
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

### Example 3: Multiple Times Per Day

```yaml
name: Scrape Concacaf Matches (Frequent)

on:
  schedule:
    # Run every 6 hours
    - cron: '0 */6 * * *'
    # Or run at specific times:
    # - cron: '0 2,8,14,20 * * *'  # 2 AM, 8 AM, 2 PM, 8 PM UTC
  workflow_dispatch:

jobs:
  scrape:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install Playwright
      run: |
        pip install playwright
        playwright install chromium
        playwright install-deps
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run scraping script
      run: |
        python3 src/data_processing/scrape_all_concacaf_matches.py
    
    - name: Commit and push changes
      run: |
        git config --local user.email "action@github.com"
        git config --local user.name "GitHub Action"
        git add data/raw/concacaf/matchstats/
        git diff --staged --quiet || (git commit -m "Auto-update: Scrape new matches [skip ci]" && git push)
      env:
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## ⚙️ Configuration Details

### Cron Schedule Syntax

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
* * * * *
```

**Examples:**
- `0 2 * * *` - Every day at 2:00 AM UTC
- `0 */6 * * *` - Every 6 hours
- `0 2,14 * * *` - At 2:00 AM and 2:00 PM UTC daily
- `0 0 * * 1` - Every Monday at midnight UTC

**Note:** GitHub Actions uses UTC time. Adjust for your timezone.

---

### Playwright Installation

The workflow installs Playwright and Chromium (headless browser) because your scraping script uses it.

**Why needed:** Your script uses Playwright to scrape Scoresway.

---

### Auto-Commit Changes

The workflow automatically:
1. Commits new JSON files to the repository
2. Pushes them to GitHub
3. Uses `[skip ci]` to prevent infinite loops

**Why useful:** Data is automatically saved and versioned in Git.

---

## 🔐 Permissions Setup

### For Auto-Commit to Work:

1. **Go to:** Repository Settings → Actions → General
2. **Under "Workflow permissions":**
   - Select: **"Read and write permissions"**
   - Check: **"Allow GitHub Actions to create and approve pull requests"**

This allows the workflow to commit and push changes.

---

## 🎬 How to Use

### For Scheduled Workflows:

1. **Push the workflow file** to your repository
2. **Workflow runs automatically** on schedule
3. **Check Actions tab** to see runs and logs
4. **Data is automatically committed** to repository

### For Manual Workflows:

1. **Go to:** Actions tab in GitHub
2. **Select workflow:** "Scrape Concacaf Matches"
3. **Click:** "Run workflow" button
4. **Select branch:** (usually `main` or `master`)
5. **Click:** "Run workflow"
6. **Monitor progress** in the Actions tab

---

## 📊 Monitoring Workflows

### View Workflow Runs:

1. Go to **Actions** tab in GitHub
2. Click on workflow name
3. See all runs (successful, failed, in progress)
4. Click on a run to see detailed logs

### Check for Errors:

- Red X = Failed
- Yellow circle = In progress
- Green check = Success

Click on failed runs to see error messages.

---

## 🎯 Recommended Setup for Your Use Case

### For Match Days:

**Option A: Frequent Checks**
```yaml
schedule:
  - cron: '0 */2 * * *'  # Every 2 hours
```

**Option B: After Match Times**
```yaml
schedule:
  - cron: '0 22,23,0,1 * * *'  # 10 PM, 11 PM, midnight, 1 AM UTC
```

**Option C: Manual + Scheduled**
- Use manual trigger for immediate updates after matches
- Use scheduled (daily) for catching up on any missed matches

---

## 🔧 Troubleshooting

### Workflow Fails to Run:

1. **Check Actions tab** for error messages
2. **Verify Python version** matches your local setup
3. **Check Playwright installation** (sometimes needs extra time)
4. **Verify file paths** are correct

### Auto-Commit Not Working:

1. **Check permissions** (see Permissions Setup above)
2. **Verify GITHUB_TOKEN** is available (it's automatic)
3. **Check if files actually changed** (workflow only commits if there are changes)

### Playwright Issues:

If Playwright fails to install:
```yaml
- name: Install Playwright
  run: |
    pip install playwright
    playwright install chromium
    playwright install-deps chromium
  timeout-minutes: 10  # Give it more time
```

---

## 💡 Advanced Options

### Run Only on Weekends:

```yaml
schedule:
  - cron: '0 2 * * 0,6'  # Saturday and Sunday at 2 AM
```

### Run at Specific Times (Match Days):

```yaml
schedule:
  - cron: '0 22 * * 1,3,5'  # Monday, Wednesday, Friday at 10 PM
```

### Add Notifications:

```yaml
- name: Notify on failure
  if: failure()
  uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.create({
        owner: context.repo.owner,
        repo: context.repo.repo,
        title: 'Scraping workflow failed',
        body: 'The match scraping workflow failed. Please check the logs.'
      })
```

---

## 📝 Next Steps

1. **Choose your trigger type** (scheduled, manual, or both)
2. **Create the workflow file** in `.github/workflows/`
3. **Push to GitHub**
4. **Test it** (run manually first)
5. **Monitor** the Actions tab
6. **Adjust schedule** as needed

---

## 🎓 Summary

**GitHub Actions allows you to:**
- ✅ Run scraping automatically on a schedule
- ✅ Trigger manually when needed
- ✅ Run in the cloud (no local machine needed)
- ✅ Auto-commit results to repository
- ✅ Monitor and debug easily

**Best for your use case:**
- **Manual trigger** for immediate updates after matches
- **Daily schedule** to catch any missed matches
- **Both** for maximum coverage

---

**Questions?** Check the GitHub Actions documentation or test with manual triggers first!

