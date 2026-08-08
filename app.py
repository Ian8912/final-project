"""Stonks - a Flask stock analyzer.

- web data access (fetch_stock) + data organization (save_csv, bookmarks).
- analysis (analyze) + visualization (make_plot).
"""
import csv
import json
import os
from datetime import datetime

import matplotlib

matplotlib.use("Agg") # headless backend to save plots to file
import matplotlib.pyplot as plt
import numpy as np
import requests
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# No path issues with different Operating Systems
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PLOT_DIR = os.path.join(os.path.dirname(__file__), "static", "plots")
BOOKMARKS = os.path.join(DATA_DIR, "bookmarks.json")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PLOT_DIR, exist_ok=True)


# Access Web Data
def fetch_stock(ticker):
    """One year of daily prices from Yahoo Finance for free with no API key needed."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker.upper()}"
    resp = requests.get(url, params={"range": "1y", "interval": "1d"},
                        headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    if resp.status_code != 200: # not OK
        return None  # unknown ticker returns a 404
    result = resp.json()["chart"]["result"]
    if not result:
        return None
    result = result[0]
    stamps = result["timestamp"]
    closes = result["indicators"]["quote"][0]["close"]
    # Build simple date/close rows, skipping any gaps returned by the API.
    rows = [
        {"Date": datetime.utcfromtimestamp(t).strftime("%Y-%m-%d"),
         "Close": c}
        for t, c in zip(stamps, closes) if c is not None
    ]
    return rows or None


# Data Organization
def save_csv(ticker, rows):
    """Store each ticker's data as its own CSV file locally. Within .gitignore."""
    path = os.path.join(DATA_DIR, f"{ticker.upper()}.csv")
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    return path


def load_bookmarks():
    if os.path.exists(BOOKMARKS):
        with open(BOOKMARKS) as f:
            return json.load(f)
    return []


def save_bookmarks(marks):
    with open(BOOKMARKS, "w") as f:
        json.dump(marks, f)


def add_bookmark(ticker, days):
    """Save the ticker together with the day range the user was viewing."""
    marks = load_bookmarks()
    entry = {"ticker": ticker.upper(), "days": int(days)}
    if entry not in marks:  # same ticker at a different range is its own bookmark
        marks.append(entry)
        save_bookmarks(marks)


def remove_bookmark(ticker, days):
    """Delete the bookmark matching this ticker and day range."""
    entry = {"ticker": ticker.upper(), "days": int(days)}
    marks = [m for m in load_bookmarks() if m != entry]
    save_bookmarks(marks)


# Data Analysis
def analyze(rows, days):
    """Compute summary statistics on the most recent `days` closing prices."""
    closes = np.array([float(r["Close"]) for r in rows[-days:]])
    dates = [r["Date"] for r in rows[-days:]]
    daily_returns = np.diff(closes) / closes[:-1]
    stats = {
        "start": round(float(closes[0]), 2),
        "end": round(float(closes[-1]), 2),
        "min": round(float(closes.min()), 2),
        "max": round(float(closes.max()), 2),
        "mean": round(float(closes.mean()), 2),
        "pct_change": round(float((closes[-1] - closes[0]) / closes[0] * 100), 2),
        "volatility": round(float(daily_returns.std() * 100), 2),
    }
    return closes, dates, stats


# Visualization
def make_plot(ticker, closes, dates):
    """Plot the closing price time series with a 10-day moving average."""
    sma = np.convolve(closes, np.ones(10) / 10, mode="valid")
    plt.figure(figsize=(9, 4))
    plt.plot(range(len(closes)), closes, label="Close")
    plt.plot(range(9, len(closes)), sma, label="10-day avg", color="orange")
    plt.title(f"{ticker.upper()} closing price")
    plt.xlabel(f"{dates[0]}  to  {dates[-1]}")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, f"{ticker.upper()}.png")
    plt.savefig(path)
    plt.close()
    return f"plots/{ticker.upper()}.png"


# Routes / interface
@app.route("/")
def index():
    return render_template("index.html", bookmarks=load_bookmarks())


@app.route("/analyze", methods=["GET", "POST"])
def analyze_view():
    ticker = (request.values.get("ticker") or "").strip()
    days = int(request.values.get("days") or 90)
    if not ticker:
        return redirect(url_for("index"))
    rows = fetch_stock(ticker)
    if not rows:
        return render_template("index.html", bookmarks=load_bookmarks(),
                               error=f"No data found for '{ticker}'.")
    save_csv(ticker, rows)
    closes, dates, stats = analyze(rows, days)
    plot = make_plot(ticker, closes, dates)
    return render_template("result.html", ticker=ticker.upper(), days=days,
                           stats=stats, plot=plot)


@app.route("/bookmark", methods=["POST"])
def bookmark():
    ticker = request.form.get("ticker", "")
    days = request.form.get("days", 90)
    if ticker:
        add_bookmark(ticker, days)
    return redirect(url_for("index"))


@app.route("/remove", methods=["POST"])
def remove():
    ticker = request.form.get("ticker", "")
    days = request.form.get("days", 90)
    if ticker:
        remove_bookmark(ticker, days)
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
