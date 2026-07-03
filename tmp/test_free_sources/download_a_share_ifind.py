# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/test_free_sources/download_a_share_ifind.py | §data-source-verification
# [MODULE] tmp.download_a_share_ifind
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.security.secrets; iFinDPy
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 一次性数据源验证脚本——iFind API 验证
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=验证完成
# [TESTS]
# [TTL] task_bound

"""iFind 批量下载A股日K线增量 (2025-11-13 ~ 2026-07-03)
iFind THS_HistoryQuotes 支持多只股票逗号分隔, 每批20只, 5758只需3分钟
代码格式: 000001 → 000001.SZ, 600000 → 600000.SH
输出CSV: trade_date,symbol,open,high,low,close,volume,amount
"""
import sys
import csv
import time
from iFinDPy import *
import time as _time  # iFinDPy的import *覆盖了time模块, 重命名导入
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

INPUT_FILE = r'd:\ZephyrAlpha\tmp\test_free_sources\a_share_symbols.txt'
OUTPUT_CSV = r'd:\ZephyrAlpha\tmp\test_free_sources\a_share_incremental.csv'
START_DATE = '2025-11-13'
END_DATE = '2026-07-03'
BATCH_SIZE = 20  # 每批20只股票

# 读取股票代码
with open(INPUT_FILE, 'r') as f:
    symbols = [line.strip() for line in f if line.strip()]

print(f"待下载: {len(symbols)} 只A股 ({START_DATE} ~ {END_DATE}), 每批{BATCH_SIZE}只")

# 转换代码格式: 000001 → 000001.SZ, 600000 → 600000.SH, 920981 → sz.920981
def to_ifind_code(sym):
    if sym.startswith('6') or sym.startswith('9'):
        return f'{sym}.SH'
    elif sym.startswith('0') or sym.startswith('3') or sym.startswith('2'):
        return f'{sym}.SZ'
    elif sym.startswith('8') or sym.startswith('4'):
        return f'{sym}.BJ'  # 北交所
    else:
        return None  # T开头等跳过

# 登录
r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f"iFind登录: {r} (0=成功, -201=已登录)")

# 批量下载
all_rows = []
success = 0
failed = 0
start_time = _time.time()

# 分批
batches = []
for i in range(0, len(symbols), BATCH_SIZE):
    batch = symbols[i:i+BATCH_SIZE]
    batches.append(batch)

print(f"共 {len(batches)} 批")

for i, batch in enumerate(batches, 1):
    # 转换代码
    ifind_codes = [to_ifind_code(s) for s in batch]
    valid = [(sym, code) for sym, code in zip(batch, ifind_codes) if code is not None]
    if not valid:
        continue
    codes_str = ','.join([c for _, c in valid])
    sym_map = {c: s for s, c in valid}

    try:
        data = THS_HistoryQuotes(
            codes_str,
            'open,high,low,close,volume,amount',
            'Interval:D',
            START_DATE,
            END_DATE
        )
        df = THS_Trans2DataFrame(data)
        if df is not None and len(df) > 0:
            for _, row in df.iterrows():
                thscode = str(row.get('thscode', ''))
                # 去掉 .SH/.SZ 后缀, 保持与现有 daily_kline 表一致
                symbol = thscode.split('.')[0] if '.' in thscode else thscode
                try:
                    all_rows.append({
                        'trade_date': str(row.get('time', ''))[:10],
                        'symbol': symbol,
                        'open': float(row.get('open', 0)),
                        'high': float(row.get('high', 0)),
                        'low': float(row.get('low', 0)),
                        'close': float(row.get('close', 0)),
                        'volume': int(float(row.get('volume', 0))),
                        'amount': float(row.get('amount', 0)),
                    })
                except (ValueError, TypeError):
                    continue
            success += len(valid)
        else:
            failed += len(valid)
    except Exception as e:
        failed += len(valid)

    if i % 20 == 0 or i == len(batches):
        elapsed = _time.time() - start_time
        rate = i / elapsed
        remaining = (len(batches) - i) / rate
        print(f"  批次 {i}/{len(batches)} ({rate:.1f}/s, 预计剩余 {remaining:.0f}s), 累计 {len(all_rows)} 行")

elapsed = _time.time() - start_time
print(f"\n下载完成: {success} 成功, {failed} 失败, 耗时 {elapsed:.1f}s")
print(f"总行数: {len(all_rows)}")

# 写CSV
with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=['trade_date', 'symbol', 'open', 'high', 'low', 'close', 'volume', 'amount'])
    writer.writeheader()
    writer.writerows(all_rows)

print(f"CSV文件: {OUTPUT_CSV}")

THS_iFinDLogout()
