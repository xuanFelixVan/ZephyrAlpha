# [A_module] module_id=MOD-INF-OPS-ALERT-FEED | layer=module | stability=evolving | safety=M | ai_autonomy=ai_modifiable
# [BLUEPRINT] MOD-INF-OPS-ALERT-FEED | docs/03_modules/_domain_infrastructure_operations/ops_alert_feed/blueprint.md | §
# [MODULE] zephyr.infrastructure.system_telemetry.alerts.ops_alert_feed
# [INVARIANTS] 通知必落盘 JSONL（进程重启不丢）; 同 dedup key 静默窗口内只刷新不重复; probe 异常 fail-safe 不抛出; 板目录可注入（测试隔离禁写生产 .runtime）
# [MODIFY-GUARD] config/alert_rules.yaml; config/resource_optimization.yaml（ops_alerting.project_rss_alert_gb=RSS 兜底线数值真源）; src/zephyr/frontend/dashboard/api_server.py（/api/ops-notifications + 探针线程段）
# [CONSUMERS] src/zephyr/frontend/dashboard/api_server.py（告警段 30s 探针线程 + /api/ops-notifications 端点）; tests/frontend/test_ops_alert_feed.py
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] OSError; yaml.YAMLError
# [TESTS] tests/frontend/test_ops_alert_feed.py
# [TTL] permanent

"""OpsAlertFeed — 运营告警供给线（治理战役 A2，2026-09-16）。

背景（治理挖矿地图 §4 发现 3）：config/alert_rules.yaml 的 ALERT-SYS-002
（OOM>8GB critical）自 2026-05 起无人生产 ``system.memory_rss_bytes`` 指标，
facade 定时 evaluate("__scheduled__") 是空转占位——规则引擎在、触发链断。
2026-09-15 裁定删除飞书/SMTP 通道后，通知唯一出口=前端 promotion 页。

本模块补上供给线，四段：

1. ``probe_project_rss_bytes`` — 项目衍生进程 RSS 探针（psutil）：
   当前进程树（self+全部后代）∪ cmdline/exe 引用仓根路径的进程。
   8GB 线语义=项目自身内存即将失控（9-15 事故：9 孤儿 llama-server ≈12GB）；
   该绝对值在代码里零副本——规则条件真源=config/alert_rules.yaml，GiB 口径登记与
   规则缺席兜底真源=config/resource_optimization.yaml ops_alerting.project_rss_alert_gb
   （排班表 v2 §2.3 C-1⑤ 消硬编码）。
2. ``OpsAlertFeed.publish/list_active`` — 通知板（JSONL 落盘
   ``.runtime/ops_notifications/notifications.jsonl``，safe_write_text CAS 写）：
   同 dedup key 静默窗口内只刷新 count/last_seen 不重复发布；resolve 语义打
   resolved_at 时间戳（前端灰显近期已解除项）。
3. ``OpsAlertFeed.tick`` — 一个监测周期：探针取值 → 按规则评估（复用
   AlertSubsystem._check_condition 的条件解析，零复制语义）→ critical 触发即
   publish（静默窗口取规则 silence_window）→ 上一周期仍有活动 OOM 项且本周期
   回落阈值*0.9（滞回）→ resolve。
4. ``OpsAlertFeed.tick_survival`` / ``probe_survival_status`` — 生存线 KPI 供给
   （ALERT-KPI-001/002，2026-09-16 清偿"规则+通道+UI 齐、独缺度量"断链）：
   只读净值序列（c1_market.account_nav_daily）→ SurvivalInput →
   ``zephyr.risk.core.survival_line_monitor.evaluate_survival_line`` → 状态
   ok/survival_breach/failure 即 ``kpi.survival_line.status`` 指标值。
   日频指标按规则 silence_window 节奏复评（30s tick 不复查 CH）；输入缺席/样本
   不足/判定异常 = **不产出该指标 + loud warning**（绝不兜底成 ok，也绝不炸循环）。

api_server 侧接线（告警段）：模块级 daemon 线程 30s 一 tick + 只读端点
``GET /api/ops-notifications``；前端 promotion 页横幅轮询该端点。

边界：本模块不投递任何外部通道（飞书/SMTP 已裁撤），不碰 facade 调度器，
不做收割（收割=reaper，M3 闭环另线）。
"""

from __future__ import annotations

import json
import logging
import math
import os
import threading
import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Final

import yaml

from zephyr.shared.io.file_utils import safe_write_text
from zephyr.shared.io.paths import REPO_ROOT

if TYPE_CHECKING:  # 运行时零依赖：判定模块仅在探针内 lazy import（infra 不在导入期依赖 risk）
    from zephyr.risk.core.survival_line_monitor import SurvivalInput, SurvivalLineConfig

logger = logging.getLogger(__name__)

_DEFAULT_BOARD_DIRNAME = "ops_notifications"
_BOARD_FILE = "notifications.jsonl"

# 与 facade alert 调度同拍（30s）；首轮延迟 5s 避开 api_server 启动尖峰
TICK_INTERVAL_S = 30.0
FIRST_TICK_DELAY_S = 5.0

# OOM 解除滞回：回落到阈值*0.9 才算解除（防阈值附近振荡刷板）
RESOLVE_HYSTERESIS = 0.9

# 已解除通知在前端的保留时长（灰显供回看）
RESOLVED_RETENTION_S = 3600.0

# ── 项目 RSS 绝对值告警线（排班表 v2 施工方案 §2.3 C-1⑤：消"8GB 绝对值"散落）──
# 规则真源仍是 config/alert_rules.yaml ALERT-SYS-002 的 condition（本模块照旧读它）；
# 下面这条 GiB 线的登记真源=config/resource_optimization.yaml
# ops_alerting.project_rss_alert_gb，仅当规则源缺席（文件缺失/损坏/无内存字节型规则）
# 时充当兜底线——静默失明比误报更坏，但兜底也只在 YAML 有值时生效（不臆造阈值）。
_RESOURCE_CFG_RELPATH: Final[str] = "config/resource_optimization.yaml"
_RSS_ALERT_KEY: Final[str] = "project_rss_alert_gb"
_RSS_ALERT_SECTION: Final[str] = "ops_alerting"
_GIB_BYTES: Final[int] = 1024 ** 3
_MEMORY_METRIC_FRAGMENT: Final[str] = "memory"
#: 兜底合成规则 id（与真源规则同前缀风格，MODIFY-GUARD 声明本模块不改规则文件）
FALLBACK_OOM_RULE_ID: Final[str] = "ALERT-SYS-002-FALLBACK"


def load_project_rss_alert_bytes() -> int | None:
    """读 resource_optimization.yaml ops_alerting.project_rss_alert_gb（GiB → 字节）。

    返回 None=键缺席/文件不可读/数值非法——调用方不臆造阈值（本模块零数值副本），
    仅 loud warning 后维持既有"无规则即不告警"语义。
    """
    import yaml  # try 外绑定：except 子句求值时需可见 yaml.YAMLError（非 ValueError 子类）

    try:
        data = yaml.safe_load((REPO_ROOT / _RESOURCE_CFG_RELPATH).read_text(encoding="utf-8")) or {}
        section = data.get(_RSS_ALERT_SECTION) if isinstance(data, dict) else None
        raw_gb = section.get(_RSS_ALERT_KEY) if isinstance(section, dict) else None
        if raw_gb is None:
            logger.warning(
                "load_project_rss_alert_bytes: %s 缺 %s.%s 键——OOM 兜底线不可用",
                _RESOURCE_CFG_RELPATH, _RSS_ALERT_SECTION, _RSS_ALERT_KEY,
            )
            return None
        gb = float(raw_gb)
        if gb <= 0:
            logger.warning("load_project_rss_alert_bytes: 非正数值 %s——OOM 兜底线不可用", raw_gb)
            return None
        return int(gb * _GIB_BYTES)
    except (OSError, ValueError, TypeError, yaml.YAMLError) as exc:
        logger.warning("load_project_rss_alert_bytes 读表失败（OOM 兜底线不可用）: %s", exc)
        return None


def board_dir() -> Path:
    """通知板目录：环境变量可重定向（测试隔离主通道），缺省生产 .runtime 路径。"""
    env = os.environ.get("ZEPHYR_OPS_NOTIFICATION_DIR", "")
    if env:
        return Path(env)
    return REPO_ROOT / ".runtime" / _DEFAULT_BOARD_DIRNAME


def _repo_root_lower() -> str:
    return str(REPO_ROOT).lower()


def probe_project_rss_bytes() -> int:
    """项目衍生进程 RSS 总量（字节）：当前进程树 ∪ cmdline/exe 引用仓根的进程。

    fail-safe：任何 psutil 异常（权限/消失竞态/缺席）按可测部分返回，绝不抛出——
    探针是常驻周期调用，抛异常=供给线自杀。
    """
    root_lower = _repo_root_lower()
    total = 0
    try:
        import psutil

        me = psutil.Process()
        try:
            total += me.memory_info().rss
        except psutil.Error:
            pass
        # 当前进程树（后代递归，消失即跳过）
        seen: set[int] = {me.pid}
        stack = list(me.children(recursive=False))
        while stack:
            proc = stack.pop()
            try:
                if proc.pid in seen:
                    continue
                seen.add(proc.pid)
                total += proc.memory_info().rss
                stack.extend(proc.children(recursive=False))
            except psutil.Error:
                continue
        # 仓根引用进程（llama-server 加载项目模型/项目内脚本等，去重已计树的）
        for proc in psutil.process_iter(["pid", "cmdline", "exe"]):
            try:
                if proc.info["pid"] in seen:
                    continue
                blob = " ".join(proc.info["cmdline"] or []).lower()
                exe = (proc.info["exe"] or "").lower()
                if root_lower in blob or root_lower in exe:
                    total += proc.memory_info().rss
            except (psutil.Error, psutil.NoSuchProcess):
                continue
    except Exception:  # noqa: BLE001 — 探针绝不抛出（INVARIANTS）
        logger.debug("probe_project_rss_bytes degraded", exc_info=True)
    return total


# ── 生存线 KPI 供给线（ALERT-KPI-001/002，2026-09-16 接线清偿）─────────────────
# 断链原貌：config/alert_rules.yaml 自 2026-08-19 起声明两条 critical 规则订阅
#   metric=kpi.survival_line.status（condition "== survival_breach" / "== failure"）、
#   通知板与 promotion 横幅通道已出厂——唯一缺件是"谁生产这个指标"。
# 判定真源：zephyr.risk.core.survival_line_monitor（90 号 §16 裁定①，阈值/口径均
#   取其 SurvivalLineConfig 默认，本文件零复刻）；状态词表=SurvivalStatus 枚举值
#   （ok / survival_breach / failure），与规则 condition 右端逐字对齐。
# 数据真源：c1_market.account_nav_daily（DDL-as-Code 唯一真源
#   schemas/categories/market/market_account_nav_daily.py；NavPoint 七字段口径，
#   含 benchmark_ratio 供超额口径——缺基准即不出指标，同 build_nav_curve 纪律）。

#: 生存线规则订阅口径：metric 含此片段即视为"状态型 KPI"规则
#: （与 evaluate_memory_rules 的 metric 片段过滤同族——阈值与严重度真源在 YAML）
SURVIVAL_METRIC_FRAGMENT: Final[str] = "survival_line"

#: 失败态复评退避：净值序列缺席/查询失败时按此节奏重试（既防空转打爆 CH，又不误伤
#: 到"数据补齐后 24h 才出指标"）；成功态复评节奏取规则 silence_window（见下）
SURVIVAL_RETRY_BACKOFF_S: Final[float] = 300.0

#: 日频净值最小样本（低于此不出指标——防冷启动噪声误报破线）
#: 口径对齐 35 号 memo §3.15 保守判据（zephyr.risk.core.drawdown_session_persistence
#  .MIN_NAV_HISTORY 同源 30 日），非本文件自立阈值
SURVIVAL_MIN_NAV_POINTS: Final[int] = 30

#: 净值查询超时（秒）
_NAV_QUERY_TIMEOUT_S: Final[int] = 15

#: 年化因子（日频 → 年频 Sharpe，A 股 252 交易日，同 strategy_retirement_evaluator 口径）
_ANNUAL_TRADING_DAYS: Final[int] = 252

#: 只读净值序列（NO-BARE-SQL gate 豁免：_SQL_* 前缀常量，同 ch_parts_monitor 约定）
#: {table} 由 DDL-as-Code 真源填充、{months} 由 SurvivalLineConfig.window_months 填充；
#: FINAL 去重由 ch_reader.inject_final 负责（此处勿硬编）。
#: 列不加别名——实测别名与 WHERE/ORDER BY 同名列相撞会让 CH 把谓词解析到 String
#: 投影上（"no supertype for types String, Date"）；parse_nav_tsv 按列序取值。
_SQL_SURVIVAL_NAV: Final[str] = (
    "SELECT toString(trade_date), toString(nav_ratio), toString(benchmark_ratio) "
    "FROM {table} WHERE trade_date >= subtractMonths(today(), {months}) ORDER BY trade_date"
)


def _nav_table_ref() -> str:
    """净值表引用（真源=DDL-as-Code 模块，禁码内第二真源）。"""
    from schemas.categories.market.market_account_nav_daily import DATABASE, TABLE_NAME

    return f"{DATABASE}.{TABLE_NAME}"


def _default_nav_query(sql: str, timeout: int) -> str:
    """默认查询通道（ch_reader 统一只读入口，TSV 输出；失败返回空串）。"""
    from zephyr.data import ch_reader

    return ch_reader.query(sql, timeout=timeout)


def parse_nav_tsv(tsv: str) -> list[tuple[str, float, float | None]]:
    """净值 TSV → [(trade_date, nav_ratio, benchmark_ratio|None)]（坏行跳过不致命）。

    benchmark_ratio 为 Nullable 列：CH TSV 原生 NULL 是 \\N，但 ch_writer 侧手工拼 TSV 用 str(v)，
    NULL 会落成字面量 "None" —— 两种形态（及空串/NULL/null）一律认作「基准缺席」。
    """
    rows: list[tuple[str, float, float | None]] = []
    for line in (tsv or "").splitlines():
        fields = line.split("\t")
        if len(fields) < 2:
            continue
        day, nav_raw, bench_raw = fields[0].strip(), fields[1].strip(), fields[2].strip() if len(fields) > 2 else ""
        try:
            nav = float(nav_raw)
        except ValueError:
            logger.warning("ops alert feed: skip corrupt nav row: %s", line[:120])
            continue
        if not math.isfinite(nav):  # NaN/inf=脏数据，跳过（下游判定 fail-closed 会抛）
            logger.warning("ops alert feed: skip non-finite nav row: %s", line[:120])
            continue
        bench: float | None
        if bench_raw in ("", "\\N", "NULL", "null", "None"):
            bench = None
        else:
            try:
                bench = float(bench_raw)
            except ValueError:
                bench = None
            else:
                if not math.isfinite(bench):
                    bench = None
        rows.append((day, nav, bench))
    return rows


def _max_drawdown(navs: list[float]) -> float:
    """峰谷最大回撤（正数）。"""
    peak = navs[0]
    max_dd = 0.0
    for n in navs:
        peak = max(peak, n)
        if peak > 0:
            max_dd = max(max_dd, 1.0 - n / peak)
    return max_dd


def _annualized_sharpe(navs: list[float]) -> float | None:
    """日收益均值/标准差 × √252；样本 <2 或零方差（序列冻结）→ None=不可测。"""
    daily = [navs[i] / navs[i - 1] - 1.0 for i in range(1, len(navs)) if navs[i - 1] > 0]
    if len(daily) < 2:
        return None
    mean = sum(daily) / len(daily)
    var = sum((r - mean) ** 2 for r in daily) / (len(daily) - 1)
    if var <= 1e-18:  # 序列冻结（净值长期不更新）=指标不可测，不伪装成 ok 也不伪装成破线
        return None
    return mean / (var**0.5) * (_ANNUAL_TRADING_DAYS**0.5)


def _month_end_navs(pts: list[tuple[str, float, float | None]]) -> list[tuple[str, float]]:
    """日频 → 月末净值序列（同月后到者覆盖；入参已按日期升序）。"""
    month_end: list[tuple[str, float]] = []
    for d, n, _ in pts:
        key = d[:7]
        if month_end and month_end[-1][0] == key:
            month_end[-1] = (key, n)
        else:
            month_end.append((key, n))
    return month_end


def _consecutive_loss_months(pts: list[tuple[str, float, float | None]]) -> int:
    """月末环比连续为负的尾部月数（在途月计入——风险侧保守）。"""
    month_end = _month_end_navs(pts)
    monthly = [
        month_end[i][1] / month_end[i - 1][1] - 1.0 for i in range(1, len(month_end)) if month_end[i - 1][1] > 0
    ]
    streak = 0
    for r in reversed(monthly):
        if r >= 0:
            break
        streak += 1
    return streak


def _excess_return(pts: list[tuple[str, float, float | None]]) -> float | None:
    """区间净值收益 − 区间基准收益；基准点 <2 → None（超额无定义，同 build_nav_curve 降级纪律）。"""
    bench_pts = [(d, n, b) for d, n, b in pts if b is not None and b > 0]
    if len(bench_pts) < 2:
        return None
    nav_ret = bench_pts[-1][1] / bench_pts[0][1] - 1.0
    bench_ret = bench_pts[-1][2] / bench_pts[0][2] - 1.0
    return nav_ret - bench_ret


def survival_input_from_nav(
    points: list[tuple[str, float, float | None]],
    *,
    min_points: int = SURVIVAL_MIN_NAV_POINTS,
) -> SurvivalInput | None:
    """日频净值序列 → 生存线输入（纯函数；不足/畸形 → None，不出伪指标）。

    口径（与 90 号 §16 裁定①四字段一一对应）见四个 `_`* 子函数各自 docstring。
    """
    pts = [(d, n, b) for d, n, b in points if n > 0]
    if len(pts) < 2 or len(pts) < min_points:
        return None
    navs = [n for _, n, _ in pts]
    sharpe = _annualized_sharpe(navs)
    if sharpe is None:
        return None
    excess = _excess_return(pts)
    if excess is None:
        return None

    from zephyr.risk.core.survival_line_monitor import SurvivalInput

    return SurvivalInput(
        excess_return_12m=excess,
        max_drawdown=_max_drawdown(navs),
        sharpe=sharpe,
        consecutive_loss_months=_consecutive_loss_months(pts),
    )


def probe_survival_status(
    *,
    query_fn: Callable[[str, int], str] | None = None,
    config: SurvivalLineConfig | None = None,
) -> dict | None:
    """生存线状态探针 → {"status","breaches","input"} | None（None=指标缺席）。

    fail-safe（INVARIANTS 同 RSS 探针：绝不抛出）：判定模块缺位 / 查询失败 /
    表结构未就绪 / 样本不足 / 评估异常 → logger.warning + None。
    降级=**不产出该指标**，绝不兜底成 ok（静默兜底=假健康，正是本次要清偿的反模式）。
    """
    try:
        from zephyr.risk.core.survival_line_monitor import SurvivalLineConfig, evaluate_survival_line
    except Exception as exc:  # noqa: BLE001 — 判定模块缺位=本指标不产（不炸 feed 循环）
        logger.warning("survival line monitor unavailable, metric skipped: %s", exc)
        return None
    cfg = config or SurvivalLineConfig()
    q = query_fn or _default_nav_query
    try:
        tsv = q(
            _SQL_SURVIVAL_NAV.format(table=_nav_table_ref(), months=int(cfg.window_months)),
            _NAV_QUERY_TIMEOUT_S,
        )
    except Exception as exc:  # noqa: BLE001 — 数据通道异常降级缺席
        logger.warning("survival nav query failed, metric not published: %s", exc)
        return None
    if not (tsv or "").strip():
        logger.warning(
            "survival nav series empty (%s 无滚动 %s 月净值), metric not published",
            "account_nav_daily",
            cfg.window_months,
        )
        return None
    points = parse_nav_tsv(tsv)
    metrics = survival_input_from_nav(points)
    if metrics is None:
        logger.warning(
            "survival line inputs insufficient (nav rows=%d, min=%d; 缺基准/样本不足/序列冻结) "
            "— metric not published",
            len(points),
            SURVIVAL_MIN_NAV_POINTS,
        )
        return None
    try:
        result = evaluate_survival_line(metrics, cfg)
    except Exception as exc:  # noqa: BLE001 — 判定异常降级缺席（非法输入=数据脏，不猜状态）
        logger.warning("evaluate_survival_line raised, metric not published: %s", exc)
        return None
    return {"status": result.status.value, "breaches": list(result.breaches), "input": metrics}


class OpsAlertFeed:
    """运营告警通知板：规则评估 → 落盘发布 → 只读清单。

    Args:
        board_dir: 通知板目录；None 时经模块级 board_dir()（环境变量可重定向）。
        rules_path: 告警规则 YAML；None 时用 config/alert_rules.yaml。
        module_id: 通知来源标识。
    """

    def __init__(
        self,
        board_dir: str | Path | None = None,
        rules_path: str | Path | None = None,
        module_id: str = "ops-alert-feed",
    ):
        self._board_dir = Path(board_dir) if board_dir else None
        self._rules_path = Path(rules_path) if rules_path else None
        self._module_id = module_id
        self._rules: list[dict] = []
        self._rules_loaded = False
        self._lock = threading.Lock()
        # 生存线日频段状态 {"last_ts": float, "payload": dict | None}（30s tick 不复查 CH）
        self._survival_state: dict = {}

    # ── 板存储 ──

    def _dir(self) -> Path:
        return self._board_dir if self._board_dir else board_dir()

    def _board_path(self) -> Path:
        return self._dir() / _BOARD_FILE

    def _read_entries(self) -> list[dict]:
        p = self._board_path()
        if not p.exists():
            return []
        out: list[dict] = []
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    out.append(obj)
            except json.JSONDecodeError:
                logger.warning("ops notification board: skip corrupt line in %s", p)
        return out

    def _write_entries(self, entries: list[dict]) -> None:
        p = self._board_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        content = "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in entries)
        expected = None
        if p.exists():
            # CAS base=读到的原文本 content_sha256（UTF-8 语义 hash，同 safe_write_text 校验口径）
            from zephyr.shared.io.file_utils import content_sha256

            expected = content_sha256(p.read_text(encoding="utf-8"))
        safe_write_text(p, content, expected_base_sha256=expected)

    # ── 发布 / 清单 / 解除 ──

    def publish(
        self,
        *,
        key: str,
        severity: str,
        title: str,
        message: str,
        source: str | None = None,
        labels: dict | None = None,
        silence_window_s: float = 300.0,
        now: float | None = None,
    ) -> dict:
        """发布一条通知（静默窗口内同 key 只刷新不重复）。返回该次操作结果。"""
        import time

        ts = now if now is not None else time.time()
        with self._lock:
            entries = self._read_entries()
            for e in entries:
                if e.get("key") == key and not e.get("resolved_at"):
                    if ts - float(e.get("last_seen", 0)) < silence_window_s:
                        e["last_seen"] = ts
                        e["count"] = int(e.get("count", 1)) + 1
                        self._write_entries(entries)
                        return {"op": "refresh", "id": e.get("id"), "key": key}
            entry = {
                "id": uuid.uuid4().hex[:12],
                "key": key,
                "module_id": self._module_id,
                "severity": severity,
                "title": title,
                "message": message,
                "source": source or self._module_id,
                "labels": labels or {},
                "first_seen": ts,
                "last_seen": ts,
                "count": 1,
                "resolved_at": None,
            }
            entries.append(entry)
            self._write_entries(entries)
            return {"op": "created", "id": entry["id"], "key": key}

    def list_active(self, resolved_retention_s: float = RESOLVED_RETENTION_S, now: float | None = None) -> list[dict]:
        """活动通知清单（未解除 + 近期解除灰显项），first_seen 倒序。"""
        import time

        ts = now if now is not None else time.time()
        entries = self._read_entries()
        out = [
            e
            for e in entries
            if not e.get("resolved_at") or (ts - float(e.get("resolved_at", 0))) <= resolved_retention_s
        ]
        out.sort(key=lambda e: (bool(e.get("resolved_at")), -float(e.get("first_seen", 0))))
        return out

    def resolve(self, key: str, now: float | None = None) -> int:
        """解除指定 key 的全部活动通知，返回解除条数。"""
        import time

        ts = now if now is not None else time.time()
        with self._lock:
            entries = self._read_entries()
            n = 0
            for e in entries:
                if e.get("key") == key and not e.get("resolved_at"):
                    e["resolved_at"] = ts
                    n += 1
            if n:
                self._write_entries(entries)
            return n

    # ── 规则评估与周期 tick ──

    def _load_rules(self) -> list[dict]:
        if self._rules_loaded:
            return self._rules
        path = self._rules_path or (REPO_ROOT / "config" / "alert_rules.yaml")
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            self._rules = data.get("rules", []) or []
        except (OSError, yaml.YAMLError):
            self._rules = []
        self._rules_loaded = True
        return self._rules

    def _memory_rules(self) -> list[dict]:
        """内存字节型规则清单：真源=config/alert_rules.yaml；缺席时按兜底线合成一条。

        兜底合成（排班表 v2 §2.3 C-1⑤）只在规则源"完全没有内存字节型规则"时启用，
        生产正常路径逐字不变；silence_window 等字段刻意不写，沿用调用处既有缺省
        （不新增第二处口径）。兜底线本身来自 resource_optimization.yaml，
        该键也缺席 → 返回空表（与改造前"无规则=不告警"同语义，但已 loud warning）。
        """
        rules = [
            r
            for r in self._load_rules()
            if _MEMORY_METRIC_FRAGMENT in str(r.get("metric", "")) and "bytes" in str(r.get("metric", ""))
        ]
        if rules:
            return rules
        fb_bytes = load_project_rss_alert_bytes()
        if fb_bytes is None:
            return []
        logger.warning(
            "alert_rules.yaml 无内存字节型规则——OOM 评估改按 %s.%s 兜底线 %d 字节",
            _RESOURCE_CFG_RELPATH, _RSS_ALERT_KEY, fb_bytes,
        )
        return [{
            "id": FALLBACK_OOM_RULE_ID,
            "name": "oom_risk",
            "severity": "critical",
            "metric": "system.memory_rss_bytes",
            "condition": f"> {fb_bytes}",
            "description": "内存即将耗尽（RSS 兜底线，数值真源见 config/resource_optimization.yaml）",
        }]

    def evaluate_memory_rules(self, value: float) -> list[dict]:
        """对内存类规则（metric 含 memory 的字节型规则）评估，返回触发规则列表。"""
        triggered: list[dict] = []
        for rule in self._memory_rules():
            condition = str(rule.get("condition", ""))
            if self._check(value, condition):
                triggered.append(rule)
        return triggered

    @staticmethod
    def _check(value: float, condition: str) -> bool:
        # 复用 AlertSubsystem 的条件解析（零复制语义）；静态方法无实例依赖
        from zephyr.infrastructure.system_telemetry.alerts import AlertSubsystem

        return AlertSubsystem._check_condition(value, condition)

    def _iter_survival_rules(self) -> list[dict]:
        """订阅生存线状态指标的规则清单（metric 真源=config/alert_rules.yaml）。"""
        return [r for r in self._load_rules() if SURVIVAL_METRIC_FRAGMENT in str(r.get("metric", ""))]

    def evaluate_survival_rules(self, status: str) -> list[dict]:
        """对生存线状态型规则（ALERT-KPI-001/002）评估，返回触发列表。

        Args:
            status: SurvivalStatus 词表值（"ok"/"survival_breach"/"failure"）。
        """
        triggered: list[dict] = []
        for rule in self._iter_survival_rules():
            if self._check_status(status, str(rule.get("condition", ""))):
                triggered.append(rule)
        return triggered

    @staticmethod
    def _check_status(value: str, condition: str) -> bool:
        """字符串状态条件评估（KPI 规则形态 "== survival_breach"）。

        真源 AlertSubsystem._check_condition 只认 >/＜ 数值比较（_check 复用之），
        对 "== xxx" 恒 False；而 alerts/__init__.py 是 safety=H / ai_autonomy=
        human_gated（本模块不越权改）。故此处只补 == / != 两式，其余形态一律 False
        ——不认识的条件下绝不触发（宁漏不误报）。
        """
        cond = str(condition).strip()
        if cond.startswith("=="):
            return value == cond[2:].strip()
        if cond.startswith("!="):
            return value != cond[2:].strip()
        return False

    def survival_refresh_interval_s(self) -> float | None:
        """生存线复评节奏（秒）=规则 silence_window 最大值（节奏真源在 YAML，不硬编）。

        返回 None=规则集里根本没有生存线指标（本环境不产该指标）。
        """
        rules = self._iter_survival_rules()
        if not rules:
            return None
        return max(self._parse_silence(r.get("silence_window", "1d")) for r in rules)

    def _survival_payload(
        self,
        now: float,
        *,
        probe_fn: Callable[[], dict | None],
        refresh_s: float,
        force: bool,
    ) -> dict | None:
        """复评节奏判定 + 探针调用（缓存段，不碰通知板）。

        命中缓存=直接返回上次载荷；否则真探一次并刷新 last_ts。探针抛出
        绝不外炸（INVARIANTS）→ 记 WARNING 后按缺席处理。
        """
        st = self._survival_state
        cached = st.get("payload") if "payload" in st else None
        last_ts = float(st.get("last_ts", 0.0))
        backoff = refresh_s if cached is not None else min(refresh_s, SURVIVAL_RETRY_BACKOFF_S)
        if not force and st and (now - last_ts) < backoff:
            return cached
        try:
            payload = probe_fn()
        except Exception as exc:  # noqa: BLE001 — 探针绝不炸 tick（INVARIANTS）
            logger.warning("survival probe raised unexpectedly: %s", exc)
            payload = None
        st["last_ts"] = now
        st["payload"] = payload
        return payload

    def _publish_survival_rule(self, rule: dict, status: str, breaches: list[str], now: float) -> dict:
        """单条 critical 规则 → 通知板一条目（CAS 拒写降级不炸 tick）。"""
        detail = f"（实测状态 {status}"
        if breaches:
            detail += "：" + "；".join(breaches)
        detail += "）"
        try:
            return self.publish(
                key=str(rule.get("id", "ALERT-UNKNOWN")),
                severity="critical",
                title=str(rule.get("name", "survival_line")),
                message=str(rule.get("description", "")) + detail,
                labels={"metric": rule.get("metric"), "value": status, "breaches": breaches},
                silence_window_s=self._parse_silence(rule.get("silence_window", "1d")),
                now=now,
            )
        except Exception as exc:  # noqa: BLE001 — 板 CAS 拒写降级不炸 tick
            logger.warning("survival notification publish failed: %s", exc)
            return {"op": "failed", "key": rule.get("id"), "reason": str(exc)[:120]}

    def _resolve_stale_survival_alerts(self, fired: set[str], now: float) -> list[dict]:
        """未命中生存线规则的历史通知解除（回 ok / 状态互斥切换在此收敛）。"""
        ops: list[dict] = []
        for rule in self._iter_survival_rules():
            rid = str(rule.get("id", ""))
            if not rid or rid in fired:
                continue
            try:
                n = self.resolve(rid, now=now)
                if n:
                    ops.append({"op": "resolved", "key": rid, "count": n})
            except Exception as exc:  # noqa: BLE001 — 解除失败不炸 tick
                logger.warning("survival notification resolve failed: %s", exc)
        return ops

    def _emit_survival_alerts(self, status: str, breaches: list[str], triggered: list[dict], now: float) -> list[dict]:
        """命中规则逐条发布 + 未命中规则历史解除。"""
        ops: list[dict] = []
        for rule in triggered:
            if str(rule.get("severity", "")).lower() != "critical":
                continue
            ops.append(self._publish_survival_rule(rule, status, breaches, now))
        return ops + self._resolve_stale_survival_alerts({str(r.get("id", "")) for r in triggered}, now)

    def tick_survival(
        self,
        now: float,
        *,
        probe: Callable[[], dict | None] | None = None,
        force: bool = False,
    ) -> dict:
        """生存线 KPI 监测段：探针→评估→发布/解除（独立于内存段，互不连坐）。

        日频指标按规则 silence_window 节奏复评；失败态以 SURVIVAL_RETRY_BACKOFF_S
        退避重试（防 30s 打爆 CH，亦防数据补齐后再等一天）。

        降级姿态（INVARIANTS）：探针缺席/异常 → 不产出任何通知 + logger.warning
        （loud，绝不静默兜底成 ok）；本段永不抛出，返回值携 available/reason。
        """
        refresh = self.survival_refresh_interval_s()
        if refresh is None:
            logger.warning(
                "no %s metric rule found in alert rules — survival line metric not produced",
                SURVIVAL_METRIC_FRAGMENT,
            )
            return {"available": False, "reason": "no-survival-rule", "status": None, "ops": []}

        payload = self._survival_payload(now, probe_fn=probe or probe_survival_status, refresh_s=refresh, force=force)
        if payload is None:
            return {"available": False, "reason": "input-unavailable", "status": None, "ops": []}

        status = str(payload.get("status", ""))
        breaches = [str(b) for b in (payload.get("breaches") or [])]
        try:
            triggered = self.evaluate_survival_rules(status)
        except Exception as exc:  # noqa: BLE001 — 规则评估异常降级（同内存段红蓝 2026-09-16）
            logger.warning("survival rule evaluation failed: %s", exc)
            return {"available": True, "reason": "evaluate failed", "status": status, "ops": []}
        return {
            "available": True,
            "reason": None,
            "status": status,
            "breaches": breaches,
            "ops": self._emit_survival_alerts(status, breaches, triggered, now),
        }

    def tick(
        self,
        probe: Callable[[], int] | None = None,
        now: float | None = None,
        survival_probe: Callable[[], dict | None] | None = None,
    ) -> dict:
        """一个监测周期：探针→评估→发布/解除。返回周期摘要（供日志与测试断言）。

        两段独立：内存段（probe_project_rss_bytes）+ 生存线 KPI 段（tick_survival）
        ——任一段探针/评估异常只降级该段，绝不连坐另一段（2026-09-16 接线清偿）。

        fail-safe：调用方是常驻线程，本方法绝不抛出。
        """
        import time

        ts = now if now is not None else time.time()
        survival = self.tick_survival(ts, probe=survival_probe)
        probe_fn = probe or probe_project_rss_bytes
        try:
            value = probe_fn()
        except Exception as exc:  # noqa: BLE001 — INVARIANTS: fail-safe
            logger.debug("ops alert feed probe failed: %s", exc)
            return {"ok": False, "reason": f"probe failed: {exc}", "ts": ts, "survival": survival}

        try:
            triggered = self.evaluate_memory_rules(float(value))
        except Exception as exc:  # noqa: BLE001 — 规则评估异常降级（红蓝 2026-09-16）
            logger.debug("ops alert feed evaluate failed: %s", exc)
            return {"ok": False, "reason": f"evaluate failed: {exc}", "ts": ts, "survival": survival}
        ops: list[dict] = []
        for rule in triggered:
            if str(rule.get("severity", "")).lower() != "critical":
                continue
            silence = self._parse_silence(rule.get("silence_window", "5m"))
            try:
                ops.append(
                    self.publish(
                        key=str(rule.get("id", "ALERT-UNKNOWN")),
                        severity="critical",
                        title=str(rule.get("name", "oom_risk")),
                        message=str(rule.get("description", "")) + f"（实测 {value} 字节）",
                        labels={"metric": rule.get("metric"), "value": value},
                        silence_window_s=silence,
                        now=ts,
                    )
                )
            except Exception as exc:  # noqa: BLE001 — 板 CAS 拒写降级不炸 tick（红蓝 2026-09-16）
                logger.warning("ops alert feed publish failed: %s", exc)
                ops.append({"op": "failed", "key": rule.get("id"), "reason": str(exc)[:120]})
        # 无 critical 触发 → 按滞回解除既有 OOM 项
        if not any(str(r.get("severity")).lower() == "critical" for r in triggered):
            for rule in self._memory_rules():  # 含兜底合成规则——否则其触发后永不自解
                metric = str(rule.get("metric", ""))
                if _MEMORY_METRIC_FRAGMENT not in metric or SURVIVAL_METRIC_FRAGMENT in metric:
                    continue
                condition = str(rule.get("condition", ""))
                threshold = self._threshold_of(condition)
                if threshold is None:
                    continue
                if float(value) <= threshold * RESOLVE_HYSTERESIS:
                    n = self.resolve(str(rule.get("id", "")), now=ts)
                    if n:
                        ops.append({"op": "resolved", "key": rule.get("id"), "count": n})
        return {
            "ok": True,
            "ts": ts,
            "value": value,
            "triggered": [r.get("id") for r in triggered],
            "ops": ops,
            "survival": survival,
        }

    @staticmethod
    def _threshold_of(condition: str) -> float | None:
        try:
            return float(str(condition).strip()[1:])
        except (ValueError, IndexError):
            return None

    @staticmethod
    def _parse_silence(raw: object) -> float:
        """silence_window 字符串（"5m"/"30s"/"1d"）→ 秒；解析失败缺省 300s。"""
        try:
            s = str(raw).strip()
            unit = s[-1]
            num = float(s[:-1])
            return {"s": num, "m": num * 60, "h": num * 3600, "d": num * 86400}.get(unit, 300.0)
        except (ValueError, TypeError, IndexError):
            return 300.0


__all__ = [
    "FALLBACK_OOM_RULE_ID",
    "FIRST_TICK_DELAY_S",
    "RESOLVED_RETENTION_S",
    "RESOLVE_HYSTERESIS",
    "SURVIVAL_METRIC_FRAGMENT",
    "SURVIVAL_MIN_NAV_POINTS",
    "SURVIVAL_RETRY_BACKOFF_S",
    "TICK_INTERVAL_S",
    "OpsAlertFeed",
    "board_dir",
    "load_project_rss_alert_bytes",
    "parse_nav_tsv",
    "probe_project_rss_bytes",
    "probe_survival_status",
    "survival_input_from_nav",
]
