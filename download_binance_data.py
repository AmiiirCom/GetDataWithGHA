#!/usr/bin/env python
# coding: utf-8

import os
import shutil
import zipfile
import subprocess
from binance_historical_data import BinanceDataDumper
from datetime import date
import glob

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data_raw")
    
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    print("🚀 دانلود داده‌های 1 ساعته...")
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

    print("🚀 دانلود داده‌های 15 دقیقه‌ای...")
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

    print("✅ دانلود شد. در حال فشرده‌سازی...")
    
    # ساخت ZIP کامل
    full_zip = "binance_full.zip"
    with zipfile.ZipFile(full_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(data_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, start=data_dir)
                zipf.write(file_path, arcname=arcname)
    
    # حذف پوشه داده خام
    shutil.rmtree(data_dir)
    
    # تقسیم فایل به قطعات 50 مگابایتی با استفاده از split لینوکسی
    print("✂️ در حال تقسیم به قطعات 50 مگابایتی...")
    base_name = "binance_data_split"
    # حذف قطعات قبلی
    for f in glob.glob(f"{base_name}.part*"):
        os.remove(f)
    
    cmd = ["split", "-b", "50M", full_zip, f"{base_name}.part"]
    subprocess.run(cmd, check=True)
    os.remove(full_zip)
    
    # نمایش قطعات ایجاد شده
    parts = sorted(glob.glob(f"{base_name}.part*"))
    for p in parts:
        size = os.path.getsize(p) / (1024*1024)
        print(f"   {p} ({size:.2f} MB)")
    print(f"✅ تعداد قطعات: {len(parts)}")

if __name__ == "__main__":
    main()