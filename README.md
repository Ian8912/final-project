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

## Future Updates
- User accounts and login so bookmarks are per-user.
- Compare multiple tickers on the same chart.
- More analysis (compare different stock tickers).
- Cache downloaded data to avoid re-fetching and support offline use.
- Deploy to a hosting service (AWS, Vercel, etc.) instead of running locally.
