# [BLUEPRINT] N/A | tmp/debug_ifind_round2.py | §data-source-verification
# [MODULE] tmp.debug_ifind_round2
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

"""第二轮调试: 修复参数, 测试估值/期货/美股/港股/资金流向。"""
from iFinDPy import *
import time, json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f'登录: {r}')

# 1. 估值数据 - BasicData需要指定日期参数
print('\n=== 1. 估值数据(调整日期参数) ===')
# 格式: 指标;指标;指标  参数;参数;参数
# ths_pe_stock的参数: 日期,100(静态)
data = THS_BasicData('600000.SH',
    'ths_pe_stock;ths_pb_stock;ths_ps_stock;ths_pcf_stock_ttm;ths_dividend_ratio_stock',
    '2025-06-30,100;2025-06-30,100;2025-06-30,100;2025-06-30,100;2025-06-30,100')
if isinstance(data, dict):
    print(f'errorcode: {data.get("errorcode")}')
    if data.get('tables'):
        t = data['tables'][0]
        print(f'table: {json.dumps(t, ensure_ascii=False)[:500]}')

time.sleep(0.5)

# 2. 期货 - 使用当前主力合约
print('\n=== 2. 期货(当前主力合约) ===')
# 上期所主力: 用i问财查询
data = THS_iwencai('沪铜主力合约代码', 'stock')
if isinstance(data, dict) and data.get('tables'):
    t = data['tables'][0]
    cols = list(t.get('table', {}).keys())
    print(f'  i问财列名: {cols}')
    for c in cols:
        print(f'    {c}: {t["table"][c][:3]}')

time.sleep(0.5)

# 直接尝试期货主力合约代码格式
print('\n  尝试期货主力代码:')
for code in ['CU25M.SHF', 'CU9999.SHF', 'CU.SHF', 'cu2507.SHF', 'CU2507.SHF', 'RB2510.SHF', 'RB2510']:
    data = THS_HistoryQuotes(code, 'open;high;low;close;volume',
        'Interval:D,CPS:1,fill:Previous', '2025-06-01', '2025-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        if rows > 0:
            print(f'  ✅ {code}: rows={rows}')
            break
        else:
            print(f'  ❌ {code}: errorcode={ec}')
    time.sleep(0.2)

# 3. 美股 - 用i问财查询正确代码
print('\n=== 3. 美股(用i问财查询代码) ===')
data = THS_iwencai('苹果公司', 'stock')
if isinstance(data, dict) and data.get('tables'):
    t = data['tables'][0]
    cols = list(t.get('table', {}).keys())
    print(f'  i问财列名: {cols[:10]}')
    for c in cols[:3]:
        print(f'    {c}: {t["table"][c][:3]}')

time.sleep(0.5)

# 尝试美股代码格式
print('\n  尝试美股代码:')
for code in ['AAPL.OQ', 'AAPL.OQD', 'AAPL.OO', 'AAPL.OOD', 'AAPL.I', 'AAPL']:
    data = THS_HistoryQuotes(code, 'open;high;low;close;volume',
        'Interval:D,CPS:1,fill:Previous', '2025-06-01', '2025-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        if rows > 0:
            print(f'  ✅ {code}: rows={rows}')
            # 打印数据
            t = data['tables'][0]['table']
            print(f'    time: {t.get("time", [])[:3]}')
            print(f'    close: {t.get("close", [])[:3]}')
            break
        else:
            print(f'  ❌ {code}: errorcode={ec}')
    time.sleep(0.2)

# 4. 港股 - 用i问财查询正确代码
print('\n=== 4. 港股(用i问财查询代码) ===')
data = THS_iwencai('腾讯控股', 'stock')
if isinstance(data, dict) and data.get('tables'):
    t = data['tables'][0]
    cols = list(t.get('table', {}).keys())
    print(f'  i问财列名: {cols[:10]}')
    for c in cols[:3]:
        print(f'    {c}: {t["table"][c][:3]}')

time.sleep(0.5)

# 尝试港股代码格式
print('\n  尝试港股代码:')
for code in ['00700.HK', '00700.HKEx', '00700.HKE', '700.HK', '00700.HKD', '00700']:
    data = THS_HistoryQuotes(code, 'open;high;low;close;volume',
        'Interval:D,CPS:1,fill:Previous', '2025-06-01', '2025-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        if rows > 0:
            print(f'  ✅ {code}: rows={rows}')
            t = data['tables'][0]['table']
            print(f'    time: {t.get("time", [])[:3]}')
            print(f'    close: {t.get("close", [])[:3]}')
            break
        else:
            print(f'  ❌ {code}: errorcode={ec}')
    time.sleep(0.2)

# 5. 资金流向 - 用DateSerial获取历史
print('\n=== 5. 资金流向(用DateSerial获取历史) ===')
# 先用i问财查询资金流向的指标代码
data = THS_iwencai('600000.SH 近5天主力资金流向', 'stock')
if isinstance(data, dict) and data.get('tables'):
    t = data['tables'][0]
    cols = list(t.get('table', {}).keys())
    print(f'  i问财列名: {cols[:10]}')

time.sleep(0.5)

# 用DateSerial获取资金流向 - 尝试不同的指标代码
print('\n  尝试资金流向指标:')
indicators = [
    'ths_main_net_inflow_stock',
    'ths_main_inflow_stock',
    'ths_net_inflow_amount_stock',
    'ths_capital_flow_stock',
]
for ind in indicators:
    data = THS_DateSerial('600000.SH', ind, '100',
        'Days:Alldays,Fill:Previous,Interval:D', '2025-06-25', '2025-06-30')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        if ec == 0 and data.get('tables'):
            t = data['tables'][0]
            tbl = t.get('table', {}).get(ind, [])
            times = t.get('time', [])
            if tbl and any(v is not None for v in tbl):
                print(f'  ✅ {ind}: {len(tbl)}行, 示例值={tbl[:2]}')
                break
            else:
                print(f'  ⚠️ {ind}: {len(tbl)}行但全null')
        else:
            print(f'  ❌ {ind}: errorcode={ec}')
    time.sleep(0.3)

# 6. 5分钟K线 - 试用账号限制1年,测试近1个月内
print('\n=== 6. 5分钟K线(试用账号限1年,测试近1月) ===')
data = THS_HighFrequenceSequence('600000.SH', 'open;high;low;close;volume;amount',
    'CPS:no,baseDate:1900-01-01,MaxPoints:50000,Fill:Previous,Interval:5',
    '2025-06-30 09:30:00', '2025-06-30 15:00:00')
if isinstance(data, dict):
    ec = data.get('errorcode')
    em = data.get('errmsg', '')
    if data.get('tables'):
        t = data['tables'][0]
        tbl = t.get('table', {})
        rows = len(tbl.get('time', [])) if isinstance(tbl, dict) else 0
        print(f'  errorcode={ec}, rows={rows}, errmsg={em[:80]}')
        if rows > 0:
            print(f'  列名: {list(tbl.keys())}')
            print(f'  time: {tbl.get("time", [])[:3]}')
            print(f'  close: {tbl.get("close", [])[:3]}')
    else:
        print(f'  errorcode={ec}, errmsg={em[:100]}')

THS_iFinDLogout()
print('\n已登出')
