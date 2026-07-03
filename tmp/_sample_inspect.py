"""下载并检查一个ETF tick zip样本，验证CSV内部格式。"""
import io
import os
import subprocess
import zipfile

remote = "量化交易数据/基金_分笔成交/ETF分笔成交_按月归档/2005-02/20050223.zip"
local = r"d:\ZephyrAlpha\tmp\_sample_20050223.zip"

# 下载（已存在则跳过）
if not os.path.exists(local):
    print(f"下载 {remote}...")
    r = subprocess.run(["wsl", "-d", "Ubuntu", "-e", "bash", "-c",
                        f'/root/.local/bin/bdpan download "{remote}" "{local.replace(chr(92), "/").replace("d:", "/mnt/d")}"'],
                       capture_output=True, timeout=120)
    print(f"  returncode={r.returncode}")
    if r.returncode != 0 or not os.path.exists(local):
        print(f"  下载失败: {r.stderr.decode('utf-8', errors='replace')[:200]}")
        raise SystemExit(1)
print(f"  本地大小: {os.path.getsize(local)} bytes")

# 解压并检查
with zipfile.ZipFile(local, "r") as zf:
    names = zf.namelist()
    print(f"\n=== zip内文件数: {len(names)} ===")
    print(f"前5个文件名: {names[:5]}")

    csv_names = [n for n in names if n.lower().endswith(".csv")]
    if not csv_names:
        print("⚠ zip内无CSV文件！尝试列出所有文件类型:")
        exts = set(os.path.splitext(n)[1].lower() for n in names)
        print(f"  文件扩展名: {exts}")
        raise SystemExit(1)

    print(f"\n=== 第一个CSV: {csv_names[0]} ===")
    content = zf.read(csv_names[0])
    text = content.decode("utf-8", errors="replace")
    lines = text.splitlines()
    print(f"总行数: {len(lines)}")
    print(f"\n前5行内容:")
    for i, line in enumerate(lines[:5], 1):
        print(f"  [{i}] {line}")

    # 检查是否有表头
    if lines:
        print(f"\n=== 表头字段数 ===")
        header = lines[0].split(",")
        print(f"  表头字段({len(header)}): {header}")
        if len(lines) > 1:
            sample = lines[1].split(",")
            print(f"  数据行字段({len(sample)}): {sample}")
