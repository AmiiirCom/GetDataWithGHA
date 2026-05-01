#!/usr/bin/env python
# coding: utf-8

import os
import subprocess
import shutil
from binance_historical_data import BinanceDataDumper
from datetime import date
import glob

def download_data():
    """دانلود داده‌های ۱ ساعته و ۱۵ دقیقه‌ای BTCUSDT از ۲۰۱۷ تا امروز"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data", "raw")
    
    # حذف پوشه قبلی برای شروع تمیز
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

    print(f"📁 تعداد فایل‌های CSV پیدا شده: {len(csv_files)}")

    # دایرکتوری موقت برای جمع کردن فایل‌ها (بدون ساختار پوشه)
    parent_dir = os.path.dirname(data_dir)
    temp_dir = os.path.join(parent_dir, "temp_zip")
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    for f in csv_files:
        shutil.copy2(f, temp_dir)   # کپی فایل بدون حفظ ساختار زیرپوشه‌ها

    # مسیر فایل ZIP نهایی (قبل از اسپلیت)
    full_zip = os.path.join(parent_dir, f"{output_zip_base}_full.zip")
    
    # استفاده از لیست فایل‌ها به جای wildcard
    file_list = glob.glob(os.path.join(temp_dir, "*.csv"))
    if not file_list:
        print("❌ هیچ فایل CSV در temp_dir کپی نشد!")
        shutil.rmtree(temp_dir)
        return None

    # ساخت ZIP از همه فایل‌ها (با -j برای حذف مسیر)
    cmd = ["zip", "-j", full_zip] + file_list
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ خطا در ساخت ZIP: {result.stderr}")
        shutil.rmtree(temp_dir)
        return None

    # حذف دایرکتوری موقت
    shutil.rmtree(temp_dir)

    # تقسیم فایل ZIP به پارت‌های ۵۰ مگابایتی
    split_zip_base = os.path.join(parent_dir, output_zip_base)
    # ابتدا فایل خروجی قبلی را حذف می‌کنیم (در صورت وجود)
    for ext in [".zip", ".z01", ".z02", ".z03", ".z04", ".z05"]:
        fpath = split_zip_base + ext
        if os.path.exists(fpath):
            os.remove(fpath)

    cmd_split = ["zip", "-s", f"{part_size_mb}m", full_zip, "--out", split_zip_base]
    result = subprocess.run(cmd_split, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"❌ خطا در تقسیم ZIP: {result.stderr}")
        return None

    # حذف فایل ZIP کامل
    os.remove(full_zip)

    # حذف پوشه داده اصلی برای کاهش حجم (اختیاری)
    shutil.rmtree(data_dir)

    # برگرداندن لیست فایل‌های پارت شده
    part_files = glob.glob(split_zip_base + ".*")
    return part_files

if __name__ == "__main__":
    data_dir = download_data()
    parts = zip_and_split(data_dir, part_size_mb=50)
    if parts:
        print("🎉 فایل‌های پارت شده ایجاد شدند:")
        for p in parts:
            print(f"   {p} ({os.path.getsize(p) / (1024*1024):.2f} MB)")
    else:
        print("❌ خطا در ایجاد پارت‌ها")
        exit(1)