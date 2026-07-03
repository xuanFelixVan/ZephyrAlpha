"""MiniQMT Level-2 API 权限测试脚本

测试目标:
  1. 连接MiniQMT终端
  2. 测试Tick数据获取（Level-1）
  3. 测试Level-2盘口数据获取（十档买卖挂单）
  4. 测试实时订阅能力

使用方法:
  1. 先登录MiniQMT终端（保持运行）
  2. 运行: python tmp/test_miniqumt_l2_api.py
"""

import sys
import time
from datetime import datetime

print("=" * 60)
print("MiniQMT Level-2 API 权限测试")
print("=" * 60)

# ========== 步骤1: 测试xtquant导入 ==========
print("\n[步骤1] 测试xtquant导入...")
try:
    from xtquant import xtdata, xttrader
    print("  ✅ xtquant导入成功")
    print(f"  xtdata版本: {getattr(xtdata, '__version__', '未知')}")
except ImportError as e:
    print(f"  ❌ xtquant导入失败: {e}")
    print("  解决: pip install xtquant")
    sys.exit(1)

# ========== 步骤2: 测试连接MiniQMT ==========
print("\n[步骤2] 测试连接MiniQMT终端...")
try:
    # 尝试获取行情数据（不需要登录交易，只需MiniQMT终端运行）
    test_code = "000001.SZ"  # 平安银行
    ticks = xtdata.get_market_data_ex(
        stock_list=[test_code],
        period="tick",
        count=1,
    )
    if ticks and test_code in ticks:
        print(f"  ✅ MiniQMT连接成功")
        print(f"  获取到 {test_code} 的Tick数据")
    else:
        print("  ⚠️ 连接成功但无数据，可能MiniQMT未下载历史数据")
except Exception as e:
    print(f"  ❌ 连接失败: {e}")
    print("  解决: 确保MiniQMT终端已登录并运行")
    sys.exit(1)

# ========== 步骤3: 测试Tick数据（Level-1） ==========
print("\n[步骤3] 测试Tick数据获取（Level-1）...")
try:
    tick_data = xtdata.get_market_data_ex(
        stock_list=[test_code],
        period="tick",
        count=5,
    )
    if tick_data and test_code in tick_data:
        df = tick_data[test_code]
        print(f"  ✅ Tick数据获取成功，共 {len(df)} 条")
        print(f"  最新Tick字段: {list(df.columns)}")
        print(f"  最新一条:")
        print(df.tail(1).to_string())
    else:
        print("  ❌ Tick数据为空")
except Exception as e:
    print(f"  ❌ Tick数据获取失败: {e}")

# ========== 步骤4: 测试Level-2盘口数据（关键！） ==========
print("\n[步骤4] 测试Level-2盘口数据（关键测试）...")
try:
    # Level-2数据通常通过get_market_data_ex的tick周期获取
    # 如果权限开通，tick数据中会包含 ten_buy / ten_sell 等十档字段
    tick_data = xtdata.get_market_data_ex(
        stock_list=[test_code],
        period="tick",
        count=10,
    )

    if tick_data and test_code in tick_data:
        df = tick_data[test_code]
        columns = list(df.columns)

        # 检查是否有Level-2字段
        l2_fields = [c for c in columns if 'buy' in c.lower() or 'sell' in c.lower() or 'bid' in c.lower() or 'ask' in c.lower()]
        ten_buy_fields = [c for c in columns if 'ten_buy' in c.lower() or 'buy_price' in c.lower()]
        ten_sell_fields = [c for c in columns if 'ten_sell' in c.lower() or 'sell_price' in c.lower()]

        print(f"  Tick数据字段: {columns}")

        if l2_fields:
            print(f"  ✅ 发现盘口相关字段: {l2_fields}")
            if ten_buy_fields or ten_sell_fields:
                print(f"  ✅✅ Level-2十档盘口API可用！")
                print(f"     买档字段: {ten_buy_fields}")
                print(f"     卖档字段: {ten_sell_fields}")
            else:
                print(f"  ⚠️ 有盘口字段但可能只是五档（Level-1）")
        else:
            print(f"  ❌ 未发现Level-2盘口字段")
            print(f"  可能原因: Level-2权限未开通，或数据未下载")

        # 打印最新一条数据的盘口
        if len(df) > 0:
            latest = df.iloc[-1]
            print(f"\n  最新Tick盘口数据:")
            for col in columns:
                if 'buy' in col.lower() or 'sell' in col.lower() or 'price' in col.lower() or 'vol' in col.lower():
                    print(f"    {col}: {latest[col]}")

except Exception as e:
    print(f"  ❌ Level-2数据获取失败: {e}")

# ========== 步骤5: 测试实时订阅能力 ==========
print("\n[步骤5] 测试实时Tick订阅能力...")
try:
    received_data = []

    def on_tick(data):
        received_data.append(data)
        print(f"  收到Tick: {data}")

    # 尝试订阅实时Tick
    xtdata.subscribe_quote(test_code, period="tick", callback=on_tick)
    print(f"  ✅ 订阅成功，等待3秒接收数据...")

    time.sleep(3)

    if received_data:
        print(f"  ✅✅ 收到 {len(received_data)} 条实时Tick")
        print(f"  实时Tick数据示例: {received_data[0]}")
    else:
        print(f"  ⚠️ 3秒内未收到实时数据（可能非交易时段）")

    # 取消订阅
    xtdata.unsubscribe_quote(test_code, period="tick")

except Exception as e:
    print(f"  ❌ 实时订阅失败: {e}")

# ========== 步骤6: 测试交易接口（可选） ==========
print("\n[步骤6] 测试交易接口连接（不会实际下单）...")
try:
    # 注意：这里只测试连接，不会下单
    # 需要填写你的miniQMT路径和session_id
    print("  ⚠️ 交易接口测试需要手动配置路径，跳过")
    print("  如需测试交易接口，请参考xttrader文档")
except Exception as e:
    print(f"  ❌ 交易接口测试失败: {e}")

# ========== 总结 ==========
print("\n" + "=" * 60)
print("测试总结")
print("=" * 60)
print("""
关键判断:
  1. 如果步骤4显示 "Level-2十档盘口API可用" → 你的Level-2 API权限已开通
  2. 如果步骤4显示 "未发现Level-2盘口字段" → 需要联系客户经理开通Level-2 API权限
  3. 如果步骤5收到实时Tick → 实时订阅能力正常

下一步:
  - 将测试结果截图发给客户经理确认权限
  - 如果Level-2 API可用，我们就可以开始设计盘口策略架构
  - 如果不可用，需要先开通权限或换方案
""")

print("测试完成时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
