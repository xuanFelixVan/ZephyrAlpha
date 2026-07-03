"""探查 daily_qfq.zip 和 15min zip 的CSV格式"""
import zipfile
import csv
import io

# 1. daily_qfq.zip
print("=== daily_qfq.zip ===")
with zipfile.ZipFile(r"d:\ZephyrAlpha\data\raw\bdpan\daily\daily_qfq.zip", "r") as zf:
    names = [n for n in zf.namelist() if n.endswith(".csv")]
    print(f"CSV文件数: {len(names)}")
    print(f"前5个: {names[:5]}")
    # 读第一个CSV
    content = zf.read(names[0])
    reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8"))
    for i, row in enumerate(reader):
        print(row)
        if i >= 5:
            break

# 2. 2026_15min.zip
print("\n=== 2026_15min.zip ===")
with zipfile.ZipFile(r"d:\ZephyrAlpha\data\raw\bdpan\15min\2026_15min.zip", "r") as zf:
    names = [n for n in zf.namelist() if n.endswith(".csv")]
    print(f"CSV文件数: {len(names)}")
    print(f"前5个: {names[:5]}")
    content = zf.read(names[0])
    reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8"))
    for i, row in enumerate(reader):
        print(row)
        if i >= 5:
            break
