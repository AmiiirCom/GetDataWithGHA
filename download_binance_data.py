# download_data.py
import os
from binance_historical_data import BinanceDataDumper
from datetime import datetime

def setup_and_download():
    # ایجاد پوشه دیتا (مشابه کد قبلی)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data", "raw")
    os.makedirs(data_dir, exist_ok=True)

    # --- تنظیمات دانلود ---
    dumper = BinanceDataDumper(
        path_dir_where_to_dump=data_dir,
        asset_class="spot",                # دانلود از بازار اسپات
        data_type="klines",                # دانلود کندل‌ها
        data_frequency="1h"                # تایم فریم 1 ساعته
    )

    # --- شروع دانلود ---
    print("شروع به دانلود کندل‌های 1 ساعته BTCUSDT (از 2017 تا امروز)...")
    dumper.dump_data(
        tickers=["BTCUSDT"],               # فقط نماد مدنظر
        date_start=datetime(2017, 1, 1),   # از این تاریخ
        date_end=datetime.now(),           # تا امروز
        is_to_update_existing=False
    )

    # --- دانلود تایم فریم 15 دقیقه - توجه: این کار را جداگانه انجام می‌دهد ---
    print("\nشروع به دانلود کندل‌های 15 دقیقه‌ای...")

    # برای تایم فریم 15 دقیقه، متغیر new_dumper را در پوشه دیگری تعریف کنید
    # (library فعلاً در یک run نمی‌تواند دو تایم فریم جدا دانلود کند)
    new_dumper = BinanceDataDumper(
        path_dir_where_to_dump=data_dir,
        asset_class="spot",
        data_type="klines",
        data_frequency="15m"
    )
    new_dumper.dump_data(
        tickers=["BTCUSDT"],
        date_start=datetime(2017, 1, 1),
        date_end=datetime.now(),
        is_to_update_existing=False
    )
    
    print("\n✅ تمامی دانلودها با موفقیت انجام شد.")

if __name__ == "__main__":
    setup_and_download()