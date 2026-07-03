# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/verify_extra2.py | §data-source-verification
# [MODULE] tmp.verify_extra2
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

"""补充验证：北向资金查询 + 期货主力合约K线 + EDB返回内容"""
from iFinDPy import *
import sys, os
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

# ============ iFind补充测试 ============
r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print("=" * 70)
print("iFind补充测试")
print("=" * 70)

# 北向资金换查询语句
print("\n>>> 北向资金查询测试 <<<\n")
for query in ['沪股通净买入前10只股票', '深股通净买入前10只股票', '沪深股通净买入前10只股票', '今日北向资金净流入']:
    try:
        data = THS_iwencai(query, 'stock')
        if data and 'tables' in data and len(data['tables']) > 0:
            table = data['tables'][0].get('table', {})
            if table:
                first_key = list(table.keys())[0]
                rows = len(table[first_key]) if isinstance(table[first_key], list) else 1
                print(f"  ✅ '{query}' → {rows}行 | 字段: {list(table.keys())[:5]}")
            else:
                print(f"  ⚠️ '{query}' → table为空")
        else:
            print(f"  ❌ '{query}' → 无数据")
    except Exception as e:
        print(f"  ❌ '{query}' → {e}")

# EDB返回内容检查
print("\n>>> EDB返回内容检查 <<<\n")
try:
    data = THS_EDBQuery('M001620326', '2025-01-01', '2025-06-30')
    if isinstance(data, dict) or hasattr(data, 'get'):
        ec = data.get('errorcode', 'N/A') if hasattr(data, 'get') else getattr(data, 'errorcode', 'N/A')
        errmsg = data.get('errmsg', '') if hasattr(data, 'get') else getattr(data, 'errmsg', '')
        tables = data.get('tables', []) if hasattr(data, 'get') else getattr(data, 'tables', [])
        print(f"  EDB errorcode={ec} errmsg={errmsg} tables数量={len(tables) if tables else 0}")
        if tables:
            print(f"  EDB有数据!")
    else:
        print(f"  EDB返回类型: {type(data)}, 内容: {str(data)[:300]}")
except Exception as e:
    print(f"  EDB异常: {e}")

# ============ QMT补充测试：期货主力合约K线 ============
print("\n" + "=" * 70)
print("QMT补充测试：期货主力合约K线")
print("=" * 70)

sys.path.append(r'D:\国金证券QMT交易端\bin.x64\Lib\site-packages')
os.chdir(r'D:\国金证券QMT交易端\bin.x64')
from xtquant import xtdata

# 找中金所的期货合约（非期权）
print("\n>>> 中金所期货合约（非期权）<<<\n")
cffex = xtdata.get_stock_list_in_sector('中金所')
futures_only = [c for c in cffex if '-C-' not in c and '-P-' not in c and c[0:2] in ['IF', 'IC', 'IH', 'IM']]
print(f"中金所期货合约(非期权): {len(futures_only)}个")
if futures_only:
    print(f"前10个: {futures_only[:10]}")
    # 测试第一个期货合约的K线
    code = futures_only[0]
    print(f"\n测试期货合约K线: {code}")
    xtdata.download_history_data(code, '1d', '20250601', '20250630')
    data = xtdata.get_market_data_ex([], [code], '1d', '20250601', '20250630')
    if code in data:
        df = data[code]
        print(f"  K线: ✅ {len(df)}行")
        print(f"  字段: {list(df.columns)}")
        if len(df) > 0:
            print(f"  首行数据:")
            row = df.head(1).to_dict('records')[0]
            for k, v in row.items():
                print(f"    {k}: {v}")
            # 重点检查openInterest
            if 'openInterest' in df.columns:
                print(f"\n  >>> openInterest(持仓量)有数据: {df['openInterest'].iloc[0]} <<<")
    else:
        print(f"  K线: ⚠️ 返回空")

# 测试上期所主力期货合约
print("\n>>> 上期所期货合约测试 <<<\n")
shfe = xtdata.get_stock_list_in_sector('上期所')
# 找非期权的合约（不含P或C）
shfe_futures = [c for c in shfe if '-P-' not in c and '-C-' not in c and not c.endswith('P') or '.SF' in c]
# 取前几个看起来像期货的
shfe_real = [c for c in shfe if len(c.split('.')[0]) <= 6 and '-P-' not in c and '-C-' not in c]
print(f"上期所可能的期货合约: {len(shfe_real)}个")
if shfe_real:
    print(f"前10个: {shfe_real[:10]}")
    code = shfe_real[0]
    print(f"\n测试: {code}")
    xtdata.download_history_data(code, '1d', '20250601', '20250630')
    data = xtdata.get_market_data_ex([], [code], '1d', '20250601', '20250630')
    if code in data:
        df = data[code]
        print(f"  K线: ✅ {len(df)}行")
        if len(df) > 0:
            print(f"  首行: {df.head(1).to_dict('records')[0]}")

print("\n" + "=" * 70)
print("补充验证完成")
