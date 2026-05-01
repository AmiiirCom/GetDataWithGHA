#!/usr/bin/env python
# coding: utf-8

import os
from binance_historical_data import BinanceDataDumper
from datetime import date

def setup_and_download():
    # پوشه ذخیره‌سازی داده‌ها
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data", "raw")
    os.makedirs(data_dir, exist_ok=True)

    # ----- تایم فریم 1 ساعته -----
    print("🚀 شروع دانلود داده‌های 1 ساعته BTCUSDT (از 2017 تا امروز)...")
    dumper_h1 = BinanceDataDumper(
        path_dir_where_to_dump=data_dir,
        asset_class="spot",
        data_type="klines",
        data_frequency="1h"
    )
    dumper_h1.dump_data(
        tickers=["BTCUSDT"],
        date_start=date(2017, 1, 1),
        date_end=date.today(),
        is_to_update_existing=False
    )

    # ----- تایم فریم 15 دقیقه -----
    print("\n🚀 شروع دانلود داده‌های 15 دقیقه‌ای BTCUSDT (از 2017 تا امروز)...")
    dumper_15m = BinanceDataDumper(
        path_dir_where_to_dump=data_dir,
        asset_class="spot",
        data_type="klines",
        data_frequency="15m"
    )
    dumper_15m.dump_data(
        tickers=["BTCUSDT"],
        date_start=date(2017, 1, 1),
        date_end=date.today(),
        is_to_update_existing=False
    )

    print("\n✅ دانلود همه داده‌ها با موفقیت انجام شد.")
    # نمایش مسیر فایل‌های ذخیره شده
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                print(f"   📄 {os.path.join(root, file)}")

if __name__ == "__main__":
    setup_and_download()