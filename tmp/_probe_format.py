"""探查下载的CSV和zip样本格式"""
import os
import zipfile
import csv

BASE = r"d:\ZephyrAlpha\data\raw\bdpan"

# 1. 探查所有CSV文件
print("=" * 60)
print("CSV 文件格式探查")
print("=" * 60)
csv_dir = os.path.join(BASE, "csv")
for fn in sorted(os.listdir(csv_dir)):
    if not fn.endswith(".csv"):
        continue
    fp = os.path.join(csv_dir, fn)
    sz = os.path.getsize(fp)
    print(f"\n--- {fn} ({sz/1024:.0f}KB) ---")
    # 尝试不同编码
    for enc in ["utf-8", "gbk", "utf-8-sig"]:
        try:
            with open(fp, "r", encoding=enc) as f:
                lines = [next(f).rstrip() for _ in range(4)]
            print(f"  encoding={enc}")
            for i, line in enumerate(lines):
                print(f"  L{i}: {line[:200]}")
            break
        except (UnicodeDecodeError, StopIteration):
            continue

# 2. 探查5分钟K线zip样本
print("\n" + "=" * 60)
print("5分钟K线 zip 样本")
print("=" * 60)
sample = os.path.join(BASE, "sample", "5min_sample.zip")
with zipfile.ZipFile(sample, "r") as zf:
    names = zf.namelist()
    print(f"zip内文件数: {len(names)}")
    print(f"前5个文件名: {names[:5]}")
    # 读取第一个文件
    if names:
        content = zf.read(names[0])
        for enc in ["utf-8", "gbk", "utf-8-sig"]:
            try:
                text = content.decode(enc)
                lines = text.strip().split("\n")
                print(f"  encoding={enc}, 行数={len(lines)}")
                for i, line in enumerate(lines[:5]):
                    print(f"  L{i}: {line[:200]}")
                break
            except UnicodeDecodeError:
                continue
