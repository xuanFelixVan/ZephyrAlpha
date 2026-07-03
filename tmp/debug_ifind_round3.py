# [BLUEPRINT] N/A | tmp/debug_ifind_round3.py | §data-source-verification
# [MODULE] tmp.debug_ifind_round3
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

"""第三轮: 从配置文件获取正确代码格式 + 用当前日期测试。"""
from iFinDPy import *
import time, json, re, os
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f'登录: {r}')

# 1. 从OverseasMarket.xml获取海外市场代码后缀
print('\n=== 1. 海外市场代码后缀(OverseasMarket.xml) ===')
om_file = r'D:\同花顺Ifind金融终端api\THSDataInterface_Windows_20260227\THSDataInterface_Windows\bin\Tool\etc\OverseasMarket.xml'
if os.path.exists(om_file):
    for enc in ['gbk', 'utf-8', 'utf-16']:
        try:
            with open(om_file, 'r', encoding=enc) as f:
                content = f.read()
            break
        except:
            content = ''
    if content:
        # 提取市场代码后缀
        markets = re.findall(r'(?:market|suffix|code).*?["\']([A-Z]{2,5})["\']', content[:5000], re.I)
        print(f'  可能的后缀: {markets[:20]}')
        # 打印前500字符
        preview = content[:500].replace('\n', ' ')
        print(f'  预览: {preview[:300]}')

# 2. 从markets.xml获取市场信息
print('\n=== 2. 市场信息(markets.xml) ===')
mkt_file = r'D同花顺Ifind金融终端api\THSDataInterface_Windows_20260227\THSDataInterface_Windows\bin\Tool\etc\markets.xml'
mkt_file = r'D:\同花顺Ifind金融终端api\THSDataInterface_Windows_20260227\THSDataInterface_Windows\bin\Tool\etc\markets.xml'
if os.path.exists(mkt_file):
    for enc in ['gbk', 'utf-8', 'utf-16']:
        try:
            with open(mkt_file, 'r', encoding=enc) as f:
                content = f.read()
            break
        except:
            content = ''
    if content:
        # 提取所有market name和suffix
        entries = re.findall(r'<market\s+([^>]+)>', content)
        for e in entries[:30]:
            print(f'  {e}')

# 3. 用i问财查询期货/美股/港股的正确代码
print('\n=== 3. i问财查询期货主力合约 ===')
for query in ['沪铜期货主力合约', '沪铜主力', '铜期货合约']:
    data = THS_iwencai(query, 'stock')
    if isinstance(data, dict) and data.get('tables'):
        t = data['tables'][0]
        cols = list(t.get('table', {}).keys())
        print(f'  查询"{query}": 列={cols[:5]}')
        if '股票代码' in t.get('table', {}):
            codes = t['table']['股票代码'][:3]
            print(f'    代码: {codes}')
    time.sleep(0.3)

# 4. 用i问财查询美股代码
print('\n=== 4. i问财查询美股 ===')
data = THS_iwencai('美股AAPL苹果股票代码', 'stock')
if isinstance(data, dict) and data.get('tables'):
    t = data['tables'][0]
    cols = list(t.get('table', {}).keys())
    print(f'  列: {cols[:10]}')
    if '股票代码' in t.get('table', {}):
        print(f'  代码: {t["table"]["股票代码"][:5]}')

time.sleep(0.5)

# 5. 用i问财查询港股代码
print('\n=== 5. i问财查询港股 ===')
data = THS_iwencai('港股腾讯股票代码', 'stock')
if isinstance(data, dict) and data.get('tables'):
    t = data['tables'][0]
    cols = list(t.get('table', {}).keys())
    print(f'  列: {cols[:10]}')
    if '股票代码' in t.get('table', {}):
        print(f'  代码: {t["table"]["股票代码"][:5]}')

time.sleep(0.5)

# 6. 期货 - 用当前日期(2026年)的合约测试
print('\n=== 6. 期货(用2026年当前合约) ===')
# 今天是2026-07-02, 尝试2026年7月/8月合约
for code in ['CU2607.SHF', 'CU2608.SHF', 'CU2609.SHF', 'RB2610.SHF', 'RB2607.SHF']:
    data = THS_HistoryQuotes(code, 'open;high;low;close;volume',
        'Interval:D,CPS:1,fill:Previous', '2026-06-01', '2026-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        em = data.get('errmsg', '')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        if rows > 0:
            t = data['tables'][0]['table']
            print(f'  ✅ {code}: rows={rows}, close={t.get("close", [])[:2]}')
            break
        else:
            print(f'  ❌ {code}: ec={ec}, em={em[:60]}')
    time.sleep(0.3)

# 7. 估值数据 - 尝试不同参数格式
print('\n=== 7. 估值数据(尝试不同参数) ===')
# -209可能是参数格式问题
# BasicData参数格式: 每个指标用逗号分隔(日期,类型)
params_list = [
    ('ths_pe_stock;ths_pb_stock;ths_stock_short_name_stock', ''),
    ('ths_pe_stock;ths_pb_stock;ths_stock_short_name_stock', '2025-06-30;2025-06-30;'),
    ('ths_pe_stock;ths_pb_stock', '2025-06-30,100;2025-06-30,100'),
    ('ths_pe_stock;ths_pb_stock;ths_ps_stock', '20250630;20250630;20250630'),
    ('ths_pe_stock;ths_pb_stock;ths_ps_stock', '2025-06-30;2025-06-30;2025-06-30'),
]
for indicators, params in params_list:
    data = THS_BasicData('600000.SH', indicators, params)
    if isinstance(data, dict):
        ec = data.get('errorcode')
        if ec == 0 and data.get('tables'):
            t = data['tables'][0]
            tbl = t.get('table', {})
            has_data = any(v and v[0] is not None for v in tbl.values() if isinstance(v, list))
            print(f'  params="{params}": ec=0, has_data={has_data}, table={json.dumps(tbl, ensure_ascii=False)[:200]}')
        else:
            print(f'  params="{params}": ec={ec}')
    time.sleep(0.3)

# 8. 资金流向 - RealtimeQuotes获取实时资金流
print('\n=== 8. 资金流向(RealtimeQuotes实时) ===')
data = THS_RealtimeQuotes('600000.SH', 'inflow;outflow;netInflow;latest;changeRatio;amount;volume')
if isinstance(data, dict):
    ec = data.get('errorcode')
    if ec == 0 and data.get('tables'):
        t = data['tables'][0]
        tbl = t.get('table', {})
        print(f'  ec=0, table={json.dumps(tbl, ensure_ascii=False)[:300]}')
    else:
        print(f'  ec={ec}, em={data.get("errmsg", "")}')

THS_iFinDLogout()
print('\n已登出')
