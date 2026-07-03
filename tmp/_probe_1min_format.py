"""探查2025_1min.zip格式（确认列结构与15/30/60min一致）"""
import zipfile
import csv
import io
import os

ZIP_PATH = r"d:\ZephyrAlpha\data\raw\bdpan\1min\2025_1min.zip"

print(f"=== 探查 {os.path.basename(ZIP_PATH)} ===")
print(f"文件大小: {os.path.getsize(ZIP_PATH)/1024/1024/1024:.2f}GB")

with zipfile.ZipFile(ZIP_PATH, "r") as zf:
    names = [n for n in zf.namelist() if n.endswith(".csv")]
    print(f"CSV文件数: {len(names)}")
    # 看前3个文件的header和2行数据
    for i, name in enumerate(names[:3]):
        print(f"\n--- {name} ---")
        content = zf.read(name)
        reader = csv.reader(io.TextIOWrapper(io.BytesIO(content), encoding="utf-8-sig"))
        for j, row in enumerate(reader):
            if j < 3:
                print(f"  {row}")
            else:
                break
