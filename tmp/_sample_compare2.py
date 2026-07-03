"""检查剩余5个市场的tick CSV格式：stock_bj/index/lof/sector/mkt_index。"""
import os
import subprocess
import zipfile

samples = [
    ("stock_bj", "量化交易数据/A股数据_分笔数据/分笔成交_按月归档_京市/2020-07/20200727.zip"),
    ("index", "量化交易数据/A股数据_分笔成交_指数/指数分笔成交_沪深京_按月归档/2000-07/20000714.zip"),
    ("lof", "量化交易数据/基金_分笔成交/LOF分笔成交_按月归档/2008-06/20080612.zip"),
    ("sector", "量化交易数据/通达信板块_分笔成交/通达信板块_分笔成交_按月归档/2011-11/20111103.zip"),
    ("mkt_index", "量化交易数据/通达信板块_分笔成交/通达信_市场统计指数_分笔成交_按月归档/2011-11/20111103.zip"),
]

for name, remote in samples:
    local = rf"d:\ZephyrAlpha\tmp\_sample_{name}.zip"
    print(f"\n{'='*60}")
    print(f"=== {name}: {remote} ===")

    if not os.path.exists(local):
        r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                            f'/root/.local/bin/bdpan download "{remote}" "{local.replace(chr(92), "/").replace("d:", "/mnt/d")}"'],
                           capture_output=True, timeout=180)
        if r.returncode != 0 or not os.path.exists(local):
            print(f"  下载失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
            continue

    print(f"  zip大小: {os.path.getsize(local)/1024:.1f}KB")
    with zipfile.ZipFile(local, "r") as zf:
        names = zf.namelist()
        csv_names = [n for n in names if n.lower().endswith(".csv")]
        print(f"  文件总数: {len(names)}, CSV数: {len(csv_names)}")
        if not csv_names:
            print(f"  ⚠ 无CSV, 所有文件名: {names[:5]}")
            continue
        print(f"  前3个CSV: {csv_names[:3]}")
        content = zf.read(csv_names[0])
        text = content.decode("utf-8", errors="replace")
        lines = text.splitlines()
        print(f"  第一个CSV行数: {len(lines)}")
        print(f"  前5行:")
        for i, line in enumerate(lines[:5], 1):
            print(f"    [{i}] {line}")
        if len(lines) > 5:
            print(f"  最后一行: {lines[-1]}")
