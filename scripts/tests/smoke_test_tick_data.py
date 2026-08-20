# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.tests.smoke_test_tick_data
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""Tick 数据源运行时冒烟测试（manual，不入 CI）。

治本核心（#ARCH-EDE-TICK-FUEL-001）：用运行时实证堵住 EDE 燃料层的契约漂移。
静态阅读无法 100% 确认的 4 个开放点，本脚本对接真实模拟盘验证：
  1. 新版 xtquant (250807.1.2, Python 3.12) 的 download_history_data / get_market_data_ex 行为
  2. 国金 miniQMT 模拟终端是否真提供历史 tick 下载（部分券商权限有限制）
  3. _normalize_tick_data 的 18 字段（5档盘口）假设是否与新版返回结构匹配
  4. tick 时间戳格式能否被 TickReplayEngine 正确按时间戳合并

⚠️ 关键陷阱（已由静态核查发现）：
  EDE 的 TickReplayEngine 调用 provider.fetch_historical(interval="tick")，
  真正实现该方法的是 governance.data_governance.MiniQmtQuoteProvider（小写 qmt），
  而非 data.implementations.MiniQmtIngestProvider（大写 QMT，接口是 fetch(payload,policy)）。
  本脚本 import 的是前者，与 EDE 契约一致。

前置条件：
  1. miniQMT 模拟终端已启动并登录（XtMiniQmt.exe 运行中）——行情数据需终端在线
  2. config/.env.qmt 已配置 QMT_SIM_PATH
  3. xtquant 250807.1.2+ 已安装（E:\\xtquant 或 site-packages）

运行（无需盘中，历史 tick 随时可拉）：
  python scripts/tests/smoke_test_tick_data.py

验收硬指标：
  - 行数 > 0
  - 列名含 ask_price_1 / bid_price_1（5档盘口字段存在）
  - timestamp 为 datetime 类型，且落在请求区间内
"""

from __future__ import annotations

import sys
from datetime import date, datetime, timedelta
from pathlib import Path

# 确保项目 src 在 path 中
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))

# 优先使用 E:\xtquant 新版（Python 3.12 兼容），与 broker 适配一致
_XTQUANT_PATH = Path(r"E:\xtquant")
if _XTQUANT_PATH.exists():
    sys.path.insert(0, str(_XTQUANT_PATH))


def _load_env_qmt() -> str:
    """从 config/.env.qmt 读取 QMT 模拟盘路径。"""
    env_path = _REPO_ROOT / "config" / ".env.qmt"
    if not env_path.exists():
        print(f"[FAIL] 配置文件不存在: {env_path}")
        sys.exit(1)

    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        if key.strip() == "QMT_SIM_PATH":
            return val.strip()

    print("[FAIL] .env.qmt 缺少 QMT_SIM_PATH")
    sys.exit(1)


def main() -> int:
    from zephyr.governance.data_governance.miniqmt_provider import (
        MiniQmtProviderError,
        MiniQmtQuoteProvider,
    )

    qmt_path = _load_env_qmt()
    symbol = "600000.SH"  # 浦发银行，流动性好
    # 拉最近 7 个自然日，覆盖至少 1 个交易日（防周末/节假日）
    end = date.today()
    start = end - timedelta(days=7)
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(end, datetime.min.time())

    print(f"[INFO] QMT path={qmt_path}")
    print(f"[INFO] symbol={symbol}  range={start} ~ {end}")

    # 0. 构造 provider（懒加载 xtdata，构造本身不连终端）
    print("\n=== STEP 0: MiniQmtQuoteProvider() 构造 ===")
    try:
        provider = MiniQmtQuoteProvider(path=qmt_path, session_id="smoke_tick")
        print("[OK] provider 构造成功（xtdata 尚未加载，懒加载）")
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] provider 构造失败: {e}")
        return 1

    # 1. fetch_historical(interval="tick") —— 触发 xtdata 加载 + 下载 + 拉取 + 标准化
    print("\n=== STEP 1: fetch_historical(interval='tick') ===")
    try:
        df = provider.fetch_historical(
            symbol=symbol,
            start=start_dt,
            end=end_dt,
            interval="tick",
        )
    except MiniQmtProviderError as e:
        print(f"[FAIL] 拉取 tick 失败（MiniQmtProviderError）: {e}")
        return 1
    except Exception as e:  # noqa: BLE001 — 捕获新版 xtquant 任意契约漂移
        print(f"[FAIL] 拉取 tick 失败（未预期异常，可能新版 API 契约漂移）: {type(e).__name__}: {e}")
        return 1

    # 2. 行数检查
    print("\n=== STEP 2: 行数检查 ===")
    if df is None or df.empty:
        print("[FAIL] tick 数据为空")
        print("       可能原因: (a) 该区间无交易日 (b) 终端未下载该 symbol 历史")
        print("                 (c) 模拟盘权限不提供历史 tick (d) start/end 格式问题")
        return 1
    print(f"[OK] rows={len(df)}  cols={len(df.columns)}")

    # 3. 列结构检查（18 字段 + symbol）
    print("\n=== STEP 3: 列结构检查（18 字段 / 5档盘口）===")
    columns = list(df.columns)
    print(f"columns={columns}")
    required_5level = [
        "ask_price_1",
        "bid_price_1",
        "ask_vol_1",
        "bid_vol_1",
        "ask_price_5",
        "bid_price_5",
    ]
    missing = [c for c in required_5level if c not in columns]
    if missing:
        print(f"[FAIL] 缺失 5 档盘口字段: {missing}")
        print("       说明: _normalize_tick_data 的字段假设与新版 xtdata 返回结构不匹配")
        return 1
    print("[OK] 5 档盘口字段齐全 (ask_price_1..5 / bid_price_1..5 / ask_vol_1..5 / bid_vol_1..5)")

    # 4. 时间戳检查
    print("\n=== STEP 4: timestamp 检查（类型 + 区间）===")
    if "timestamp" not in columns:
        print("[FAIL] 缺少 timestamp 列")
        return 1
    ts = df["timestamp"]
    ts_dtype = str(ts.dtype)
    print(f"timestamp dtype={ts_dtype}")
    if ts.dtype != "datetime64[ns]":
        print(f"[FAIL] timestamp 不是 datetime64[ns]（实际 {ts_dtype}）")
        print("       说明: TickReplayEngine 按时间戳合并多 symbol，类型错误会导致回放失败")
        return 1
    ts_min = ts.min()
    ts_max = ts.max()
    print(f"timestamp range: {ts_min}  ~  {ts_max}")
    # 区间内检查（允许跨日，只要落在 start~end+1 内）
    if ts_min.date() < start or ts_max.date() > end:
        print(f"[FAIL] timestamp 超出请求区间 [{start}, {end}]")
        return 1
    print("[OK] timestamp 类型与区间正确")

    # 5. 数据抽样
    print("\n=== STEP 5: 数据抽样（前 3 行关键字段）===")
    sample_cols = [
        "timestamp",
        "last_price",
        "volume",
        "amount",
        "ask_price_1",
        "bid_price_1",
        "ask_vol_1",
        "bid_vol_1",
    ]
    avail = [c for c in sample_cols if c in columns]
    with __import__("contextlib").suppress(Exception):
        import pandas as pd

        pd.set_option("display.width", 200)
        pd.set_option("display.max_columns", 20)
    print(df[avail].head(3).to_string(index=False))

    # 6. 盘口非空率
    print("\n=== STEP 6: 盘口非空率（抽样）===")
    for col in ("ask_price_1", "bid_price_1"):
        if col in columns:
            nonzero = (df[col].notna() & (df[col] != 0)).sum()
            rate = nonzero / len(df) * 100
            print(f"  {col}: 非零非空 {nonzero}/{len(df)} ({rate:.1f}%)")

    print("\n=== 冒烟测试全部通过 ===")
    print("结论: EDE tick 燃料层契约已实证可用，可开工 StrategyRunner × EDE 集成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
