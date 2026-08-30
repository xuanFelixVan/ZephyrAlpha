# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.source_health_check
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.implementations.*_provider; zephyr.shared.security.secrets
# [CONSUMERS] zephyr.data.scheduler
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] 不阻塞调度器启动（超时60s）；结果写日志+内存；异常源不自动禁用（人工决策）
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 任何provider检查失败->记录error，不抛异常（不影响调度器启动）
# [TESTS] tests/data/test_source_health_check.py
# [TTL] permanent
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 源检查配置
#   fields: _HEALTH_CHECKS（source/module/class/测试 API 探针）
#   code: 模块级 _HEALTH_CHECKS 常量
# - id: I2
#   name: 内存结果缓存
#   fields: _latest_results（各源 status + timestamp）
#   code: get_latest_results/_health_check_age_minutes
# 层: 算法
# - id: A1
#   name_zh: ① 单源三段探测
#   name_en: _run_single_check
#   intro: import provider→实例化 connect→测试 API 调用，逐段记耗时与错误，任意段失败记状态不抛异常（60s 超时红线）
#   inputs: I1
#   outputs: 单源 result 字典（status/connect_ok/耗时/error）
# - id: A2
#   name_zh: ② 全量检查与缓存落盘
#   name_en: run_source_health_check
#   intro: 遍历全部源执行 A1，单源异常不波及其他源；结果写 logs/source_health_YYYYMMDD.log + 更新 _latest_results（scheduler 启动时调用一次）
#   inputs: I1
#   outputs: results 列表 + 日志文件 + 缓存
# - id: A3
#   name_zh: ③ 缓存 TTL 单源重检
#   name_en: _recheck_single_source
#   intro: scheduler 因缓存 test_fail 跳过某源且距上次检查超 30min 时，仅对该源重检并更新缓存（成败均入缓存），避免 QMT 恢复后被永久跳过（8/18 分钟线零采集事故根因修复）
#   inputs: I1 I2
#   outputs: 该源最新 result + 缓存更新
# 层: 输出
# - id: O1
#   name_zh: 健康状态查询面
#   name_en: get_latest_results
#   intro: 供 scheduler 健康门查询各源 healthy/test_fail；日志落盘供人工巡检
"""



数据源健康检查模块（每日调度器启动时执行）。

功能：
- 对所有注册的 provider 执行连接 + 简单 API 调用测试
- 记录响应时间、错误信息、数据量
- 结果写入 logs/source_health_YYYYMMDD.log
- 异常数据源记录但不自动禁用（由人工或 fallback 机制处理）

集成点：scheduler.start() -> run_source_health_check()

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: source 参数
#   fields: 参数 source，类型注解 str
#   code: source_health_check.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① run_source_health_check
#   name_en: run_source_health_check
#   intro: 执行全量数据源健康检查（供 scheduler.start() 调用）。
#   desc: 执行全量数据源健康检查（供 scheduler.start() 调用）。 Returns: {source_name: result_dict} 最新健康状态。；源码 L564-L626
#   inputs: 无参数
#   outputs: dict[str, dict]
# - id: A2
#   name_zh: ② get_source_health
#   name_en: get_source_health
#   intro: 查询单个数据源的最新健康状态（供 scheduler 调度决策用）。
#   desc: 查询单个数据源的最新健康状态（供 scheduler 调度决策用）。 Returns: 最新健康状态 dict，或 None（未检查过）。；源码 L681-L688
#   inputs: source
#   outputs: dict | None
# - id: A3
#   name_zh: ③ get_all_source_health
#   name_en: get_all_source_health
#   intro: 查询所有数据源的最新健康状态。
#   desc: 查询所有数据源的最新健康状态。；源码 L691-L694
#   inputs: 无参数
#   outputs: dict[str, dict]
# 层: 输出
# - id: O1
#   name_zh: dict[str, dict]
#   name_en: dict[str, dict]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler
# - id: O2
#   name_zh: dict | None
#   name_en: dict | None
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.data.scheduler
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> O1
"""

from __future__ import annotations

import logging
import os
import time
from pathlib import Path
from typing import Any

from zephyr.shared.utils.time_utils import now_utc

log = logging.getLogger(__name__)

# 健康检查超时（秒）—— 不阻塞调度器启动太久
_HEALTH_CHECK_TIMEOUT = 60

# 健康检查缓存 TTL（分钟）—— scheduler 因健康检查跳过某源时，若距上次全量检查超过
# 此时间，对该源单独重检一次并更新缓存，避免 QMT 恢复后仍被永久跳过。
_HEALTH_CACHE_TTL_MINUTES = 30

# ---- 同源连续失败告警（#ARCH-DATA-015） ----
# 免费匿名源无 SLA（如 baostock 10001011 IP黑名单），异常可能持续多日无人察觉；
# 100% AI 开发无人类盯环境，同源连续异常 >=_STREAK_ALERT_DAYS 天必须主动触达。
_STREAKS_PATH = Path("data/source_health_streaks.json")
_STREAK_ALERT_DAYS = 3
_OK_STATUSES = ("healthy", "connect_only", "env_missing")


def _update_failure_streaks(results: list[dict]) -> None:
    """按自然日累计同源连续异常，超阈值告警、恢复消警。

    同一天多次健康检查只计一次（last_date 去重）；告警/状态读写失败仅记日志，
    绝不影响健康检查主流程（ERROR_CONTRACT）。
    """
    import datetime as _dt
    import json

    try:
        today = now_utc().date().isoformat()
        yesterday = (now_utc().date() - _dt.timedelta(days=1)).isoformat()
        streaks: dict[str, dict] = {}
        if _STREAKS_PATH.is_file():
            try:
                streaks = json.loads(_STREAKS_PATH.read_text(encoding="utf-8"))
            except Exception:  # noqa: BLE001 — 损坏则从空重建
                streaks = {}

        from zephyr.data.alerter import LEVEL_ERROR, LEVEL_INFO, Alerter

        alerter = Alerter()
        for r in results:
            source = r["source"]
            status = r["status"]
            entry = streaks.get(source) or {"streak": 0, "alerted": False}
            last_date = entry.get("last_date")
            if status in _OK_STATUSES:
                if entry.get("alerted"):
                    alerter.notify(
                        f"source_health:{source}",
                        f"数据源 {source} 已恢复正常（{status}），连续异常告警解除",
                        level=LEVEL_INFO,
                        source=source,
                    )
                streaks[source] = {
                    "streak": 0,
                    "alerted": False,
                    "last_date": today,
                    "last_status": status,
                }
                continue
            # 异常分支：按自然日累计连续异常
            if last_date == today:
                streak = entry.get("streak", 0) or 1
            elif last_date == yesterday:
                streak = entry.get("streak", 0) + 1
            else:
                streak = 1
            alerted = entry.get("alerted", False)
            if streak >= _STREAK_ALERT_DAYS and not alerted:
                alerter.notify(
                    f"source_health:{source}",
                    (
                        f"数据源 {source} 连续 {streak} 天异常（{status}: {r.get('error', '')}）。"
                        "处置 SOP 见运维手册 §7.2.6：①换公网 IP（路由器重播/切换 VPN 出口）后复测；"
                        "②确认 IP 级封禁则联系数据源管理员解封；③评估 fallback 是否够用（多数任务已有替代源）"
                    ),
                    level=LEVEL_ERROR,
                    source=source,
                )
                alerted = True
                log.warning("数据源 %s 连续 %d 天异常，已触发告警", source, streak)
            streaks[source] = {
                "streak": streak,
                "alerted": alerted,
                "last_date": today,
                "last_status": status,
            }

        _STREAKS_PATH.parent.mkdir(parents=True, exist_ok=True)
        _STREAKS_PATH.write_text(json.dumps(streaks, ensure_ascii=False, indent=1), encoding="utf-8")
    except Exception as e:  # noqa: BLE001 — 告警链路故障不阻塞健康检查
        log.warning("连续失败告警更新失败（不影响健康检查）: %s", e)


# ---- API 拉取探针（connect_only 源升级为真实数据拉取测试，2026-08-04）----
# 每个探针接收已 connect 的 provider，返回 list/DataFrame（非空=healthy，空=empty_data）。
# 导入在函数内延迟执行：单源 provider 模块导入失败不影响整体 health check 模块加载。
# 探针选型均经 tmp/probe_7_sources.py 实测验证返回非空数据。
def _probe_miniqmt(provider) -> list:
    """miniQMT 探针：xtdata.get_stock_list_in_sector 沪深A股成分股列表。

    选型依据（项目记忆 QMT 探活 API 选型铁律）：必须用 get_stock_list_in_sector，
    禁用依赖行情时段的 get_market_data_ex（午休/盘前假阴性）。
    """
    from xtquant import xtdata

    return xtdata.get_stock_list_in_sector("沪深A股")


def _probe_tdx(provider):
    """tdx 探针：取浦发银行(600000)最近1根日线，验证服务器支持K线查询。

    与 connect() 内 _verify_kline 一致，确保 bestip 选中的服务器真能出K线数据。
    """
    return provider._client.bars(symbol="600000", frequency=9, start=0, offset=1)


def _probe_tickflow(provider):
    """tickflow 探针：取 SPY.US 最近5根日K（免费版支持美股日K）。

    符号必须带 .US 后缀——裸 "AAPL" 返回空 DataFrame（实测）。
    """
    return provider._client.klines.get(
        "SPY.US",
        period="1d",
        count=5,
        as_dataframe=True,
    )


def _probe_rss(provider) -> list:
    """rss 探针：解析国内直连 RSS feed，返回 entries。

    选国内直连源（非 RSSHub 路由、非海外源），不依赖本地 RSSHub 进程或 VPN，
    纯粹验证 feedparser + 国内 HTTP 连通性。
    2026-08-14 修复：36kr.com/feed 变为返回 200 但 0 entries（反爬空壳页），
    单源探针误报 empty_data → 任务误走 fallback。改为双源任一并非空即健康。
    """
    import feedparser

    from zephyr.shared.foundation.constants import DEFAULT_HTTP_UA

    for url in ("https://36kr.com/feed", "https://www.tmtpost.com/rss.xml"):
        try:
            resp = provider._http_get(url, timeout=15, headers={"User-Agent": DEFAULT_HTTP_UA})
            entries = feedparser.parse(resp.content).entries
            if entries:
                return entries
        except Exception:  # noqa: BLE001 — 探针容错：单源失败尝试下一源
            continue
    return []


def _probe_cls(provider) -> list:
    """cls 探针：本地 RSSHub 财联社电报，返回 items。

    依赖本地 RSSHub 实例（localhost:1200）。RSSHub 未运行→连接失败→test_fail，
    属真实健康信号（cls 能力本身依赖 RSSHub 路由）。
    """
    from zephyr.data.implementations.cls_provider import _CLS_HEADERS, _CLS_RSSHUB_URL

    resp = provider._http_get(
        _CLS_RSSHUB_URL,
        params={"format": "json"},
        headers=_CLS_HEADERS,
        timeout=15,
    )
    return resp.json().get("items") or []


def _probe_eastmoney_news(provider) -> list:
    """eastmoney_news 探针：东方财富7x24快讯API，返回新闻 list。

    注：np-listapi.eastmoney.com 与 push2.eastmoney.com 是不同子域——
    push2 因 akshare 100+ fields 大请求被断连（见 akshare 探针选型注释），
    但 np-listapi 实测可用，不受影响。
    """
    from zephyr.data.implementations.eastmoney_news_provider import (
        _EM_HEADERS,
        _EM_NEWS_URL,
    )

    params = {
        "client": "web",
        "biz": "web_724",
        "column": "350",
        "order": "1",
        "needInteractData": "0",
        "page_index": "1",
        "page_size": "5",
        "req_trace": str(int(now_utc().timestamp() * 1000)),
    }
    resp = provider._http_get(
        _EM_NEWS_URL,
        params=params,
        headers=_EM_HEADERS,
        timeout=15,
    )
    return (resp.json().get("data") or {}).get("list") or []


def _probe_tqcenter(provider) -> list:
    """tqcenter 探针：tq.get_sector_list 880xxx 板块代码列表。"""
    return provider._tq.get_sector_list()


# 每个数据源的检查配置
# source: (module, class_name, test_lambda_or_None, env_required)
_HEALTH_CHECKS: list[dict[str, Any]] = [
    {
        "source": "tushare",
        "module": "zephyr.data.implementations.tushare_provider",
        "class": "TushareProvider",
        "test": lambda p: p._pro.index_classify(level="L1", src="SW2021"),
        "test_desc": "index_classify L1",
        "env_required": ["TUSHARE_TOKEN"],
    },
    {
        "source": "akshare",
        "module": "zephyr.data.implementations.akshare_provider",
        "class": "AkshareIngestProvider",
        # 探针选型（2026-08-04）：stock_individual_info_em 走东财 push2，akshare 发送 100+ fields
        # 大请求被东财断连（实测 0/5 失败），会误判 akshare=unhealthy → scheduler 跳过 →
        # akshare 主源任务全断。改用 tool_trade_date_hist_sina（新浪源，0.26s，3/3 成功），
        # 既达标（<2s）又符合项目反爬规避策略（非东财接口）。
        "test": lambda p: __import__("akshare").tool_trade_date_hist_sina(),
        "test_desc": "tool_trade_date_hist_sina 新浪交易日历",
        "env_required": [],
    },
    {
        "source": "baostock",
        "module": "zephyr.data.implementations.baostock_provider",
        "class": "BaostockProvider",
        "test": lambda p: (
            __import__("baostock").query_trade_dates(start_date="2026-08-01", end_date="2026-08-04").get_data()
        ),
        "test_desc": "query_trade_dates 交易日历",
        "env_required": [],
    },
    {
        "source": "miniqmt",
        "module": "zephyr.data.implementations.miniqmt_provider",
        "class": "MiniQmtIngestProvider",
        "test": _probe_miniqmt,
        "test_desc": "xtdata.get_stock_list_in_sector 沪深A股（需 XtMiniQmt.exe）",
        "env_required": [],
    },
    {
        "source": "tdx",
        "module": "zephyr.data.implementations.tdx_provider",
        "class": "TDXProvider",
        "test": _probe_tdx,
        "test_desc": "bars(600000) 1根日线 验证K线查询能力",
        "env_required": [],
    },
    {
        "source": "tickflow",
        "module": "zephyr.data.implementations.tickflow_provider",
        "class": "TickFlowProvider",
        "test": _probe_tickflow,
        "test_desc": "klines.get(SPY.US) 5根日K 验证美股日K能力",
        "env_required": [],
    },
    {
        "source": "rss",
        "module": "zephyr.data.implementations.rss_provider",
        "class": "RSSProvider",
        "test": _probe_rss,
        "test_desc": "feedparser 36氪直连feed entries",
        "env_required": [],
    },
    {
        "source": "cls",
        "module": "zephyr.data.implementations.cls_provider",
        "class": "ClsProvider",
        "test": _probe_cls,
        "test_desc": "本地RSSHub 财联社电报 items",
        "env_required": [],
    },
    {
        "source": "eastmoney_news",
        "module": "zephyr.data.implementations.eastmoney_news_provider",
        "class": "EastmoneyNewsProvider",
        "test": _probe_eastmoney_news,
        "test_desc": "np-listapi 7x24快讯 list",
        "env_required": [],
    },
    {
        "source": "tqcenter",
        "module": "zephyr.data.implementations.tqcenter_provider",
        "class": "TQCenterProvider",
        "test": _probe_tqcenter,
        "test_desc": "tq.get_sector_list 880xxx板块列表",
        "env_required": [],
    },
]

# 内存中的最新健康状态（供 scheduler 查询）
_latest_results: dict[str, dict] = {}
_results_lock = None  # 延迟初始化


def _get_lock():
    global _results_lock
    if _results_lock is None:
        import threading

        _results_lock = threading.Lock()
    return _results_lock


def _check_env(vars_needed: list[str]) -> tuple[bool, str]:
    missing = [v for v in vars_needed if not os.environ.get(v)]
    if missing:
        return False, f"缺少环境变量: {', '.join(missing)}"
    return True, "OK"


def _run_single_check(cfg: dict) -> dict:
    """执行单个数据源的健康检查。"""
    source = cfg["source"]
    result: dict[str, Any] = {
        "source": source,
        "status": "unknown",
        "connect_ok": False,
        "test_ok": False,
        "connect_time": 0.0,
        "test_time": 0.0,
        "error": "",
        "data_count": 0,
        "test_desc": cfg["test_desc"],
        "timestamp": now_utc().isoformat(),
    }

    # 1. 环境变量检查
    if cfg.get("env_required"):
        ok, msg = _check_env(cfg["env_required"])
        if not ok:
            result["status"] = "env_missing"
            result["error"] = msg
            return result

    # 2. import provider
    try:
        mod = __import__(cfg["module"], fromlist=[cfg["class"]])
        cls = getattr(mod, cfg["class"])
    except Exception as e:  # noqa: BLE001 — 健康探针需兜底 provider 模块任意导入异常（缺失依赖/语法错误均须记 import_fail 不阻断调度器启动）
        result["status"] = "import_fail"
        result["error"] = f"导入失败: {e}"
        return result

    # 3. 实例化 + connect
    t0 = time.monotonic()
    try:
        provider = cls()
        connect_method = getattr(provider, "connect", None)
        if connect_method:
            connect_method()
        result["connect_time"] = round(time.monotonic() - t0, 2)
        result["connect_ok"] = True
    except Exception as e:  # noqa: BLE001 — 探针需兜底 provider 连接阶段任意异常（网络/认证/第三方库），记 connect_fail 不阻断
        result["connect_time"] = round(time.monotonic() - t0, 2)
        result["status"] = "connect_fail"
        result["error"] = f"连接失败: {e}"
        return result

    # 4. 测试 API 调用
    test_fn = cfg.get("test")
    if test_fn is None:
        result["status"] = "connect_only"
        return result

    t0 = time.monotonic()
    try:
        ret = test_fn(provider)
        result["test_time"] = round(time.monotonic() - t0, 2)

        if ret is None:
            result["data_count"] = 0
        elif hasattr(ret, "__len__"):
            result["data_count"] = len(ret)
        elif hasattr(ret, "empty"):
            result["data_count"] = 0 if ret.empty else len(ret)
        else:
            result["data_count"] = 1

        if result["data_count"] > 0:
            result["test_ok"] = True
            result["status"] = "healthy"
        else:
            result["status"] = "empty_data"
            result["error"] = "API 返回空数据"
    except Exception as e:  # noqa: BLE001 — 探针需兜底测试 API 调用任意异常（外部数据源行为不可枚举），记 test_fail 不阻断
        result["test_time"] = round(time.monotonic() - t0, 2)
        result["status"] = "test_fail"
        result["error"] = f"测试失败: {e}"

    return result


def _write_log(results: list[dict]) -> Path:
    """将健康检查结果写入日志文件。"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / f"source_health_{now_utc().strftime('%Y%m%d')}.log"

    lines = [
        f"{'=' * 70}",
        "  数据源健康检查报告",
        f"  时间: {now_utc().strftime('%Y-%m-%d %H:%M:%S')}",
        f"{'=' * 70}",
        "",
    ]

    for r in results:
        icon = {"healthy": "✓", "connect_only": "✓", "env_missing": "⚠"}.get(r["status"], "✗")
        detail = ""
        if r["data_count"] > 0:
            detail = f" ({r['data_count']}行, {r['test_time']}s)"
        elif r["connect_ok"]:
            detail = f" (连接OK, {r['connect_time']}s)"
        err = f" {r['error']}" if r["error"] else ""
        lines.append(f"  {icon} {r['source']:15s} {r['status']:15s}{detail}{err}")

    # 汇总
    healthy = sum(1 for r in results if r["status"] in ("healthy", "connect_only"))
    warnings = sum(1 for r in results if r["status"] == "env_missing")
    failed = sum(1 for r in results if r["status"] not in ("healthy", "connect_only", "env_missing"))
    lines.extend(
        [
            "",
            f"{'=' * 70}",
            f"  汇总: ✓正常 {healthy}  ⚠环境缺失 {warnings}  ✗异常 {failed}",
            f"{'=' * 70}",
            "",
        ]
    )

    with open(log_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return log_file


def run_source_health_check() -> dict[str, dict]:
    """执行全量数据源健康检查（供 scheduler.start() 调用）。

    Returns:
        {source_name: result_dict} 最新健康状态。
    """
    log.info("开始数据源健康检查（%d 个数据源）...", len(_HEALTH_CHECKS))

    results = []
    for cfg in _HEALTH_CHECKS:
        source = cfg["source"]
        try:
            result = _run_single_check(cfg)
        except Exception as e:  # noqa: BLE001 — 单源检查内部兜底外的最后一道防线，任一源异常不得波及其他源检查结果
            result = {
                "source": source,
                "status": "unexpected_error",
                "error": str(e),
                "connect_ok": False,
                "test_ok": False,
                "connect_time": 0,
                "test_time": 0,
                "data_count": 0,
                "test_desc": cfg["test_desc"],
                "timestamp": now_utc().isoformat(),
            }
        results.append(result)

        # 实时日志
        status = result["status"]
        if status in ("healthy", "connect_only"):
            log.info("  ✓ %s: %s", source, status)
        elif status == "env_missing":
            log.warning("  ⚠ %s: %s (%s)", source, status, result["error"])
        else:
            log.error("  ✗ %s: %s (%s)", source, status, result["error"])

    # 写日志文件
    try:
        log_file = _write_log(results)
        log.info("健康检查日志已写入: %s", log_file)
    except Exception as e:  # noqa: BLE001 — 日志落盘失败（磁盘满/权限）仅降级告警，不影响健康检查主流程返回
        log.warning("写入健康检查日志失败: %s", e)

    # 更新内存状态
    with _get_lock():
        global _latest_results
        _latest_results = {r["source"]: r for r in results}

    # 同源连续失败 streak 累计 + 超阈值告警（#ARCH-DATA-015）
    _update_failure_streaks(results)

    # 汇总
    healthy = sum(1 for r in results if r["status"] in ("healthy", "connect_only"))
    failed_list = [r["source"] for r in results if r["status"] not in ("healthy", "connect_only", "env_missing")]
    log.info(
        "数据源健康检查完成: %d/%d 正常%s",
        healthy,
        len(results),
        f"，异常: {', '.join(failed_list)}" if failed_list else "",
    )

    return _latest_results


def _recheck_single_source(source: str) -> dict | None:
    """对单个数据源执行一次健康重检并更新缓存（供 scheduler 跳过前 TTL 到期时调用）。

    仅重检 _HEALTH_CHECKS 中已注册的源；未注册返回 None。
    重检失败不影响缓存更新——新状态（含失败）同样写入 _latest_results。
    """
    cfg = next((c for c in _HEALTH_CHECKS if c["source"] == source), None)
    if cfg is None:
        return None
    log.info("健康检查缓存已过期，对源 %s 单独重检...", source)
    try:
        result = _run_single_check(cfg)
    except Exception as e:  # noqa: BLE001 — 重检异常不阻塞调度
        result = {
            "source": source,
            "status": "unexpected_error",
            "error": str(e),
            "connect_ok": False,
            "test_ok": False,
            "connect_time": 0,
            "test_time": 0,
            "data_count": 0,
            "test_desc": cfg["test_desc"],
            "timestamp": now_utc().isoformat(),
        }
    with _get_lock():
        _latest_results[source] = result
    status = result["status"]
    if status in ("healthy", "connect_only"):
        log.info("  ✓ %s 重检结果: %s", source, status)
    else:
        log.warning("  ✗ %s 重检结果: %s (%s)", source, status, result.get("error", ""))
    return result


def _health_check_age_minutes(result: dict) -> float | None:
    """计算健康检查结果距现在的分钟数；timestamp 缺失/解析失败返回 None。"""
    import datetime as _dt

    ts = result.get("timestamp")
    if not ts:
        return None
    try:
        checked_at = _dt.datetime.fromisoformat(ts)
        if checked_at.tzinfo is None:
            checked_at = checked_at.replace(tzinfo=_dt.timezone.utc)
        age = now_utc() - checked_at
        return age.total_seconds() / 60.0
    except (ValueError, TypeError):
        return None


def get_source_health(source: str) -> dict | None:
    """查询单个数据源的最新健康状态（供 scheduler 调度决策用）。

    Returns:
        最新健康状态 dict，或 None（未检查过）。
    """
    with _get_lock():
        return _latest_results.get(source)


def get_all_source_health() -> dict[str, dict]:
    """查询所有数据源的最新健康状态。"""
    with _get_lock():
        return dict(_latest_results)
