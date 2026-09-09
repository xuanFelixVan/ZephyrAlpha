# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.implementations.qmt_bridge_provider
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base
# [CONSUMERS] zephyr.data.scheduler (source=qmt_bridge 工厂路由/契约校验注册表)
# [STARTUP] manual
# [MATURITY] testing
# [INVARIANTS] 只增桥不删 miniqmt（迁移台账 §3）——本 Provider 注册为独立 source，任何 tasks.yaml 任务
#              的 source 切换必须走 9/17 收盘后窗口（迁移台账红线 1）；探活=桥文件族存在性+mtime 新鲜度
#              +HTTP 18901 /health 三通道；fetch 遵循基类错误契约（返回 FetchResult(error=...) 不抛异常）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 探活失败→health_check False；fetch 未实现 capability→FetchResult(error=NotImplementedError 语义)
# [TESTS] 手动冒烟：python -c "from zephyr.data.implementations.qmt_bridge_provider import QmtBridgeIngestProvider; p=QmtBridgeIngestProvider(); p.connect(); print(p.probe())"
# [A_module] module_id=MOD-L00-004 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""QMT 文件桥数据源 Provider（大QMT 沙箱三策略，miniQMT 9/18 退役替代，93 号备忘）。

定位（迁移台账 §3，2026-09-09 夜班）：tasks.yaml 全部任务仍挂 source=miniqmt，
本 Provider 只做"桥能力注册"——把 qmt_bridge 纳入 provider 工厂/健康检查/测速
体系，使 9/17 收盘后窗口的主源切换成为纯 YAML 变更（零新代码）。

三通道对应（93 号备忘 §12/§14，均已实盘验证）：
  - tick  : 沙箱 TICKDUMP3_v19 → E:\\qmt_bridge(_sim)\\ticks3.csv → 实时采集由
            tick_subscriber.BridgeTickSource 尾读承担（独立进程，不经本 Provider）。
            本 Provider 对 tick_data capability 返回零行成功结果（no-op 语义，
            防止 9/18 后误配任务造成双写）。
  - 下单  : HTTP 127.0.0.1:18901 POST /order（32ms）+ orders_sim.csv 文件兜底
            ——交易执行属 ex_core 域（qmt_file_bridge_broker），不在数据 Provider 职责内，
            仅作探活信号之一。
  - 行情  : QUOTE_V17 → quote.csv（29 列 5 档）。K 线族/指数取价等 capability 的
            桥通道映射待台账 §2.2 三选一方案裁定（a 沙箱扩 dump / b tick 聚合合成 /
            c akshare 兜底），裁定前 fetch 一律返回"未实现"错误结果。

环境分区铁律（93 备忘 §5-A）：sim=E:\\qmt_bridge_sim\\，real=E:\\qmt_bridge\\。
"""

from __future__ import annotations

import datetime
import socket
import time
from pathlib import Path
from typing import Final, Iterator
from zoneinfo import ZoneInfo

from zephyr.data.provider_base import (
    CapabilityContract,
    FetchPayload,
    FetchResult,
    IngestProviderBase,
    IngestProviderMeta,
)
from zephyr.shared.utils.time_utils import now_utc

# 与 BridgeTickSource.ENV_CONFIG 同源（ticks3.csv = v19 产出，#BRIDGE-WRONG-FILE 教训：
# 桥文件路径登记必须与当前沙箱策略产出文件同步升级）
_TICK_FILE: Final[dict[str, str]] = {
    "real": r"E:\qmt_bridge\ticks3.csv",
    "sim": r"E:\qmt_bridge_sim\ticks3.csv",
}

_QUOTE_FILE: Final[dict[str, str]] = {
    "real": r"E:\qmt_bridge\quote.csv",
    "sim": r"E:\qmt_bridge_sim\quote.csv",
}

# HTTP 桥（EXEC_V16.4 沙箱内，93 备忘 §12）
_HTTP_BRIDGE_HOST: Final[str] = "127.0.0.1"
_HTTP_BRIDGE_PORT: Final[int] = 18901

# 盘中文件新鲜度阈值（秒）——与 BridgeTickSource._STALE_WARN_S 同口径
_FRESH_SECONDS: Final[float] = 60.0


# 台账 §8.6 任务二（裁定③方案 b）：capability → (period, 目标表)
# 合成执行走 _call_synth 懒导入（ch_tick_kline 依赖 table_registry，不依赖本模块）
def _call_synth(period: str, start: str, end: str) -> int:
    from zephyr.data.implementations.ch_tick_kline import (
        synth_kline_from_1min,
        synth_tick_kline,
    )

    if period in ("1min", "5min"):
        return synth_tick_kline(period, start, end)
    return synth_kline_from_1min(period, start, end)


_KLINE_PERIOD_MAP: Final[dict[str, tuple[str, str]]] = {
    "kline_1min": ("1min", "c1_market.kline_1min"),
    "kline_5min": ("5min", "c1_market.kline_5min"),
    "kline_15min": ("15min", "c1_market.kline_15min"),
    "kline_30min": ("30min", "c1_market.kline_30min"),
    "kline_60min": ("60min", "c1_market.kline_60min"),
}


class QmtBridgeIngestProvider(IngestProviderBase):
    """QMT 文件桥数据源 Provider（骨架：桥文件族探活 + 逐 capability 映射）。

    9/18 主源切换窗口前仅作为"已注册可探活"的 source 存在；各 capability 的
    数据通道随台账 §2.2 方案裁定逐个点亮。
    """

    source_name: str = "qmt_bridge"

    meta: IngestProviderMeta = IngestProviderMeta(
        name="qmt_bridge",
        display_name="QMT 文件桥（大QMT 沙箱）",
        auth_type="anonymous",  # 文件/本机 HTTP，无认证
        requires_process=True,  # 依赖大QMT 终端 XtItClient.exe + 沙箱策略常驻
        thread_safety="shared",  # 纯文件尾读+socket，无进程内共享可变状态
        rate_limit_default=0,
        capabilities=[
            # 实时 tick 采集真身 = tick_subscriber.BridgeTickSource（93 备忘 §14，
            # 9/8 起 bridge 为唯一实时源）；此处注册仅为 source 语义完备——
            # scheduler 侧对 tick_data 拉取返回零行 no-op（防误配双写）
            CapabilityContract("tick_data", supports_symbols_null=True),
            # 台账 §8.6 任务二（裁定③方案 b）：tick→分钟K CH 内自拼——
            # 1/5min 从 tick_data 聚合（ch_tick_kline.synth_tick_kline），
            # 15/30/60min 从 kline_1min 二次合成（synth_kline_from_1min）。
            # 点亮 capability ≠ 切换任务主源（tasks.yaml source 字段零改动，红线 1）。
            CapabilityContract("kline_1min", supports_symbols_null=True),
            CapabilityContract("kline_5min", supports_symbols_null=True),
            CapabilityContract("kline_15min", supports_symbols_null=True),
            CapabilityContract("kline_30min", supports_symbols_null=True),
            CapabilityContract("kline_60min", supports_symbols_null=True),
        ],
        known_issues=[
            "依赖大QMT 终端（XtItClient.exe）+ 沙箱策略常驻（EXEC_V16.4/QUOTE_V17/TICKDUMP3_v19）",
            "quote 族/指数取价桥通道未实现——QUOTE_V17 并入评估见 93 §14.9（9/15 检查点）",
            "无历史回补能力（桥只产出实时流，历史靠 miniQMT 9/18 前囤货；分钟K 自 9/9 起随窗口累积）",
        ],
    )

    # ============== 生命周期方法 ==============

    def connect(self) -> None:
        """探活桥文件族（tick/quote 任一存在即就绪）。

        不要求 HTTP 桥在线——午休/收盘线程冻结是沙箱已知特性（93 备忘 §12.5），
        探活通道见 probe()。
        """
        tick_ok = Path(self._tick_path()).exists()
        quote_ok = Path(self._quote_path()).exists()
        if not (tick_ok or quote_ok):
            self._connected = False
            raise FileNotFoundError(
                f"桥文件族均不存在（ticks3={self._tick_path()} quote={self._quote_path()}）；"
                "QMT 沙箱策略未启动？见 93 号备忘 §14/迁移台账"
            )
        self._connected = True
        self._log.info(
            "QMT 文件桥连接就绪（tick_file=%s quote_file=%s）",
            tick_ok,
            quote_ok,
        )

    def health_check(self) -> bool:
        """探活：桥文件族存在性 + mtime 新鲜度（盘中窗口）/HTTP 18901 存活。

        判定语义（从宽，探活≠数据质量）：
        - tick 或 quote 桥文件存在即 True 的必要条件；均不存在 → False
        - 存在但 mtime 陈旧：交易时段内（09:15-15:00）视为 False（沙箱停摆可见），
          非交易时段视为 True（沙箱夜间冻结属已知特性）
        - HTTP 18901 存活作为加分信号但不一票否决（EXEC 策略可能单独重启中）
        """
        verdict = self.probe()
        return verdict["alive"]

    def disconnect(self) -> None:
        """断开：纯文件探活无连接可断，仅重置状态标记。"""
        self._connected = False

    # ============== 探活细节（source_health_check / speed_tester 共用语义） ==============

    def _tick_path(self) -> str:
        return _TICK_FILE.get(self._env(), _TICK_FILE["sim"])

    def _quote_path(self) -> str:
        return _QUOTE_FILE.get(self._env(), _QUOTE_FILE["sim"])

    @staticmethod
    def _env() -> str:
        """环境分区（sim/real）——与 tick_subscriber TICK_BRIDGE_ENV 同语义，默认 sim。"""
        import os

        return os.environ.get("TICK_BRIDGE_ENV", "sim")

    @staticmethod
    def _in_trading_window() -> bool:
        """是否在 A 股交易时段（09:15-15:00 北京时间，含集合竞价）——粗判即可，供探活口径。"""
        now_cn = now_utc().astimezone(ZoneInfo("Asia/Shanghai"))
        t = now_cn.time()
        return datetime.time(9, 15) <= t <= datetime.time(15, 0)

    def probe(self) -> dict:
        """桥全环节探活明细（健康检查/测速/前端共用语义）。

        Returns:
            dict: alive 总判定 / tick_file / quote_file（存在+mtime age_s）/ http（alive+ms）
        """

        def _file_state(path_str: str) -> dict:
            p = Path(path_str)
            if not p.exists():
                return {"path": path_str, "exists": False, "fresh": False}
            age_s = max(0.0, now_utc().timestamp() - p.stat().st_mtime)
            fresh = age_s <= _FRESH_SECONDS
            if not fresh and not self._in_trading_window():
                fresh = True  # 非交易时段沙箱冻结属已知特性，不判死
            return {"path": path_str, "exists": True, "age_s": round(age_s, 1), "fresh": fresh}

        tick = _file_state(self._tick_path())
        quote = _file_state(self._quote_path())
        http = self._probe_http()
        alive = (tick.get("exists") and tick.get("fresh", False)) or (
            quote.get("exists") and quote.get("fresh", False)
        )
        return {"alive": bool(alive), "tick_file": tick, "quote_file": quote, "http": http}

    @staticmethod
    def _probe_http(timeout: float = 2.0) -> dict:
        """HTTP 桥探活（GET /health，语义对齐 api_server._bridge_http_health）。"""
        t0 = time.perf_counter()
        try:
            with socket.create_connection((_HTTP_BRIDGE_HOST, _HTTP_BRIDGE_PORT), timeout=timeout) as s:
                s.sendall(b"GET /health HTTP/1.0\r\n\r\n")
                buf = b""
                while b"\r\n\r\n" not in buf:
                    c = s.recv(4096)
                    if not c:
                        break
                    buf += c
            ms = round((time.perf_counter() - t0) * 1000)
            body = buf.decode("utf-8", "ignore").split("\r\n\r\n", 1)[-1]
            return {"alive": bool(body), "ms": ms}
        except OSError as e:
            return {"alive": False, "detail": str(e)[:60], "ms": round((time.perf_counter() - t0) * 1000)}

    # ============== fetch 路由 ==============

    def fetch(self, payload: FetchPayload, policy) -> Iterator[FetchResult]:
        """按 capability 路由（骨架：tick_data no-op，其余未实现）。

        遵循基类错误契约：未实现的 capability 返回 FetchResult(error=...)，
        不抛异常（让上层决定告警/跳过）。
        """
        started = time.perf_counter()
        capability = (payload.extra or {}).get("capability")
        if capability == "tick_data":
            # 实时 tick 由 tick_subscriber BridgeTickSource 独立进程入库（93 备忘 §14）；
            # scheduler 侧拉取=零行成功 no-op，防止误配造成 CH 双写
            self._log.info("tick_data 桥通道=no-op（实时采集由 tick_subscriber 桥模式承担）")
            yield FetchResult(
                table=payload.table,
                columns=[],
                rows=[],
                last_key="",
                elapsed_sec=round(time.perf_counter() - started, 3),
            )
            return
        # 台账 §8.6 任务二（裁定③方案 b）：分钟K 族桥通道 = CH 内自拼
        if capability in _KLINE_PERIOD_MAP:
            period, table_hint = _KLINE_PERIOD_MAP[capability]
            start_str = payload.start.strftime("%Y-%m-%d")
            end_str = payload.end.strftime("%Y-%m-%d")
            try:
                n = _call_synth(period, start_str, end_str)
                self._log.info(
                    "桥通道分钟K合成完成: %s [%s~%s] 窗口内 %d bars（幂等 DELETE+INSERT）",
                    capability, start_str, end_str, n,
                )
                yield FetchResult(
                    table=table_hint,
                    columns=[],
                    rows=[],
                    last_key=end_str,
                    elapsed_sec=round(time.perf_counter() - started, 3),
                )
            except Exception as e:  # noqa: BLE001 — 错误契约：error 不抛
                yield FetchResult(
                    table=table_hint,
                    columns=[],
                    rows=[],
                    last_key=end_str,
                    elapsed_sec=round(time.perf_counter() - started, 3),
                    error=f"qmt_bridge {capability} 合成失败: {e}",
                )
            return
        # quote 族/指数取价等：待 QUOTE_V17 并入评估（93 §14.9，9/15 检查点）
        yield FetchResult(
            table=payload.table,
            columns=[],
            rows=[],
            last_key="",
            elapsed_sec=round(time.perf_counter() - started, 3),
            error=(
                f"NotImplementedError: qmt_bridge 源暂不支持 capability={capability}"
                "（quote 族待 QUOTE_V17 并入评估 93 §14.9）"
            ),
        )
