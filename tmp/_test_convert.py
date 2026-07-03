"""用9个已下载样本测试 _import_tick.py 的转换逻辑，打印前3行TSV。"""
import os
import sys
import tempfile

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _import_tick import zip_to_tsv_append

samples = [
    ("stock", r"d:\ZephyrAlpha\tmp\_sample_A股沪深.zip"),
    ("stock_bj", r"d:\ZephyrAlpha\tmp\_sample_stock_bj.zip"),
    ("index", r"d:\ZephyrAlpha\tmp\_sample_index.zip"),
    ("hk", r"d:\ZephyrAlpha\tmp\_sample_港股.zip"),
    ("etf", r"d:\ZephyrAlpha\tmp\_sample_ETF.zip"),
    ("lof", r"d:\ZephyrAlpha\tmp\_sample_lof.zip"),
    ("cb", r"d:\ZephyrAlpha\tmp\_sample_可转债.zip"),
    ("sector", r"d:\ZephyrAlpha\tmp\_sample_sector.zip"),
    ("mkt_index", r"d:\ZephyrAlpha\tmp\_sample_mkt_index.zip"),
]

tsv = tempfile.mktemp(suffix=".tsv")
for mt, zip_path in samples:
    if not os.path.exists(zip_path):
        print(f"\n[跳过] {mt}: {zip_path} 不存在")
        continue
    # 清空TSV
    open(tsv, "w").close()
    rows = zip_to_tsv_append(zip_path, tsv, mt)
    print(f"\n=== {mt} ({os.path.basename(zip_path)}) ===")
    print(f"  转换行数: {rows}")
    with open(tsv, "r", encoding="utf-8") as f:
        lines = f.readlines()
    print(f"  前3行TSV:")
    for line in lines[:3]:
        print(f"    {line.rstrip()}")
    if len(lines) > 3:
        print(f"  最后一行: {lines[-1].rstrip()}")

os.unlink(tsv)
