# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/verify_ifind2.py | §data-source-verification
# [MODULE] tmp.verify_ifind2
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

"""iFind补充：北向资金 + EDB返回内容"""
from iFinDPy import *
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print("=" * 60)
print("iFind补充测试")
print("=" * 60)

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
            ec = data.get('errorcode', '?') if hasattr(data, 'get') else '?'
            print(f"  ❌ '{query}' → 无数据(ec={ec})")
    except Exception as e:
        print(f"  ❌ '{query}' → {e}")

# EDB返回内容检查
print("\n>>> EDB返回内容检查 <<<\n")
try:
    data = THS_EDBQuery('M001620326', '2025-01-01', '2025-06-30')
    print(f"  类型: {type(data)}")
    if isinstance(data, dict):
        print(f"  keys: {list(data.keys())}")
        print(f"  errorcode: {data.get('errorcode', 'N/A')}")
        print(f"  errmsg: {data.get('errmsg', 'N/A')}")
        tables = data.get('tables', [])
        print(f"  tables数量: {len(tables)}")
        if tables:
            print(f"  EDB有数据!")
    else:
        print(f"  内容: {str(data)[:400]}")
except Exception as e:
    print(f"  EDB异常: {e}")

print("\n完成")
