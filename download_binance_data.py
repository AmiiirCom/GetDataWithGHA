#!/usr/bin/env python
# coding: utf-8

import os
import sys
import time
import pandas as pd
import dateparser
from binance import Client

# ======================== تنظیمات ========================
SYMBOLS = ["BTCUSDT"]                         # لیست نمادها
INTERVALS = ["15m", "1h"]                     # تایم فریم‌های مورد نیاز (در قالب رشته)
START_DATE_STR = "2017-01-01 00:00:00"        # تاریخ شروع
LIMIT_PER_REQUEST = 1000                      # حداکثر کندل در هر درخواست (محدودیت بایننس)

# کلیدهای API (اختیاری، از محیط‌گیر بخوانید)
API_KEY = os.environ.get("BINANCE_API_KEY")
API_SECRET = os.environ.get("BINANCE_API_SECRET")

# ========== ایجاد پوشه ذخیره داده ==========
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)    # اگر اسکریپت در پوشه scripts/ باشد
RAW_DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
os.makedirs(RAW_DATA_DIR, exist_ok=True)

# ========== توابع کمکی ==========
def interval_to_milliseconds(interval: str) -> int:
    """تبدیل رشته تایم فریم به میلی‌ثانیه."""
    ms = {
        "1m": 60 * 1000,
        "3m": 3 * 60 * 1000,
        "5m": 5 * 60 * 1000,
        "15m": 15 * 60 * 1000,
        "30m": 30 * 60 * 1000,
        "1h": 60 * 60 * 1000,
        "2h": 2 * 60 * 60 * 1000,
        "4h": 4 * 60 * 60 * 1000,
        "6h": 6 * 60 * 60 * 1000,
        "8h": 8 * 60 * 60 * 1000,
        "12h": 12 * 60 * 60 * 1000,
        "1d": 24 * 60 * 60 * 1000,
        "3d": 3 * 24 * 60 * 60 * 1000,
        "1w": 7 * 24 * 60 * 60 * 1000,
        "1M": 30 * 24 * 60 * 60 * 1000,
    }
    return ms.get(interval, 60 * 1000)

def get_start_timestamp(client, symbol, interval, start_str):
    """پیدا کردن اولین تایم‌استمپ کندل بعد از start_str."""
    try:
        parsed = dateparser.parse(start_str)
        if not parsed:
            print(f"❌ {symbol} - Could not parse start date '{start_str}'")
            return None
        start_ms = int(parsed.timestamp() * 1000)
        first = client.get_klines(symbol=symbol, interval=interval, startTime=start_ms, limit=1)
        if first:
            actual = first[0][0]
            print(f"{symbol} ({interval}) - Start timestamp: {actual}")
            return actual
        else:
            print(f"{symbol} ({interval}) - No data from start date")
            return None
    except Exception as e:
        print(f"{symbol} ({interval}) - Error getting start timestamp: {e}")
        return None

def estimate_total_requests(client, symbol, interval, start_timestamp, limit_per_req):
    """تخمین تعداد درخواست‌های لازم برای دانلود کل داده."""
    try:
        last = client.get_klines(symbol=symbol, interval=interval, limit=1)
        if not last:
            return 100
        end_ms = last[0][0]
        duration_ms = end_ms - start_timestamp
        interval_ms = interval_to_milliseconds(interval)
        if duration_ms <= 0:
            return 1
        total_candles = duration_ms // interval_ms
        requests = (total_candles // limit_per_req) + 1
        return max(1, requests)
    except Exception as e:
        print(f"{symbol} ({interval}) - Estimation error: {e}")
        return 100

def fetch_and_save(client, symbol, interval, start_str, output_path, limit_per_req=1000):
    """دریافت و ذخیره داده‌ها با نمایش پیشرفت ساده (مناسب GitHub Actions)."""
    start_ts = get_start_timestamp(client, symbol, interval, start_str)
    if start_ts is None:
        return

    all_klines = []
    current_start = start_ts
    total_req_est = estimate_total_requests(client, symbol, interval, start_ts, limit_per_req)

    # تخمین تعداد کل کندل‌ها
    interval_ms = interval_to_milliseconds(interval)
    try:
        last_kline = client.get_klines(symbol=symbol, interval=interval, limit=1)
        end_ts = last_kline[0][0] if last_kline else int(time.time() * 1000)
        total_candles_est = (end_ts - start_ts) // interval_ms
    except:
        total_candles_est = total_req_est * limit_per_req

    print(f"\n📊 {symbol} ({interval}) - حدود {total_req_est} درخواست, حدود {total_candles_est} کندل")

    req_count = 0
    processed = 0

    try:
        while True:
            klines = client.get_klines(
                symbol=symbol,
                interval=interval,
                startTime=current_start,
                limit=limit_per_req
            )
            if not klines:
                break

            all_klines.extend(klines)
            processed += len(klines)
            req_count += 1

            percent = min(100, int(processed / total_candles_est * 100)) if total_candles_est else 0
            print(f"   [{symbol} {interval}] درخواست {req_count}/{total_req_est} | کندل‌ها: {processed} ({percent}%)")

            if len(klines) < limit_per_req:
                break
            else:
                last_open = klines[-1][0]
                current_start = last_open + interval_ms

            if current_start > int(time.time() * 1000):
                break

        if not all_klines:
            print(f"⚠️ {symbol} ({interval}) - داده‌ای دریافت نشد")
            return

        # تبدیل به DataFrame و ذخیره
        original_cols = [
            'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Close Time', 'Quote Asset Volume', 'Number of Trades',
            'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume', 'Ignore'
        ]
        keep_cols = [
            'timestamp', 'Open', 'High', 'Low', 'Close', 'Volume',
            'Quote Asset Volume', 'Number of Trades',
            'Taker Buy Base Asset Volume', 'Taker Buy Quote Asset Volume'
        ]
        df = pd.DataFrame(all_klines, columns=original_cols)
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df[keep_cols]
        df.to_csv(output_path, index=False)
        print(f"✅ {symbol} ({interval}) ذخیره شد در: {output_path}")
        print(f"   تعداد رکوردها: {len(df)}")

    except Exception as e:
        print(f"❌ {symbol} ({interval}) خطا: {e}")

# ======================== اجرای اصلی ========================
def main():
    # ساخت کلاینت بیننس (در صورت نبود API key بدون احراز هویت کار می‌کند)
    client = Client(API_KEY, API_SECRET) if API_KEY and API_SECRET else Client()

    print("🚀 شروع دانلود داده‌های تاریخی از بایننس")
    print(f"📁 ذخیره در: {RAW_DATA_DIR}")

    for symbol in SYMBOLS:
        for interval in INTERVALS:
            # نام فایل: نماد_تایم فریم_زمان یونیکس.csv
            filename = f"{symbol}_{interval}_{int(time.time())}.csv"
            filepath = os.path.join(RAW_DATA_DIR, filename)
            fetch_and_save(client, symbol, interval, START_DATE_STR, filepath, LIMIT_PER_REQUEST)
            time.sleep(1)   # احترام به محدودیت نرخ

    print("\n🎉 کلیه داده‌ها با موفقیت دانلود شدند.")

if __name__ == "__main__":
    main()