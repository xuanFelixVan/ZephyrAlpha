"""批量下载财务数据zip并探查格式"""
import subprocess
import os
import zipfile
import csv
import io

BDPAN = "/root/.local/bin/bdpan"
BASE = "量化交易数据/上市公司财务信息"
DEST = r"d:\ZephyrAlpha\data\raw\bdpan\financial"

FILES = [
    "财报披露计划.zip",
    "财务审计意见数据.zip",
    "财务指标数据.zip",
    "分红配股.zip",
    "分红送股数据.zip",
    "股东人数.zip",
    "股权质押明细.zip",
    "股权质押统计.zip",
    "利润表数据.zip",
    "前十大股东.zip",
    "前十大流通股东.zip",
    "现金流量表数据.zip",
    "限售股解禁.zip",
    "业绩快报数据.zip",
    "业绩预告数据.zip",
    "主营业务构成数据.zip",
    "资产负债表数据.zip",
]

os.makedirs(DEST, exist_ok=True)

# 1. 下载所有zip
for f in FILES:
    local_path = os.path.join(DEST, f)
    if os.path.exists(local_path):
        print(f"已存在: {f} ({os.path.getsize(local_path)/1024/1024:.1f}MB)")
        continue
    print(f"下载: {f} ...", end=" ", flush=True)
    wsl_local = local_path.replace("d:", "/mnt/d").replace("\\", "/")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'{BDPAN} download "{BASE}/{f}" "{wsl_local}"'],
                       capture_output=True, timeout=300)
    if os.path.exists(local_path):
        print(f"{os.path.getsize(local_path)/1024/1024:.1f}MB")
    else:
        print(f"失败: {r.stderr.decode('utf-8', errors='replace')[:100]}")

# 2. 探查每个zip的CSV格式
print("\n=== 格式探查 ===")
for f in FILES:
    local_path = os.path.join(DEST, f)
    if not os.path.exists(local_path):
        continue
    print(f"\n--- {f} ---")
    try:
        with zipfile.ZipFile(local_path, "r") as zf:
            names = [n for n in zf.namelist() if n.endswith(".csv")]
            print(f"  CSV数: {len(names)}")
            if names:
                content = zf.read(names[0])
                reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig"))
                for i, row in enumerate(reader):
                    print(f"  {row}")
                    if i >= 3:
                        break
    except Exception as e:
        print(f"  错误: {e}")
