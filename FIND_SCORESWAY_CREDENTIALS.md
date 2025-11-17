# How to Find Scoresway/PerformFeeds API Credentials

Since you already have the correct JSON files, they were likely obtained using authenticated API calls. Here's how to find the credentials:

## Method 1: Check Browser DevTools (Network Tab) ⭐ RECOMMENDED

This is the easiest way to find authentication headers:

1. **Open a Scoresway match page** in Chrome:
   - Go to: `https://www.scoresway.com/en_GB/soccer/concacaf-caribbean-cup-2025/bygi47fmsxgbzysjdf9u481lg/match/view/2zhrn3wxg2ma02g2u2j5lotuc`

2. **Open DevTools**:
   - Press `F12` or `Cmd+Option+I` (Mac) / `Ctrl+Shift+I` (Windows)
   - Click the **Network** tab

3. **Clear the network log** (trash icon)

4. **Reload the page** (F5 or Cmd+R)

5. **Look for API requests**:
   - Filter by "XHR" or "Fetch" to see API calls
   - Look for requests to:
     - `api.performfeeds.com`
     - `widgets-api.ngdata.statsperform.com`
     - Any domain with "opta" or "statsperform"

6. **Click on a request** that looks like it returns match data (large response size)

7. **Check the Headers tab**:
   - Look in **Request Headers** for:
     - `Authorization: Bearer ...`
     - `x-api-key: ...`
     - `Cookie: ...`
     - `X-Auth-Token: ...`
     - Any custom headers

8. **Copy the headers**:
   - Right-click the request → "Copy" → "Copy as cURL"
   - Or manually copy the header values

## Method 2: Check Browser Storage

1. **In DevTools**, go to the **Application** tab (Chrome) or **Storage** tab (Firefox)

2. **Check these locations**:
   - **Local Storage** → `https://www.scoresway.com`
   - **Session Storage** → `https://www.scoresway.com`
   - **Cookies** → `https://www.scoresway.com`

3. **Look for**:
   - Keys containing "token", "auth", "api", "key", "credential"
   - Values that look like API keys or tokens

## Method 3: Check Environment Variables

```bash
# Check for environment variables
env | grep -i "api\|token\|auth\|key\|scoresway\|performfeeds\|opta"

# Or check in Python
python3 -c "import os; [print(f'{k}={v}') for k, v in os.environ.items() if any(x in k.upper() for x in ['API', 'TOKEN', 'AUTH', 'KEY', 'SCORESWAY', 'PERFORM', 'OPTA'])]"
```

## Method 4: Check for Config Files

Look for these files in your project:
- `.env` files
- `config.json`
- `credentials.json`
- `secrets.json`
- Any file with "config", "credential", or "secret" in the name

## Method 5: Check if Credentials are in Code

Since you already have working JSON files, check:
- Any Python scripts that downloaded them
- Any browser extensions or tools you used
- Any notes or documentation about how the files were obtained

## What to Look For

When you find credentials, they might be:
- **API Key**: A long string like `auz3487aifIDFI835kadfjadoeaDj38`
- **Bearer Token**: Starts with `Bearer ` followed by a long string
- **Cookie**: Session cookies that authenticate requests
- **Custom Headers**: Headers like `X-API-Key`, `Authorization`, etc.

## Next Steps

Once you find the credentials:
1. Share them with me (or add them to a `.env` file)
2. I'll update the scraper to use them
3. We'll test it to make sure it works

**Important**: Keep credentials secure! Don't commit them to Git.

