"""探查复权因子_tushare zip + 指数K线zip + 日K线不复权zip 的格式"""
import zipfile
import csv
import io
import os

FILES = [
    (r"d:\ZephyrAlpha\data\raw\bdpan\adj_factor_tushare\复权因子.zip", "复权因子_tushare"),
    (r"d:\ZephyrAlpha\data\raw\bdpan\index_kline\指数_日_kline.zip", "指数日K线"),
    (r"d:\ZephyrAlpha\data\raw\bdpan\index_kline\中证指数_日_kline.zip", "中证指数日K线"),
    (r"d:\ZephyrAlpha\data\raw\bdpan\daily_extra\daily.zip", "日K线不复权"),
    (r"d:\ZephyrAlpha\data\raw\bdpan\daily_extra\daily_hfq.zip", "日K线后复权"),
    (r"d:\ZephyrAlpha\data\raw\bdpan\daily_extra\weekly.zip", "周K线不复权"),
    (r"d:\ZephyrAlpha\data\raw\bdpan\daily_extra\weekly_hfq.zip", "周K线后复权"),
]

for fp, name in FILES:
    if not os.path.exists(fp):
        print(f"\n--- {name} --- 不存在: {fp}")
        continue
    sz = os.path.getsize(fp) / 1024 / 1024
    print(f"\n--- {name} ({sz:.0f}MB) ---")
    try:
        with zipfile.ZipFile(fp, "r") as zf:
            names = [n for n in zf.namelist() if n.endswith(".csv")]
            print(f"  CSV数: {len(names)}")
            if names:
                content = zf.read(names[0])
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig"))
                for j, row in enumerate(reader):
                    if j < 3:
                        print(f"    {row}")
                    else:
                        break
    except zipfile.BadZipFile as e:
        print(f"  损坏: {e}")
