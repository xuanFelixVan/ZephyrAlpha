# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/test_free_sources/test_ifind.py | §data-source-verification
# [MODULE] tmp.test_ifind
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

"""测试iFind连接+1个API"""
# 不需要sys.path.append，.pth已安装
from iFinDPy import *
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

print("="*50)
print("1. iFind登录测试")
print("="*50)
r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f"登录结果: {r} (0=成功, -201=已登录)")

if r == 0 or r == -201:
    print("\n2. 测试日K线API (THS_HistoryQuotes)")
    data = THS_HistoryQuotes('600000.SH', 'open,high,low,close', 'Interval:D', '2025-06-01', '2025-06-30')
    df = THS_Trans2DataFrame(data)
    print(f"   日K线: {len(df)}行")
    if len(df) > 0:
        print(f"   列: {list(df.columns)}")
        print(f"   最新: {df.tail(1).to_dict('records')[0]}")
    
    print("\n3. 测试估值API (THS_BasicData)")
    df2 = THS_BasicData('600000.SH', 'ths_pe_stock,ths_pb_stock', '2025-06-30')
    print(f"   估值: {len(df2)}行 | {df2.to_dict('records')[0] if len(df2)>0 else '空'}")

print("\n" + "="*50)
print("iFind测试完毕")
