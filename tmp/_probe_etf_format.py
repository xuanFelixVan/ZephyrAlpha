"""探查ETF和LOF分钟K线zip的格式"""
import zipfile
import csv
import io
import os

FILES = [
    r"d:\ZephyrAlpha\data\raw\bdpan\etf_minute\ETF_1min_2005_2022.zip",
    r"d:\ZephyrAlpha\data\raw\bdpan\etf_minute\ETF_5min_2005_2024.zip",
    r"d:\ZephyrAlpha\data\raw\bdpan\etf_minute\ETF_15min_2005_2024.zip",
]

for fp in FILES:
    if not os.path.exists(fp):
        print(f"\n--- {os.path.basename(fp)} --- 不存在")
        continue
    sz = os.path.getsize(fp) / 1024 / 1024
    print(f"\n--- {os.path.basename(fp)} ({sz:.0f}MB) ---")
    with zipfile.ZipFile(fp, "r") as zf:
        names = [n for n in zf.namelist() if n.endswith(".csv")]
        print(f"  CSV数: {len(names)}")
        # 看3个文件的header
        for name in names[:3]:
            print(f"  --- {name} ---")
            content = zf.read(name)
            reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig"))
            for j, row in enumerate(reader):
                if j < 3:
                    print(f"    {row}")
                else:
                    break
