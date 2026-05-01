#!/usr/bin/env python
# coding: utf-8

import os
import shutil
import zipfile
import subprocess
from binance_historical_data import BinanceDataDumper
from datetime import date
import glob

def download_data():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data", "raw")
    
    # پاک کردن پوشه قبلی
    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)
    os.makedirs(data_dir, exist_ok=True)

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

def zip_files(csv_files, output_zip_path):
    """ایجاد یک فایل ZIP از لیست فایل‌های CSV"""
    with zipfile.ZipFile(output_zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in csv_files:
            # افزودن فایل با نام پایه (بدون مسیر)
            arcname = os.path.basename(file)
            zipf.write(file, arcname=arcname)
    return output_zip_path

def split_file(file_path, part_size_mb=50):
    """تقسیم فایل به پارت‌های با حجم مشخص با استفاده از دستور split لینوکسی"""
    part_size_bytes = part_size_mb * 1024 * 1024
    base_name = os.path.splitext(file_path)[0]  # بدون .zip
    # استفاده از split با پسوند .partaa, .partab, ...
    cmd = ["split", "-b", str(part_size_bytes), file_path, f"{base_name}.part"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"خطا در split: {result.stderr}")
    # حذف فایل اصلی
    os.remove(file_path)
    # برگرداندن لیست فایل‌های پارت شده
    parts = sorted(glob.glob(f"{base_name}.part*"))
    return parts

def main():
    # دانلود داده
    data_dir = download_data()
    
    # جمع آوری همه فایل‌های CSV
    csv_files = []
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))
    
    if not csv_files:
        print("❌ هیچ فایل CSV یافت نشد!")
        return
    
    print(f"📁 تعداد فایل‌های CSV: {len(csv_files)}")
    
    # دایرکتوری والد (همان root پروژه)
    parent_dir = os.path.dirname(data_dir)
    zip_full_path = os.path.join(parent_dir, "binance_data_full.zip")
    
    # ساخت ZIP
    print("📦 در حال ساخت فایل ZIP...")
    zip_files(csv_files, zip_full_path)
    zip_size = os.path.getsize(zip_full_path) / (1024*1024)
    print(f"✅ ZIP ساخته شد. حجم: {zip_size:.2f} MB")
    
    # تقسیم به پارت‌های ۵۰ مگابایتی
    print("✂️ در حال تقسیم ZIP به پارت‌های 50 مگابایتی...")
    parts = split_file(zip_full_path, part_size_mb=50)
    print(f"✅ تعداد پارت‌ها: {len(parts)}")
    
    # حذف پوشه data/raw برای کاهش حجم در مخزن (اختیاری)
    shutil.rmtree(data_dir)
    
    # نمایش لیست پارت‌ها
    for p in parts:
        size_mb = os.path.getsize(p) / (1024*1024)
        print(f"   {p} ({size_mb:.2f} MB)")

if __name__ == "__main__":
    main()