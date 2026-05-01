#!/usr/bin/env python
# coding: utf-8

import os
import subprocess
import shutil
from binance_historical_data import BinanceDataDumper
from datetime import date

def download_data():
    """دانلود داده‌های ۱ ساعته و ۱۵ دقیقه‌ای BTCUSDT از ۲۰۱۷ تا امروز"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data", "raw")
    os.makedirs(data_dir, exist_ok=True)

    # حذف فایل‌های قبلی (در صورت وجود) برای جلوگیری از تداخل
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir, exist_ok=True)

    # ----- تایم فریم ۱ ساعته -----
    print("🚀 دانلود داده‌های 1 ساعته BTCUSDT...")
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

    # ----- تایم فریم ۱۵ دقیقه -----
    print("🚀 دانلود داده‌های 15 دقیقه‌ای BTCUSDT...")
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

    print("✅ دانلود کامل شد.")
    return data_dir

def zip_and_split(data_dir, output_zip_base="binance_data", part_size_mb=50):
    """
    همه فایل‌های CSV داخل data_dir را پیدا کرده، یک فایل ZIP بزرگ می‌سازد
    و سپس آن را به پارت‌های part_size_mb مگابایتی تقسیم می‌کند.
    پارت‌های نهایی به صورت binance_data.z01, binance_data.z02, ... و binance_data.zip ذخیره می‌شوند.
    """
    # جمع‌آوری تمام فایل‌های CSV در یک لیست
    csv_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    if not csv_files:
        print("❌ هیچ فایل CSV یافت نشد!")
        return None

    # همه فایل‌ها را در یک دایرکتوری موقت جمع می‌کنیم (برای جلوگیری از ساختار پوشه‌ها)
    temp_dir = os.path.join(os.path.dirname(data_dir), "temp_zip")
    os.makedirs(temp_dir, exist_ok=True)
    for f in csv_files:
        shutil.copy2(f, temp_dir)   # کپی فایل بدون حفظ ساختار زیرپوشه‌ها

    # مسیر فایل ZIP نهایی (قبل از اسپلیت)
    full_zip = os.path.join(os.path.dirname(data_dir), f"{output_zip_base}_full.zip")
    # ساخت ZIP از همه فایل‌های داخل temp_dir
    subprocess.run(["zip", "-j", full_zip, temp_dir + "/*"], check=True)

    # حذف دایرکتوری موقت
    shutil.rmtree(temp_dir)

    # تقسیم فایل ZIP به پارت‌های ۵۰ مگابایتی (با استفاده از ابزار zip)
    # خروجی: f"{output_zip_base}.zip", f"{output_zip_base}.z01", f"{output_zip_base}.z02", ...
    split_zip_base = os.path.join(os.path.dirname(data_dir), output_zip_base)
    subprocess.run(["zip", "-s", f"{part_size_mb}m", full_zip, "--out", split_zip_base], check=True)

    # حذف فایل ZIP کامل
    os.remove(full_zip)

    # حذف پوشه داده اصلی تا فقط فایل‌های ZIP پارت شده در مخزن بمانند (اختیاری)
    shutil.rmtree(data_dir)

    # برگرداندن لیست فایل‌های پارت شده
    part_files = []
    for f in os.listdir(os.path.dirname(data_dir)):
        if f.startswith(output_zip_base) and (f.endswith(".zip") or f.endswith(".z01") or f.endswith(".z02") or f.endswith(".z03")):
            part_files.append(os.path.join(os.path.dirname(data_dir), f))
    return part_files

if __name__ == "__main__":
    data_dir = download_data()
    parts = zip_and_split(data_dir, part_size_mb=50)
    if parts:
        print("🎉 فایل‌های پارت شده ایجاد شدند:")
        for p in parts:
            print(f"   {p}")
    else:
        print("❌ خطا در ایجاد پارت‌ها")