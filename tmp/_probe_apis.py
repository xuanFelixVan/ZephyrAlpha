"""探查各数据源 API 的实际返回结构，用于修复脚本。

测试项：
1. THS_DataPool 申万行业成分股（industry_class 错误：list index out of range）
2. THS_DataPool 指数成分股（index_constituent 无输出）
3. i问财 融资融券查询语法（margin_trading 返回空）
4. AKShare stock_profit_forecast_ths（analyst_forecast 0 行）
5. TickFlow klines end_time 参数（us_index 分页 bug）

用法：
    python _probe_apis.py             # 全部测试
    python _probe_apis.py --only 1    # 仅测试项 1
"""
import sys
import os
import json
import argparse

sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import setup_logging, load_env

log = setup_logging("probe_apis")


def pp(obj, max_len=2000):
    """pretty print，截断长输出。"""
    s = repr(obj) if not isinstance(obj, str) else obj
    if len(s) > max_len:
        s = s[:max_len] + f"... [truncated, total {len(s)} chars]"
    return s


def probe_ths_datapool_industry():
    """测试1: THS_DataPool 申万行业成分股。"""
    log.info("=" * 60)
    log.info("[测试1] THS_DataPool 申万行业成分股")
    log.info("=" * 60)
    from iFinDPy import THS_DataPool

    # 尝试多种参数组合
    tests = [
        # (desc, edb_type, params, indics)
        ("801010.SW date:Y,thscode:Y", "index", "2026-07-04;801010.SW",
         "date:Y,thscode:Y,security_name:Y"),
        ("801010.SW 不带日期", "index", ";801010.SW",
         "date:Y,thscode:Y,security_name:Y"),
        ("801010.TI", "index", "2026-07-04;801010.TI",
         "date:Y,thscode:Y,security_name:Y"),
        ("sw1sector 标识符", "sw1sector", "2026-07-04",
         "thscode:Y,security_name:Y"),
        ("板块成分股 sector", "sector", "2026-07-04;申万一级行业",
         "thscode:Y,security_name:Y"),
    ]
    for desc, et, params, indics in tests:
        log.info(f"--- 尝试: {desc} ---")
        try:
            data = THS_DataPool(et, params, indics)
            log.info(f"  type(data) = {type(data).__name__}")
            if hasattr(data, "get"):
                log.info(f"  keys = {list(data.keys())}")
                errcode = data.get("errorcode", "N/A")
                log.info(f"  errorcode = {errcode}")
                tables = data.get("tables", [])
                log.info(f"  len(tables) = {len(tables)}")
                if tables:
                    t0 = tables[0]
                    log.info(f"  tables[0] keys = {list(t0.keys()) if hasattr(t0, 'keys') else type(t0)}")
                    if hasattr(t0, "get"):
                        inner = t0.get("table", {})
                        log.info(f"  table keys = {list(inner.keys()) if hasattr(inner, 'keys') else type(inner)}")
                        for k, v in (inner.items() if hasattr(inner, "items") else []):
                            log.info(f"    {k}: type={type(v).__name__}, len={len(v) if hasattr(v, '__len__') else 'N/A'}, sample={pp(v[:3] if hasattr(v, '__getitem__') else v, 200)}")
                            if k == "THSCODE" or "code" in k.lower() or "thscode" in k.lower():
                                log.info(f"    [找到代码列] {k} = {pp(v[:5], 200)}")
                        # 成功就返回
                        if any("code" in k.lower() or "thscode" in k.lower() for k in (inner.keys() if hasattr(inner, "keys") else [])):
                            log.info(f"  ✓ 成功！参数组合: {et} | {params} | {indics}")
                            return (et, params, indics)
            else:
                log.info(f"  data = {pp(data, 500)}")
        except Exception as e:
            log.warning(f"  异常: {e}")
    log.error("✗ 所有参数组合都失败")
    return None


def probe_ths_datapool_index():
    """测试2: THS_DataPool 指数成分股。"""
    log.info("=" * 60)
    log.info("[测试2] THS_DataPool 指数成分股")
    log.info("=" * 60)
    from iFinDPy import THS_DataPool

    tests = [
        ("000300.SH date+thscode+name+weight", "index", "2026-07-04;000300.SH",
         "date:Y,thscode:Y,security_name:Y,weight:Y"),
        ("000300.SH 不带日期", "index", ";000300.SH",
         "date:Y,thscode:Y,security_name:Y,weight:Y"),
        ("000300.SH 只 thscode", "index", "2026-07-04;000300.SH",
         "thscode:Y"),
        ("000300.SH + hs300 标识", "index", "2026-07-04;hs300",
         "thscode:Y,security_name:Y,weight:Y"),
    ]
    for desc, et, params, indics in tests:
        log.info(f"--- 尝试: {desc} ---")
        try:
            data = THS_DataPool(et, params, indics)
            log.info(f"  type(data) = {type(data).__name__}")
            if hasattr(data, "get"):
                errcode = data.get("errorcode", "N/A")
                log.info(f"  errorcode = {errcode}")
                tables = data.get("tables", [])
                log.info(f"  len(tables) = {len(tables)}")
                if tables:
                    inner = tables[0].get("table", {})
                    log.info(f"  table keys = {list(inner.keys()) if hasattr(inner, 'keys') else type(inner)}")
                    for k, v in (inner.items() if hasattr(inner, "items") else []):
                        log.info(f"    {k}: len={len(v) if hasattr(v, '__len__') else 'N/A'}, sample={pp(v[:3] if hasattr(v, '__getitem__') else v, 200)}")
                    if inner:
                        log.info(f"  ✓ 成功！")
                        return (et, params, indics)
            else:
                log.info(f"  data = {pp(data, 500)}")
        except Exception as e:
            log.warning(f"  异常: {e}")
    return None


def probe_iwencai_margin():
    """测试3: i问财融资融券查询语法。"""
    log.info("=" * 60)
    log.info("[测试3] i问财 融资融券查询语法")
    log.info("=" * 60)
    from iFinDPy import THS_iwencai
    from _ds_common import iwencai_to_df

    # 注意："融资融券个股" 返回的是概念股列表（所属概念列），不是融资余额数据
    # 需要查带具体数值字段的查询
    queries = [
        "2026年6月 融资融券余额个股",
        "融资余额",
        "2026年6月 融资余额个股",
        "2026年6月 融资融券交易明细",
        "融资融券交易明细",
        "2026年6月30日 融资融券余额个股",
        "沪深A股融资融券",
        "2026年6月 两融余额个股",
        "融资融券标的股 融资余额",
    ]
    for q in queries:
        log.info(f"--- 查询: {q!r} ---")
        try:
            result = THS_iwencai(q, "stock")
            log.info(f"  type = {type(result).__name__}")
            if hasattr(result, "get"):
                errcode = result.get("errorcode", "N/A")
                log.info(f"  errorcode = {errcode}")
                tables = result.get("tables", [])
                log.info(f"  len(tables) = {len(tables)}")
                if tables:
                    inner = tables[0].get("table", {})
                    keys = list(inner.keys()) if hasattr(inner, "keys") else []
                    log.info(f"  table keys = {keys}")
                    # 检查行数
                    for k in keys:
                        v = inner.get(k)
                        if hasattr(v, "__len__"):
                            log.info(f"    {k}: len={len(v)}, sample={pp(v[:2], 150)}")
                            break
                    df = iwencai_to_df(result)
                    log.info(f"  → DataFrame 行数: {len(df)}, 列: {list(df.columns)[:8]}")
                    if len(df) > 0:
                        log.info(f"  ✓ 查询成功！")
                        return q
            else:
                log.info(f"  result = {pp(result, 500)}")
        except Exception as e:
            log.warning(f"  异常: {e}")
    log.error("✗ 所有查询都返回空")
    return None


def probe_akshare_forecast():
    """测试4: AKShare stock_profit_forecast_ths。"""
    log.info("=" * 60)
    log.info("[测试4] AKShare 分析师预期 stock_profit_forecast_ths")
    log.info("=" * 60)
    log.info("⚠️ 注意：AKShare 爬国内网站，必须断开 VPN！")
    try:
        import akshare as ak
        log.info(f"  akshare version: {ak.__version__}")
    except ImportError as e:
        log.error(f"  akshare 未安装: {e}")
        return None

    # 测试几只常见股票
    for sym in ["600000", "000001", "000858", "600519"]:
        log.info(f"--- 测试股票: {sym} ---")
        try:
            df = ak.stock_profit_forecast_ths(symbol=sym)
            if df is None:
                log.info(f"  返回 None")
                continue
            log.info(f"  type = {type(df).__name__}")
            if hasattr(df, "columns"):
                log.info(f"  columns = {list(df.columns)}")
                log.info(f"  shape = {df.shape}")
                if len(df) > 0:
                    log.info(f"  第一行 = {pp(df.iloc[0].to_dict(), 500)}")
                    log.info(f"  ✓ 成功！")
                    return sym
            else:
                log.info(f"  data = {pp(df, 500)}")
        except Exception as e:
            log.warning(f"  异常: {e}")
    log.error("✗ 所有股票都失败")
    log.info("提示：检查 1)VPN是否已断开 2)akshare版本是否过旧 3)API是否已变更")
    return None


def probe_tickflow_pagination():
    """测试5: TickFlow klines 分页参数。"""
    log.info("=" * 60)
    log.info("[测试5] TickFlow klines 分页参数")
    log.info("=" * 60)
    try:
        from tickflow import TickFlow
    except ImportError as e:
        log.error(f"  tickflow 未安装: {e}")
        return None

    tf = TickFlow.free()
    log.info("TickFlow 免费服务已初始化")

    # 测试1: 不带 end_time，count=10
    log.info("--- 测试1: count=10，不带 end_time ---")
    try:
        df1 = tf.klines.get("SPY.US", period="1d", count=10, as_dataframe=True)
        log.info(f"  shape = {df1.shape if df1 is not None else 'None'}")
        if df1 is not None and len(df1) > 0:
            log.info(f"  columns = {list(df1.columns)}")
            log.info(f"  最早 trade_date = {df1.iloc[0].get('trade_date', df1.iloc[0].get('timestamp'))}")
            log.info(f"  最新 trade_date = {df1.iloc[-1].get('trade_date', df1.iloc[-1].get('timestamp'))}")
    except Exception as e:
        log.warning(f"  异常: {e}")

    # 测试2: 带 end_time，倒序分页
    log.info("--- 测试2: count=10 + end_time='2024-01-01' ---")
    try:
        df2 = tf.klines.get("SPY.US", period="1d", count=10, end_time="2024-01-01", as_dataframe=True)
        log.info(f"  shape = {df2.shape if df2 is not None else 'None'}")
        if df2 is not None and len(df2) > 0:
            log.info(f"  最早 trade_date = {df2.iloc[0].get('trade_date', df2.iloc[0].get('timestamp'))}")
            log.info(f"  最新 trade_date = {df2.iloc[-1].get('trade_date', df2.iloc[-1].get('timestamp'))}")
            return "end_time"
    except Exception as e:
        log.warning(f"  异常: {e}")

    # 测试3: 看看 klines.get 的签名
    log.info("--- 测试3: 查看 klines.get 签名 ---")
    try:
        import inspect
        sig = inspect.signature(tf.klines.get)
        log.info(f"  signature = {sig}")
        log.info(f"  parameters = {dict(sig.parameters)}")
    except Exception as e:
        log.warning(f"  无法获取签名: {e}")

    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, choices=[1, 2, 3, 4, 5],
                    help="仅运行指定测试项")
    args = ap.parse_args()

    if not args.only or args.only == 1:
        load_env()
        from iFinDPy import THS_iFinDLogin
        import os
        r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
        if r != 0:
            log.error(f"iFind 登录失败: {r}")
        else:
            log.info("iFind 登录成功")
            probe_ths_datapool_industry()
            probe_ths_datapool_index()
            probe_iwencai_margin()

    if not args.only or args.only == 4:
        probe_akshare_forecast()

    if not args.only or args.only == 5:
        probe_tickflow_pagination()


if __name__ == "__main__":
    main()
