# Stonker

## Authors: Ian Lingo

### Project Description
Stonker is a stock analyzer web application. Users enter a stock ticker,
choose a time range, and Stonker fetches the recent price history from the internet,
computes summary statistics, and displays a price chart. Tickers can be bookmarked
for quick re-analysis.

## How It Works

| Requirement | Where it lives |
|-------------|----------------|
| **Interface** (Flask, 2 pages, 4+ widgets) | `app.py` routes + `templates/` (search box, range dropdown, Analyze button, Bookmark button, bookmark links) |
| **Access web data** | `fetch_stock()` - pulls daily prices from the free Yahoo Finance chart API (no API key needed) |
| **Data organization** | `save_csv()` writes one CSV per ticker in `data/`; bookmarks stored in `data/bookmarks.json` |
| **Data analysis** | `analyze()` - uses NumPy for start/end/min/max/mean, percent change, and volatility |
| **Visualization** | `make_plot()` - Matplotlib time-series plot with a 10-day moving average |

The two pages are the **home/search page** (`index.html`) and the **analysis dashboard**
(`result.html`).

All accessible in github: https://github.com/Ian8912

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python app.py
```

Then open http://127.0.0.1:5000 in your browser. Enter a ticker (e.g. `AAPL`),
pick a range, and click **Analyze**.

## Reading the Chart

The dashboard shows two lines:

- **Close** (blue) - the stock's actual closing price for each day.
- **10-day average** (orange) - a *moving average*. Each point is the average of
  that day's closing price plus the previous 9 days. It smooths out the daily
  ups and downs so the overall trend is easier to see. When the orange line
  slopes up the stock has been trending up; when it slopes down it has been
  trending down.

Because the average needs 10 days of data before it can start, the orange line
begins about 9 days after the blue line and is a little shorter - this is normal.
On the **30-day** range there are fewer days, so the average smooths less and the
line is short; it looks best on the **90-day** and **1-year** ranges.

### The statistics table
- **Start / End** - price on the first and last day of the range.
- **Min / Max** - the lowest and highest closing price in the range.
- **Mean** - the average closing price.
- **Change** - percent gained or lost from start to end.
- **Volatility** - how much the price bounces day to day (higher = riskier/choppier).

## Understanding the Data

- Data comes from the free Yahoo Finance API and includes only **trading days**
  (weekends and holidays are skipped), so "Last 30 days" means 30 trading days -
  roughly 6 calendar weeks.
- A full year of daily prices is downloaded and saved locally as a CSV in `data/` (not shown remotely since .gitignore), then the chosen range is sliced from it for analysis.
- If a ticker can't be found, the app shows a "No data found" message instead of
  crashing.

## Future Updates
- User accounts and login so bookmarks are per-user.
- Compare multiple tickers on the same chart.
- More analysis (compare different stock tickers).
- Cache downloaded data to avoid re-fetching and support offline use.
- Deploy to a hosting service (AWS, Vercel, etc.) instead of running locally.
