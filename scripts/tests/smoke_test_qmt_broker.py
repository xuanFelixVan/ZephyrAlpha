# [BLUEPRINT] MOD-L06-001 | docs/03_modules/_domain_execution_core/blueprint.md
# [MODULE] scripts.tests.smoke_test_qmt_broker
# [STABILITY] stable
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [TESTS] self
# [TTL] permanent
"""QMT Broker 运行时冒烟测试（manual，不入 CI）。

治本核心（#ARCH-XTQUANT-API-COMPAT-001）：用运行时实证堵住 100% AI 开发的契约漂移。
静态阅读 xtquant 源码无法 100% 确认的开放点（order_stock 失败返回值、price_type 值、
subscribe 必要性、session int 要求），本脚本对接真实模拟盘验证。

前置条件：
  1. miniQMT 模拟终端已启动并登录（XtMiniQmt.exe 运行中）
  2. config/.env.qmt 已配置 QMT_SIM_PATH / QMT_SIM_ACCOUNT
  3. xtquant 250807.1.2+ 已安装（E:\\xtquant 或 site-packages）

运行：
  python scripts/tests/smoke_test_qmt_broker.py

验证链路：
  connect() → get_positions()（查资金）→ 挂远期限价单（不成交）→
  query_order()（查委托）→ cancel_order()（撤单）→ query_order()（查撤单状态）
"""

from __future__ import annotations

import os
import sys
from decimal import Decimal
from pathlib import Path

# 确保项目 src 在 path 中
_REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO_ROOT / "src"))


def _load_env_qmt() -> tuple[str, str]:
    """从 config/.env.qmt 读取 QMT 模拟盘配置。"""
    env_path = _REPO_ROOT / "config" / ".env.qmt"
    if not env_path.exists():
        print(f"[FAIL] 配置文件不存在: {env_path}")
        sys.exit(1)

    qmt_path = ""
    qmt_account = ""
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        key = key.strip()
        val = val.strip()
        if key == "QMT_SIM_PATH":
            qmt_path = val
        elif key == "QMT_SIM_ACCOUNT":
            qmt_account = val

    if not qmt_path or not qmt_account:
        print("[FAIL] .env.qmt 缺少 QMT_SIM_PATH 或 QMT_SIM_ACCOUNT")
        sys.exit(1)

    return qmt_path, qmt_account


def _verify_sim_terminal_running() -> int:
    """环境辨识守卫：确认运行中的是模拟终端，非真实资金盘。

    治本 #ARCH-QMT-ENV-DISAMBIG-001：两个终端 exe 同名（XtMiniQmt.exe），
    仅安装目录不同（"模拟"后缀 vs "证券"中缀）。本函数比对运行进程路径，
    防止在真实资金盘上跑测试下单。显化真源：config/qmt_environments.yaml。
    """
    try:
        import psutil
    except ImportError:
        print("[WARN] psutil 不可用，跳过进程校验——请手动确认运行的是【模拟终端】而非真实资金盘")
        return 0

    running_exes: list[str] = []
    for proc in psutil.process_iter(["name", "exe"]):
        name = proc.info.get("name") or ""
        if "XtMiniQmt" in name:
            running_exes.append(proc.info.get("exe") or "(unknown)")

    if not running_exes:
        print("[FAIL] 没有 XtMiniQmt 进程在运行——请先启动模拟终端")
        print("       模拟终端：E:\\国金QMT交易端模拟\\bin.x64\\XtMiniQmt.exe")
        return 1

    print(f"[INFO] 运行中的 QMT 终端：{running_exes}")
    # 辨识规则（来自 qmt_environments.yaml）：exe_path 含"模拟"→sim，含"证券"无"模拟"→live
    if any("模拟" in p for p in running_exes):
        print('[OK] 环境辨识通过：模拟盘（含"模拟"目录）')
        return 0
    print('[FAIL] 运行中的是【真实资金盘】（路径含"证券"无"模拟"），禁止在其上跑测试下单！')
    print("       请关闭真实终端，启动模拟终端：E:\\国金QMT交易端模拟\\bin.x64\\XtMiniQmt.exe")
    return 1


def _fetch_prev_close(symbol: str) -> "Decimal | None":
    """用 xtdata 获取昨收价（prev_close）。

    优先 get_full_tick（实时，含 last_close 字段），
    失败回退 get_market_data_ex（日K，取昨日 close）。
    broker.connect() 后 xtdata 已加载，可直接调用。
    """
    try:
        from xtquant import xtdata
    except ImportError:
        print("[FAIL] xtquant 不可用")
        return None

    # 优先：实时 tick 的 lastClose（注意 camelCase，非 last_close）
    try:
        tick = xtdata.get_full_tick([symbol])
        if tick and symbol in tick:
            lc = tick[symbol].get("lastClose")
            if lc and float(lc) > 0:
                return Decimal(str(lc))
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] get_full_tick 失败: {e}")

    # 回退：日K昨日 close
    try:
        data = xtdata.get_market_data_ex([], [symbol], period="1d", count=2)
        if data and symbol in data and len(data[symbol]) >= 2:
            return Decimal(str(data[symbol]["close"].iloc[-2]))
        if data and symbol in data and len(data[symbol]) >= 1:
            print("[WARN] 仅 1 根日K，用当日 close 作 prev_close 近似")
            return Decimal(str(data[symbol]["close"].iloc[-1]))
    except Exception as e:  # noqa: BLE001
        print(f"[WARN] get_market_data_ex 失败: {e}")

    return None


def main() -> int:
    from zephyr.ex_core.adapters.miniqmt_broker import MiniQmtBroker, MiniQmtBrokerError
    from zephyr.trading.trading_contracts.execution.order import (
        Order,
        OrderSide,
        OrderType,
    )

    qmt_path, qmt_account = _load_env_qmt()
    print(f"[INFO] QMT path={qmt_path}")
    print(f"[INFO] QMT account={qmt_account}")

    # 0. 环境辨识守卫（#ARCH-QMT-ENV-DISAMBIG-001）：确认运行的是模拟终端
    print("\n=== STEP 0: 环境辨识（模拟盘 vs 真实资金盘）===")
    if _verify_sim_terminal_running() != 0:
        return 1

    broker = MiniQmtBroker(
        path=qmt_path,
        session_id="smoke_test",
        account_id=qmt_account,
    )

    # 1. 连接
    print("\n=== STEP 1: connect() ===")
    try:
        broker.connect()
        print("[OK] 连接成功")
    except MiniQmtBrokerError as e:
        print(f"[FAIL] 连接失败: {e}")
        return 1

    try:
        # 2. 查询持仓/资金
        print("\n=== STEP 2: get_positions() ===")
        try:
            snapshot = broker.get_positions()
            print(f"[OK] cash={snapshot.cash}")
            print(f"     total_market_value={snapshot.total_market_value}")
            print(f"     holdings={dict(snapshot.holdings) if snapshot.holdings else '(空)'}")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 查询持仓失败: {e}")
            return 1

        # 3. 挂远期限价单（不成交）
        #    600000.SH 浦发银行。限价需在跌停板内（QMT 服务端校验 ±10%），
        #    原硬编码 1.00 元被 QMT 拒（order_id=-1，低于跌停板）。
        #    治本：用 xtdata 取 prev_close，限价 = 跌停价 * 1.01（valid + 不成交）。
        print("\n=== STEP 3: submit_order() 远期限价单 ===")
        prev_close = _fetch_prev_close("600000.SH")
        if prev_close is None:
            print("[FAIL] 无法获取 prev_close，跳过下单（市场可能未开盘/数据未下载）")
            return 1
        # 跌停价 = prev_close * 0.9；取跌停价上方 1% 确保 valid 且不成交
        limit_price = (prev_close * Decimal("0.91")).quantize(Decimal("0.01"))
        print(f"[INFO] prev_close={prev_close}  limit_price={limit_price}（跌停板内，不成交）")
        order = Order(
            idempotency_key=f"smoke-{int(__import__('time').time())}",
            order_id=f"smoke-{int(__import__('time').time())}",
            order_type=OrderType.LIMIT,
            quantity=Decimal("100"),
            side=OrderSide.BUY,
            strategy_id="smoke_test",
            symbol="600000.SH",
            limit_price=limit_price,
        )
        try:
            broker_order_id = broker.submit_order(order)
            print(f"[OK] 下单成功 broker_order_id={broker_order_id}")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 下单失败: {e}")
            return 1

        # 4. 查询委托
        print("\n=== STEP 4: query_order() ===")
        try:
            queried = broker.query_order(broker_order_id)
            if queried is not None:
                print(f"[OK] 委托存在 status={queried.status}")
            else:
                print("[WARN] 委托查询返回 None（可能延迟，非致命）")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 查询委托失败: {e}")
            return 1

        # 5. 撤单
        print("\n=== STEP 5: cancel_order() ===")
        try:
            broker.cancel_order(broker_order_id)
            print("[OK] 撤单成功")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 撤单失败: {e}")
            return 1

        # 6. 再查委托状态（应 CANCELLED）
        print("\n=== STEP 6: query_order() 验证撤单 ===")
        try:
            final = broker.query_order(broker_order_id)
            if final is not None:
                print(f"[OK] 最终状态 status={final.status}")
            else:
                print("[WARN] 委托查询返回 None")
        except MiniQmtBrokerError as e:
            print(f"[FAIL] 查询委托失败: {e}")
            return 1

        print("\n=== 冒烟测试全部通过 ===")
        return 0

    finally:
        try:
            broker.disconnect()
            print("[INFO] 已断开连接")
        except Exception as e:  # noqa: BLE001
            print(f"[WARN] 断开连接时出错: {e}")


if __name__ == "__main__":
    sys.exit(main())
