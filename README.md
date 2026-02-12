# Wine Cellar Data Collection Script

This script automates the process of logging into manageyourcellar.com and collecting all wine data from various pages.

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

## Usage

Run the script:
```bash
python scrape_wine_cellar.py
```

The script will:
1. Launch a browser window
2. Log in with the provided credentials (bread/butter)
3. Navigate through all the pages you specified
4. Take full-page screenshots of each page
5. Extract all table data (wine entries with all columns)
6. Extract color schemes and layout information
7. Save everything to a JSON file

## Output

The script generates:
- **Screenshots**: `screenshot_XX_pagename_TIMESTAMP.png` for each page
- **JSON Data**: `wine_cellar_data_TIMESTAMP.json` containing all extracted data

## What's Collected

For each page:
- URL and page title
- All table column headers
- All wine entries with complete data
- Sidebar navigation links
- Color scheme (header, sidebar, table headers, body, footer)
- Filter/search options available

## Pages Visited

1. Home/Dashboard after login
2. Wines in Cellar (first 20 wines with all columns)
3. Ready to Drink
4. Wines on Order
5. Wines Consumed (all entries)
6. Wish List

## Notes

- The browser runs in non-headless mode so you can see what's happening
- Change `headless=False` to `headless=True` in the script for background operation
- The script waits 5 seconds at the end before closing the browser
