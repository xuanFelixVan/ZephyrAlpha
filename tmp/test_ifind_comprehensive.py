# [BLUEPRINT] N/A | tmp/test_ifind_comprehensive.py | §data-source-verification
# [MODULE] tmp.test_ifind_comprehensive
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

"""iFind全面测试: 美股/期货/港股/新闻/概念板块/情绪/行业/交易日历。"""
from iFinDPy import *
import time, json
import pandas as pd
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default
pd.set_option('display.max_columns', 50, 'display.width', 200)

r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f'登录: {r}')

results = {}

def test_api(name, func):
    """测试一个API并记录结果。"""
    print(f'\n{"=" * 80}')
    print(f'测试: {name}')
    try:
        data = func()
        if isinstance(data, dict):
            ec = data.get('errorcode', 'N/A')
            em = data.get('errmsg', '')
            if ec == 0 and data.get('tables'):
                t = data['tables'][0]
                tbl = t.get('table', {})
                if isinstance(tbl, dict):
                    rows = len(next(iter(tbl.values()), []))
                else:
                    rows = len(tbl)
                cols = list(tbl.keys()) if isinstance(tbl, dict) else []
                print(f'  ✅ ec=0, rows={rows}, cols={cols[:8]}')
                # 打印前2行
                if isinstance(tbl, dict) and rows > 0:
                    for c in cols[:5]:
                        print(f'    {c}: {tbl[c][:3]}')
                results[name] = f'✅ {rows}行, 列={cols[:5]}'
            elif ec == 0:
                print(f'  ⚠️ ec=0但无tables, data={json.dumps(data, ensure_ascii=False)[:200]}')
                results[name] = f'⚠️ ec=0无数据'
            else:
                print(f'  ❌ ec={ec}, em={em[:100]}')
                results[name] = f'❌ ec={ec} {em[:50]}'
        elif isinstance(data, pd.DataFrame):
            print(f'  ✅ DataFrame {len(data)}行, 列={list(data.columns)[:8]}')
            print(data.head(2).to_string())
            results[name] = f'✅ {len(data)}行'
        else:
            print(f'  返回: {str(data)[:200]}')
            results[name] = f'? {str(data)[:80]}'
    except Exception as e:
        print(f'  ❌ 异常: {e}')
        results[name] = f'❌ {e}'
    time.sleep(0.5)

# ============================================================
# 1. 美股 - 用THS_toTHSCODE转换代码格式
# ============================================================
test_api('美股代码转换(THS_toTHSCODE)', lambda: THS_toTHSCODE('AAPL', 'usstock'))

# 美股 - 尝试更多后缀格式
print('\n=== 美股代码格式穷举 ===')
us_suffixes = ['.OQ', '.OO', '.OQD', '.OOD', '.US', '.U', '.N', '.NDQ', '.NYC', '.OQ.N', '.OB']
for suf in us_suffixes:
    code = f'AAPL{suf}'
    data = THS_HistoryQuotes(code, 'open;close;volume', 'Interval:D,CPS:1,fill:Previous', '2026-06-01', '2026-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        if rows > 0:
            print(f'  ✅ {code}: {rows}行')
            break
    time.sleep(0.2)

# 2. 期货 - 用THS_DataPool获取期货合约列表
test_api('期货合约列表(THS_DataPool)', lambda: THS_DataPool('derict', 'CU', 'date:Y,thscode:Y'))

# 期货 - 尝试不同交易所后缀和当前合约
print('\n=== 期货代码格式穷举 ===')
# 今天是2026-07-02, 当前主力合约可能是2607/2608/2609
futures_codes = [
    'CU2607.SHF', 'CU2608.SHF', 'CU2609.SHF',
    'CU2607', 'CU2608',
    'rb2610.SHF', 'RB2610.SHF',
    'A2609.DCE', 'M2609.DCE',  # 大商所
    'MA607.CZC', 'TA607.CZC',  # 郑商所
    'IF2607.CFE', 'IC2607.CFE',  # 中金所
]
for code in futures_codes:
    data = THS_HistoryQuotes(code, 'open;close;volume', 'Interval:D,CPS:1,fill:Previous', '2026-06-25', '2026-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        em = data.get('errmsg', '')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        if rows > 0:
            t = data['tables'][0]['table']
            print(f'  ✅ {code}: {rows}行, close={t.get("close", [])[:2]}')
        else:
            print(f'  ❌ {code}: ec={ec} {em[:50]}')
    time.sleep(0.2)

# 3. 港股 - 尝试更多后缀
print('\n=== 港股代码格式穷举 ===')
hk_suffixes = ['.HK', '.HKEx', '.HKE', '.HKD', '.HH', '.G', '.HKEX', '.HKG']
for suf in hk_suffixes:
    code = f'00700{suf}'
    data = THS_HistoryQuotes(code, 'open;close;volume', 'Interval:D,CPS:1,fill:Previous', '2026-06-01', '2026-07-01')
    if isinstance(data, dict):
        ec = data.get('errorcode')
        rows = len(data.get('tables', [{}])[0].get('table', {}).get('time', [])) if data.get('tables') else 0
        if rows > 0:
            print(f'  ✅ {code}: {rows}行')
            break
    time.sleep(0.2)

# 4. 交易日历 - THS_DateQuery
test_api('交易日历(THS_DateQuery)', lambda: THS_DateQuery('SSE', 'Open', '2026-06-01', '2026-07-01'))

# 5. 同花顺概念板块 - THS_DataPool
test_api('同花顺概念板块(THS_DataPool block)', lambda: THS_DataPool('block', '2026-07-01;885301', 'date:Y,thscode:Y,security_name:Y'))

# 6. 同花顺行业板块 - THS_DataPool
test_api('同花顺行业指数成分股(THS_DataPool index)', lambda: THS_DataPool('index', '2026-07-01;881101.TI', 'date:Y,thscode:Y,security_name:Y'))

# 7. 新闻/事件 - THS_iEvent
test_api('事件查询(THS_iEvent)', lambda: THS_iEvent('600000.SH', '2025-06-01;2025-06-30;100', 'event:Y,date:Y,title:Y'))

# 8. 研究报告 - THS_iResearch
test_api('研究报告(THS_iResearch)', lambda: THS_iResearch('600000.SH', '2025-06-01;2025-06-30;100', 'date:Y,title:Y,researcher:Y'))

# 9. 情绪指标 - THS_DateSerial (同花顺情绪指标)
test_api('情绪指标(DateSerial)', lambda: THS_DateSerial('600000.SH',
    'ths_turnover_ratio_stock;ths_volume_ratio_stock;ths_amount_ratio_stock',
    '100;100;100', 'Days:Alldays,Fill:Previous,Interval:D', '2025-06-25', '2025-06-30'))

# 10. 实时估值 - THS_realTimeValuation
test_api('实时估值(THS_realTimeValuation)', lambda: THS_realTimeValuation('600000.SH', '', 'pe;pb;ps'))

# 11. 快照 - THS_Snapshot
test_api('快照(THS_Snapshot)', lambda: THS_Snapshot('600000.SH', 'open;high;low;close;volume;amount;pe;pb',
    'Interval:D,CPS:1,fill:Previous', '2025-06-30', '2025-06-30'))

# 12. 报告查询 - THS_ReportQuery
test_api('报告查询(THS_ReportQuery)', lambda: THS_ReportQuery('600000.SH', '', 'date:Y,title:Y,type:Y'))

# 13. 资金流向 - 用i问财批量查询
test_api('i问财-资金流向(THS_iwencai)', lambda: THS_iwencai('2025年6月30日主力资金净流入前10只股票', 'stock'))

# 14. 概念板块列表 - i问财
test_api('i问财-概念板块(THS_iwencai)', lambda: THS_iwencai('同花顺概念板块列表', 'stock'))

# 15. 涨停股票 - i问财
test_api('i问财-涨停股票(THS_iwencai)', lambda: THS_iwencai('今日涨停股票', 'stock'))

# 16. 数据统计 - THS_DataStatistics
test_api('数据统计(THS_DataStatistics)', lambda: THS_DataStatistics())

# ============================================================
# 汇总
# ============================================================
print('\n' + '=' * 80)
print('iFind全面测试结果汇总')
print('=' * 80)
for k, v in results.items():
    print(f'  {v[:6]} {k}')

THS_iFinDLogout()
print('\n已登出')
