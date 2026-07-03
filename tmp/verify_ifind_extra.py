# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/verify_ifind_extra.py | §data-source-verification
# [MODULE] tmp.verify_ifind_extra
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

"""iFind待验证项测试 + i问财能力测试"""
from iFinDPy import *
import traceback
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f"登录结果: {r} (0=成功, -201=已登录)")
print("=" * 70)


def test_iwencai(name, query):
    """测试i问财查询"""
    try:
        data = THS_iwencai(query, 'stock')
        if data and 'tables' in data and len(data['tables']) > 0:
            table = data['tables'][0].get('table', {})
            if table:
                first_key = list(table.keys())[0]
                val = table[first_key]
                rows = len(val) if isinstance(val, list) else 1
                fields = list(table.keys())
                print(f"[{name}] ✅ 成功 | {rows}行 | 字段: {fields[:6]}")
                return True, rows
            else:
                print(f"[{name}] ⚠️ table为空 | 查询: '{query}'")
                return False, 0
        else:
            err = str(data)[:300] if data else "None"
            print(f"[{name}] ❌ 无数据 | 查询: '{query}' | 返回: {err}")
            return False, 0
    except Exception as e:
        print(f"[{name}] ❌ 异常: {e} | 查询: '{query}'")
        return False, 0


# === 待验证项（需求清单中的⚠️项）===
print("\n>>> 待验证项测试 <<<\n")

test_iwencai('龙虎榜', '2025年6月30日龙虎榜个股')
test_iwencai('融资融券', '2025年6月融资融券余额前10只股票')
test_iwencai('大宗交易', '2025年6月大宗交易个股')
test_iwencai('沪深港通-北向资金', '2025年6月北向资金净流入前10只股票')
test_iwencai('限售解禁', '2025年7月限售解禁个股')
test_iwencai('审计意见', '600000.SH 2024年审计意见')

# === i问财额外能力测试 ===
print("\n>>> i问财额外能力测试 <<<\n")

test_iwencai('涨停股', '2025年6月30日涨停股票')
test_iwencai('跌停股', '2025年6月30日跌停股票')
test_iwencai('ST股列表', 'ST股票列表')
test_iwencai('新股上市', '2025年6月新股上市')
test_iwencai('研报评级', '600000.SH 研报评级')
test_iwencai('股东人数', '600000.SH 股东人数')
test_iwencai('每股收益', '600000.SH 每股收益')
test_iwencai('机构持仓', '600000.SH 机构持仓')
test_iwencai('业绩预告', '600000.SH 业绩预告')
test_iwencai('回购', '2025年6月回购股票')
test_iwencai('增减持', '2025年6月高管增减持')
test_iwencai('分红', '600000.SH 分红')

# === EDB配额测试 ===
print("\n>>> EDB配额测试 <<<\n")
try:
    data = THS_EDBQuery('M001620326', '2025-01-01', '2025-06-30')
    if hasattr(data, 'ErrorCode'):
        ec = data.ErrorCode
        if ec == 0:
            print(f"EDB: ✅ 成功 (配额已恢复)")
        else:
            print(f"EDB: ❌ errorcode={ec} (配额限制中)")
    else:
        print(f"EDB: 返回类型={type(data)}")
except Exception as e:
    print(f"EDB: ❌ {e}")

print("\n" + "=" * 70)
print("验证完成")
