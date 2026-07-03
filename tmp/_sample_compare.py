"""对比检查 A股沪深 + ETF + 可转债 三个市场的tick CSV格式。"""
import io
import os
import subprocess
import zipfile

samples = [
    ("A股沪深", "量化交易数据/A股数据_分笔数据/分笔成交_按月归档_沪深/2000-06/20000609.zip"),
    ("ETF", "量化交易数据/基金_分笔成交/ETF分笔成交_按月归档/2005-02/20050223.zip"),
    ("可转债", "量化交易数据/可转债_分笔成交/可转债_分笔成交_按月归档/2018-09/20180904.zip"),
    ("港股", "量化交易数据/港股_分笔成交/港股_分笔成交_按月归档/2025-01/20250102.zip"),
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
        # 读第一个CSV
        content = zf.read(csv_names[0])
        text = content.decode("utf-8", errors="replace")
        lines = text.splitlines()
        print(f"  第一个CSV行数: {len(lines)}")
        print(f"  前5行:")
        for i, line in enumerate(lines[:5], 1):
            print(f"    [{i}] {line}")
        # 检查最后一行
        if len(lines) > 5:
            print(f"  最后一行: {lines[-1]}")
