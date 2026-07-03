"""探查weekly/monthly/5min zip格式"""
import zipfile
import os

BASE = r"d:\ZephyrAlpha\data\raw\bdpan"

for name, path in [
    ("weekly_qfq", os.path.join(BASE, "kline", "weekly_qfq.zip")),
    ("monthly_qfq", os.path.join(BASE, "kline", "monthly_qfq.zip")),
    ("5min_2000", os.path.join(BASE, "5min", "2000_5min.zip")),
]:
    print(f"\n{'='*60}")
    print(f"{name}: {os.path.getsize(path)/1024/1024:.1f}MB")
    print(f"{'='*60}")
    with zipfile.ZipFile(path, "r") as zf:
        names = zf.namelist()
        print(f"文件数: {len(names)}")
        print(f"前5个: {names[:5]}")
        # 读取第一个CSV文件
        if names:
            for n in names:
                if n.endswith(".csv"):
                    content = zf.read(n)
                    for enc in ["utf-8", "gbk"]:
                        try:
                            text = content.decode(enc)
                            lines = text.strip().split("\n")
                            print(f"  文件: {n}, encoding={enc}, 行数={len(lines)}")
                            for i, line in enumerate(lines[:5]):
                                print(f"  L{i}: {line[:200]}")
                            break
                        except UnicodeDecodeError:
                            continue
                    break
