# download_binance_data.py
import os
from binance_historical_data import BinanceDataDumper
from datetime import date, datetime   # اضافه کردن date

def setup_and_download():
    # ایجاد پوشه دیتا (مشابه کد قبلی)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(script_dir, "data", "raw")
    os.makedirs(data_dir, exist_ok=True)

    # --- تنظیمات دانلود 1 ساعته ---
    dumper = BinanceDataDumper(
        path_dir_where_to_dump=data_dir,
        asset_class="spot",
        data_type="klines",
        data_frequency="1h"
    )

    print("شروع به دانلود کندل‌های 1 ساعته BTCUSDT (از 2017 تا امروز)...")
    dumper.dump_data(
        tickers=["BTCUSDT"],
        date_start=date(2017, 1, 1),          # ✅ استفاده از date
        date_end=date.today(),                # ✅ امروز به صورت date
        is_to_update_existing=False
    )

    # --- دانلود تایم فریم 15 دقیقه ---
    print("\nشروع به دانلود کندل‌های 15 دقیقه‌ای BTCUSDT...")
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

    print("\n✅ تمامی دانلودها با موفقیت انجام شد.")

if __name__ == "__main__":
    setup_and_download()