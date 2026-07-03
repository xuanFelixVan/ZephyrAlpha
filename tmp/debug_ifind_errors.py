# [BLUEPRINT] N/A | tmp/debug_ifind_errors.py | §data-source-verification
# [MODULE] tmp.debug_ifind_errors
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

"""调试iFind返回0行的接口: 检查原始errorcode和errmsg。"""
from iFinDPy import *
import time
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f'登录: {r}')

# 1. 5分钟K线 - 检查原始返回
print('\n=== 5分钟K线原始返回 ===')
data = THS_HighFrequenceSequence('600000.SH', 'open;high;low;close;volume;amount',
    'CPS:no,baseDate:1900-01-01,MaxPoints:50000,Fill:Previous,Interval:5',
    '2025-06-30 09:30:00', '2025-06-30 15:00:00')
if isinstance(data, dict):
    print(f'errorcode: {data.get("errorcode")}')
    print(f'errmsg: {data.get("errmsg")}')
    if 'tables' in data and data['tables']:
        t = data['tables'][0]
        print(f'table keys: {list(t.keys())}')
        print(f'table info: {json.dumps(t, ensure_ascii=False)[:500]}')
else:
    print(f'原始返回: {str(data)[:500]}')

time.sleep(0.5)

# 2. 估值数据 - 检查原始返回
print('\n=== 估值数据原始返回 ===')
data = THS_BasicData('600000.SH',
    'ths_pe_stock;ths_pb_stock;ths_stock_short_name_stock',
    ';;')
if isinstance(data, dict):
    print(f'errorcode: {data.get("errorcode")}')
    print(f'errmsg: {data.get("errmsg")}')
    if 'tables' in data and data['tables']:
        t = data['tables'][0]
        print(f'table: {json.dumps(t, ensure_ascii=False)[:500]}')
else:
    print(f'原始返回: {str(data)[:500]}')

time.sleep(0.5)

# 3. 财务数据 - 简化指标
print('\n=== 财务数据原始返回(简化) ===')
data = THS_DateSerial('600000.SH', 'ths_close_price_stock', '100',
    'Days:Alldays,Fill:Previous,Interval:D', '2025-06-01', '2025-06-30')
if isinstance(data, dict):
    print(f'errorcode: {data.get("errorcode")}')
    print(f'errmsg: {data.get("errmsg")}')
    if 'tables' in data and data['tables']:
        t = data['tables'][0]
        print(f'table: {json.dumps(t, ensure_ascii=False)[:500]}')
else:
    print(f'原始返回: {str(data)[:500]}')

time.sleep(0.5)

# 4. EDB - 尝试不同的指标代码
print('\n=== EDB宏观数据原始返回 ===')
# 尝试多个EDB指标代码
data = THS_EDBQuery('M001620326', '2025-01-01', '2025-06-30')
if isinstance(data, dict):
    print(f'errorcode: {data.get("errorcode")}')
    print(f'errmsg: {data.get("errmsg")}')
    if 'tables' in data and data['tables']:
        t = data['tables'][0]
        print(f'table: {json.dumps(t, ensure_ascii=False)[:500]}')
else:
    print(f'原始返回: {str(data)[:500]}')

time.sleep(0.5)

# 5. 期货 - 尝试不同代码格式
print('\n=== 期货(尝试不同代码格式) ===')
for code in ['CU2502.SHF', 'CU2502', 'IF2502.CFE', 'IF2502', 'rb2501.SHF', 'RB2501.SHF']:
    data = THS_HistoryQuotes(code, 'open;high;low;close;volume',
        'Interval:D,CPS:1,fill:Previous', '2025-06-01', '2025-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        em = data.get('errmsg', '')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        print(f'  {code}: errorcode={ec}, rows={rows}, errmsg={em[:80]}')
    else:
        print(f'  {code}: {str(data)[:100]}')
    time.sleep(0.3)

# 6. 美股 - 尝试不同代码格式
print('\n=== 美股(尝试不同代码格式) ===')
for code in ['AAPL.OQ', 'AAPL.OO', 'AAPL.US', 'AAPL.OQD', 'AAPL']:
    data = THS_HistoryQuotes(code, 'open;high;low;close;volume',
        'Interval:D,CPS:1,fill:Previous', '2025-06-01', '2025-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        em = data.get('errmsg', '')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        print(f'  {code}: errorcode={ec}, rows={rows}, errmsg={em[:80]}')
    else:
        print(f'  {code}: {str(data)[:100]}')
    time.sleep(0.3)

# 7. 港股 - 尝试不同代码格式
print('\n=== 港股(尝试不同代码格式) ===')
for code in ['00700.HK', '00700.HKEx', '00700', '700.HK', '00700.HKE']:
    data = THS_HistoryQuotes(code, 'open;high;low;close;volume',
        'Interval:D,CPS:1,fill:Previous', '2025-06-01', '2025-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        em = data.get('errmsg', '')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        print(f'  {code}: errorcode={ec}, rows={rows}, errmsg={em[:80]}')
    else:
        print(f'  {code}: {str(data)[:100]}')
    time.sleep(0.3)

# 8. 资金流向 - 尝试i问财查询指标名称
print('\n=== 资金流向(尝试i问财获取正确指标名) ===')
data = THS_iwencai('600000.SH 主力资金流向', 'stock')
if isinstance(data, dict):
    print(f'errorcode: {data.get("errorcode")}')
    print(f'errmsg: {data.get("errmsg")}')
    if data.get('tables'):
        t = data['tables'][0]
        cols = list(t.get('table', {}).keys()) if isinstance(t.get('table'), dict) else []
        print(f'  列名: {cols[:10]}')
        for c in cols[:5]:
            vals = t['table'][c]
            print(f'    {c}: {vals[:3]}')
    print()

THS_iFinDLogout()
print('已登出')
