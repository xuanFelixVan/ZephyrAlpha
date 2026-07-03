"""探查 QMT 港股 DataFrame 结构。"""
import sys
import os

QMT_LIB = r"D:\国金证券QMT交易端\bin.x64\Lib\site-packages"
QMT_HOME = r"D:\国金证券QMT交易端\bin.x64"
sys.path.append(QMT_LIB)
os.chdir(QMT_HOME)

from xtquant import xtdata

client = xtdata.get_client()
print(f"QMT connected: {client.is_connected()}")

sym = "01680.HK"
start = "20250101"
end = "20260704"

# 下载
xtdata.download_history_data(sym, "1d", start, end)
data = xtdata.get_market_data_ex([], [sym], "1d", start, end)
df = data[sym]

print(f"\n=== DataFrame info ===")
print(f"shape: {df.shape}")
print(f"index type: {type(df.index)}")
print(f"index dtype: {df.index.dtype}")
print(f"columns: {list(df.columns)}")
print(f"\n=== First 3 rows ===")
print(df.head(3))
print(f"\n=== Index values (first 5) ===")
print(list(df.index[:5]))
print(f"\n=== Index values type ===")
for i, v in enumerate(df.index[:3]):
    print(f"  [{i}] type={type(v).__name__}, val={v}, float={float(v) if isinstance(v, (int, float)) or str(v).replace('.','').replace('-','').isdigit() else 'N/A'}")

# 尝试解析时间戳
import pandas as pd
print(f"\n=== Timestamp parsing ===")
ts0 = df.index[0]
print(f"index[0] = {ts0} (type={type(ts0).__name__})")
try:
    v = float(ts0)
    print(f"  float(ts0) = {v}")
    if v > 1e14:
        dt = pd.Timestamp(v, unit="us")
        print(f"  as us: {dt}")
    elif v > 1e11:
        dt = pd.Timestamp(v, unit="ms")
        print(f"  as ms: {dt}")
    else:
        dt = pd.Timestamp(v, unit="s")
        print(f"  as s: {dt}")
    print(f"  year: {dt.year}")
except Exception as e:
    print(f"  float() failed: {e}")
    try:
        dt = pd.Timestamp(ts0)
        print(f"  pd.Timestamp(ts0) = {dt}, year={dt.year}")
    except Exception as e2:
        print(f"  pd.Timestamp failed: {e2}")

print(f"\n=== Row 0 data ===")
row = df.iloc[0]
print(f"row keys: {list(row.index)}")
for col in df.columns:
    print(f"  {col} = {row[col]} (type={type(row[col]).__name__})")
