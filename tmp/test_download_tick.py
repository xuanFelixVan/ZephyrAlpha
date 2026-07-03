"""下载历史Tick数据并查看盘口详情

测试目标:
  1. 下载000001.SZ最近几天的Tick数据
  2. 查看askPrice/bidPrice数组的实际内容（5档还是10档）
  3. 打印一条完整的Tick数据样本

使用方法:
  python tmp/test_download_tick.py
"""

from xtquant import xtdata
import datetime

print("=" * 60)
print("下载历史Tick数据并查看盘口详情")
print("=" * 60)

test_code = "000001.SZ"  # 平安银行

# ========== 步骤1: 下载历史Tick数据 ==========
print(f"\n[步骤1] 下载 {test_code} 最近3天的Tick数据...")

# 计算最近3天的日期
end_date = datetime.datetime.now().strftime("%Y%m%d")
start_date = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime("%Y%m%d")

print(f"  日期范围: {start_date} ~ {end_date}")

try:
    # 下载历史Tick数据
    xtdata.download_history_data(test_code, "tick", start_date, end_date)
    print(f"  ✅ 历史数据下载完成")
except Exception as e:
    print(f"  ⚠️ 下载提示: {e}")

# ========== 步骤2: 获取Tick数据 ==========
print(f"\n[步骤2] 获取Tick数据...")

try:
    tick_data = xtdata.get_market_data_ex(
        stock_list=[test_code],
        period="tick",
        start_time=start_date,
        end_time=end_date,
        count=10,  # 只取10条样本
    )

    if tick_data and test_code in tick_data:
        df = tick_data[test_code]
        print(f"  ✅ 获取到 {len(df)} 条Tick数据")

        if len(df) == 0:
            print("  ⚠️ 数据为空，可能历史数据未下载完成")
            print("  尝试获取最近1条...")
            tick_data = xtdata.get_market_data_ex(
                stock_list=[test_code],
                period="tick",
                count=1,
            )
            if tick_data and test_code in tick_data:
                df = tick_data[test_code]
                print(f"  获取到 {len(df)} 条")

        if len(df) > 0:
            # ========== 步骤3: 分析盘口字段 ==========
            print(f"\n[步骤3] 分析盘口字段...")

            latest = df.iloc[-1]
            print(f"\n  最新Tick时间: {latest['time']}")
            print(f"  最新价: {latest['lastPrice']}")
            print(f"  成交量: {latest['volume']}")

            # 检查askPrice/bidPrice数组
            ask_price = latest['askPrice']
            bid_price = latest['bidPrice']
            ask_vol = latest['askVol']
            bid_vol = latest['bidVol']

            print(f"\n  askPrice类型: {type(ask_price)}")
            print(f"  askPrice内容: {ask_price}")
            print(f"  bidPrice内容: {bid_price}")
            print(f"  askVol内容: {ask_vol}")
            print(f"  bidVol内容: {bid_vol}")

            # 判断档位数
            if hasattr(ask_price, '__len__'):
                ask_len = len(ask_price)
                bid_len = len(bid_price) if hasattr(bid_price, '__len__') else 0
                print(f"\n  📊 卖盘档位数: {ask_len}")
                print(f"  📊 买盘档位数: {bid_len}")

                if ask_len >= 10:
                    print(f"  ✅✅ Level-2十档盘口！API完全可用")
                elif ask_len >= 5:
                    print(f"  ✅ Level-1五档盘口！够用")
                else:
                    print(f"  ⚠️ 档位数异常: {ask_len}")

                # 打印详细盘口
                print(f"\n  📋 详细盘口（卖盘从高到低，买盘从高到低）:")
                print(f"  {'档位':<6} {'卖价':<12} {'卖量':<12} | {'买价':<12} {'买量':<12}")
                print(f"  {'-'*60}")

                max_levels = max(ask_len, bid_len)
                for i in range(max_levels):
                    ask_p = ask_price[i] if i < ask_len else "-"
                    ask_v = ask_vol[i] if i < ask_len and hasattr(ask_vol, '__len__') else "-"
                    bid_p = bid_price[i] if i < bid_len else "-"
                    bid_v = bid_vol[i] if i < bid_len and hasattr(bid_vol, '__len__') else "-"
                    print(f"  {i+1:<6} {str(ask_p):<12} {str(ask_v):<12} | {str(bid_p):<12} {str(bid_v):<12}")

            else:
                print(f"  askPrice不是数组: {ask_price}")

            # ========== 步骤4: 打印完整Tick字段 ==========
            print(f"\n[步骤4] 完整Tick字段列表:")
            for i, col in enumerate(df.columns):
                val = latest[col]
                val_str = str(val)
                if len(val_str) > 80:
                    val_str = val_str[:80] + "..."
                print(f"  {i+1:2d}. {col:<25} = {val_str}")

    else:
        print(f"  ❌ 未获取到数据")

except Exception as e:
    print(f"  ❌ 获取数据失败: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试完成")
