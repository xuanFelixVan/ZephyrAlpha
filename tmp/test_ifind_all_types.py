# [BLUEPRINT] N/A | tmp/test_ifind_all_types.py | §data-source-verification
# [MODULE] tmp.test_ifind_all_types
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

"""iFind全数据类型下载测试 - 每种类型下载一个样本验证可用性。"""
from iFinDPy import *
import pandas as pd
import time
import traceback
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

pd.set_option('display.max_columns', 50, 'display.width', 200)

# 登录
print('=' * 80)
print('登录iFind...')
r = THS_iFinDLogin(get_secret_or_default("IFIND_USERNAME"), get_secret_or_default("IFIND_PASSWORD"))
print(f'登录返回: {r} (0=成功, -201=已登录, 其他=失败)')
if r != 0 and r != -201:
    print('登录失败,终止测试')
    exit(1)
print('登录成功!')

results = {}

# ============================================================
# 1. 历史行情(日K线) - THS_HistoryQuotes
# ============================================================
print('\n' + '=' * 80)
print('测试1: 历史行情(日K线) - THS_HistoryQuotes')
try:
    data = THS_HistoryQuotes('600000.SH',
        'preClose,open,high,low,close,avgPrice,change,changeRatio,volume,turnoverRatio,amount,transactionAmount',
        'Interval:D,CPS:1,baseDate:1900-01-01,Currency:YSHB,fill:Previous',
        '2025-06-01', '2025-07-01')
    df = THS_Trans2DataFrame(data)
    print(f'  行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['日K线'] = f'✅ {len(df)}行'
except Exception as e:
    results['日K线'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 2. 历史行情(周K线/月K线)
# ============================================================
print('\n' + '=' * 80)
print('测试2: 历史行情(周K线) - THS_HistoryQuotes Interval:W')
try:
    data = THS_HistoryQuotes('600000.SH', 'open;high;low;close;volume;amount',
        'Interval:W,CPS:1,fill:Previous', '2025-06-01', '2025-07-01')
    df = THS_Trans2DataFrame(data)
    print(f'  周K线 行数: {len(df)}')
    print(df.head(3).to_string())
    results['周K线'] = f'✅ {len(df)}行'
except Exception as e:
    results['周K线'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 3. 高频序列(分钟K线) - THS_HighFrequenceSequence
# ============================================================
print('\n' + '=' * 80)
print('测试3: 高频序列(5分钟K线) - THS_HighFrequenceSequence')
try:
    data = THS_HighFrequenceSequence('600000.SH', 'open;high;low;close;volume;amount',
        'CPS:no,baseDate:1900-01-01,MaxPoints:50000,Fill:Previous,Interval:5',
        '2025-06-30 09:30:00', '2025-06-30 15:00:00')
    df = THS_Trans2DataFrame(data)
    print(f'  5分钟K线 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['5分钟K线'] = f'✅ {len(df)}行'
except Exception as e:
    results['5分钟K线'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 4. 基础数据(估值PE/PB) - THS_BasicData
# ============================================================
print('\n' + '=' * 80)
print('测试4: 基础数据(估值PE/PB) - THS_BasicData')
try:
    data = THS_BasicData('600000.SH',
        'ths_pe_stock;ths_pb_stock;ths_ps_stock;ths_pcf_stock;ths_stock_short_name_stock',
        ';;2025-06-30,100;2025-06-30,100;2025-06-30,100;2025-06-30,100;')
    df = THS_Trans2DataFrame(data)
    print(f'  估值数据 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head().to_string())
    results['估值数据'] = f'✅ {len(df)}行'
except Exception as e:
    results['估值数据'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 5. 日期序列(财务数据) - THS_DateSerial
# ============================================================
print('\n' + '=' * 80)
print('测试5: 日期序列(财务数据) - THS_DateSerial')
try:
    data = THS_DateSerial('600000.SH',
        'ths_roe_stock;ths_net_profit_is;ths_total_assets_bs',
        '100;100;100',
        'Days:Alldays,Fill:Previous,Interval:D',
        '2025-01-01', '2025-06-30')
    df = THS_Trans2DataFrame(data)
    print(f'  财务数据 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['财务数据'] = f'✅ {len(df)}行'
except Exception as e:
    results['财务数据'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 6. 资金流向 - THS_DateSerial (inflow/outflow指标)
# ============================================================
print('\n' + '=' * 80)
print('测试6: 资金流向 - THS_DateSerial')
try:
    data = THS_DateSerial('600000.SH',
        'ths_main_inflow_stock;ths_main_outflow_stock;ths_super_large_inflow_stock;ths_large_inflow_stock',
        '100;100;100;100',
        'Days:Alldays,Fill:Previous,Interval:D',
        '2025-06-01', '2025-06-30')
    df = THS_Trans2DataFrame(data)
    print(f'  资金流向 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['资金流向'] = f'✅ {len(df)}行'
except Exception as e:
    results['资金流向'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 7. EDB经济数据库(宏观) - THS_EDBQuery
# ============================================================
print('\n' + '=' * 80)
print('测试7: EDB经济数据库(宏观数据) - THS_EDBQuery')
try:
    # M001620326=CPI同比, M002822183=M2同比
    data = THS_EDBQuery('M001620326;M002822183', '2025-01-01', '2025-06-30')
    df = THS_Trans2DataFrame(data)
    print(f'  宏观数据 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['宏观数据'] = f'✅ {len(df)}行'
except Exception as e:
    results['宏观数据'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 8. 数据池(指数成分股) - THS_DataPool
# ============================================================
print('\n' + '=' * 80)
print('测试8: 数据池(沪深300成分股) - THS_DataPool')
try:
    data = THS_DataPool('index', '2025-06-30;000300.SH',
        'date:Y,thscode:Y,security_name:Y')
    df = THS_Trans2DataFrame(data)
    print(f'  沪深300成分股 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['指数成分股'] = f'✅ {len(df)}行'
except Exception as e:
    results['指数成分股'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 9. 期货数据 - THS_HistoryQuotes (期货代码)
# ============================================================
print('\n' + '=' * 80)
print('测试9: 期货行情 - THS_HistoryQuotes (期货代码)')
try:
    # IF主力合约, CU沪铜主力
    data = THS_HistoryQuotes('CU2502.SHF',
        'open;high;low;close;volume;amount;position',
        'Interval:D,CPS:1,fill:Previous',
        '2025-06-01', '2025-07-01')
    df = THS_Trans2DataFrame(data)
    print(f'  期货行情 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['期货行情'] = f'✅ {len(df)}行'
except Exception as e:
    results['期货行情'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 10. 美股数据 - THS_HistoryQuotes (美股代码)
# ============================================================
print('\n' + '=' * 80)
print('测试10: 美股行情 - THS_HistoryQuotes (美股代码)')
try:
    data = THS_HistoryQuotes('AAPL.OQ',
        'open;high;low;close;volume;amount',
        'Interval:D,CPS:1,fill:Previous',
        '2025-06-01', '2025-07-01')
    df = THS_Trans2DataFrame(data)
    print(f'  美股行情 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['美股行情'] = f'✅ {len(df)}行'
except Exception as e:
    results['美股行情'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 11. 港股数据 - THS_HistoryQuotes (港股代码)
# ============================================================
print('\n' + '=' * 80)
print('测试11: 港股行情 - THS_HistoryQuotes (港股代码)')
try:
    data = THS_HistoryQuotes('00700.HK',
        'open;high;low;close;volume;amount',
        'Interval:D,CPS:1,fill:Previous',
        '2025-06-01', '2025-07-01')
    df = THS_Trans2DataFrame(data)
    print(f'  港股行情 行数: {len(df)} | 列: {list(df.columns)}')
    print(df.head(3).to_string())
    results['港股行情'] = f'✅ {len(df)}行'
except Exception as e:
    results['港股行情'] = f'❌ {e}'
    print(f'  失败: {e}')

time.sleep(0.5)

# ============================================================
# 12. i问财(自然语言查询)
# ============================================================
print('\n' + '=' * 80)
print('测试12: i问财(自然语言查询) - THS_iwencai')
try:
    data = THS_iwencai('今日涨停股票', 'stock')
    if isinstance(data, dict):
        print(f'  i问财返回类型: dict, keys: {list(data.keys())[:5]}')
        if 'tables' in data:
            tbl = data['tables'][0] if data['tables'] else {}
            print(f'  表数据行数: {len(tbl.get("table", {}).get("thscode", []))}')
    else:
        print(f'  i问财返回: {str(data)[:200]}')
    results['i问财'] = '✅ 成功'
except Exception as e:
    results['i问财'] = f'❌ {e}'
    print(f'  失败: {e}')

# ============================================================
# 汇总
# ============================================================
print('\n' + '=' * 80)
print('测试结果汇总')
print('=' * 80)
for k, v in results.items():
    status = '✅' if v.startswith('✅') else '❌'
    print(f'  {status} {k}: {v}')

THS_iFinDLogout()
print('\n已登出')
