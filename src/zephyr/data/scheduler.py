# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.scheduler
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.policy_registry; zephyr.data.progress_store; zephyr.data.ch_writer; zephyr.data.ch_reader; zephyr.data.task_queue; zephyr.data.alerter; zephyr.data.implementations.{miniqmt,akshare,tushare}_provider; zephyr.data.trading_calendar; zephyr.data.local_replay; apscheduler(pip); exchange_calendars(pip)
# [CONSUMERS] CLI(zephyr.data.cli 阶段3+); main()入口
# [STARTUP] manual
# [MATURITY] production
# [INVARIANTS] APScheduler BackgroundScheduler常驻进程; 5档cron时段; DAG依赖(task_queue); per-source串行+跨源并行; 断点续传(progress_store); 失败告警(alerter); subscribe()事件订阅支持热更新
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_task失败->返回False+alerter.notify; start/stop异常->log+不抛; 所有方法返回dict/bool不抛异常
# [TESTS] tests/zephyr/data/test_scheduler.py
# [A_module] module_id=MOD-GOV-scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m02-manual  M02豁免: APScheduler常驻服务,由cli.py启动,启动后自动运行;非reconciler无需事件触发
# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 调度与任务配置 YAML
#   fields: schedules（cron 时段）+ tasks（table/source/capability/fallback_sources/dependencies/trading_day_only）
#   code: IntegratorScheduler._load_config
# - id: I2
#   name: 源健康状态缓存
#   fields: source_health_check._latest_results（healthy/test_fail + timestamp）
#   code: run_task 健康门分支（超 30min TTL 先 _recheck_single_source 单源重检再判定）
# - id: I3
#   name: 断点游标
#   fields: task_progress.last_key（上次推进到的日期键）
#   code: progress_store.get_last_key → _compute_start_date
# 层: 算法
# - id: A1
#   name_zh: ① cron 时段触发与交易日过滤
#   name_en: _run_schedule_callback
#   intro: APScheduler cron 触发时段批次；trading_day_only 任务非 A 股交易日跳过
#   inputs: I1
#   outputs: 本时段待执行任务清单
# - id: A2
#   name_zh: ② DAG 就绪并行调度
#   name_en: _run_schedule_dag
#   intro: TaskQueue 按 dependencies 拓扑出就绪任务，per-source 串行 + 跨源并行（线程池），未就绪任务阻塞等待
#   inputs: I1
#   outputs: 各任务 run_task 调用
# - id: A3
#   name_zh: ③ 单任务执行链（健康门→主源→fallback→重试→写库→游标）
#   name_en: run_task/_try_source/_fetch_and_write
#   intro: 健康门（含 TTL 重检）→主源 fetch 流→按 error_classifier 不可恢复判定切 fallback→call_with_policy 按 policies.retry_on 重试→流式写 ClickHouse→推进 last_key→FAILED 经 alerter 告警
#   inputs: I2 I3
#   outputs: CH 目标表行 + task_progress/task_runs 状态
# 层: 输出
# - id: O1
#   name_zh: 数据落库与进度面
#   name_en: CH rows + progress_store
#   intro: ClickHouse 目标表行写入；SQLite task_progress.last_key 游标 + task_runs 运行记录；subscribe() 事件回调（config_changed/shutdown/task_completed）
"""数据源调度编排层（MOD-L00-004 §6）。

APScheduler 常驻进程，按 cron 时段触发任务批次，管理 DAG 依赖，
调用 Provider 拉数据，写入 ClickHouse，记录进度，失败告警。

核心组件：
- IntegratorScheduler：封装 APScheduler + TaskQueue + ProgressStore + Alerter
- 5 档调度时段（蓝图 §6.2）：盘后日K 16:30 / 盘后资金 17:00 / 盘后事件 18:00 / 周末财务 周六10:00 / 静态数据 月初09:00
- DAG 依赖（蓝图 §6.3）：adj_factor -> kline_daily_hfq；kline_daily -> daily_valuation
- 并发控制（蓝图 §6.4）：per-source 串行（heavy 池 2 线程），跨源并行（default 池 8 线程）

事件订阅（满足永久系统全自动要求）：
- subscribe(event, handler)：注册事件处理器
- 支持事件：config_changed（策略热更新）/ shutdown（优雅关闭）/ task_completed（任务完成回调）
"""

from __future__ import annotations

import datetime
import http.server
import json
import logging
import threading
import time
from pathlib import Path
from socketserver import ThreadingMixIn
from typing import Any, Callable

from zephyr.data import local_replay
from zephyr.data.alerter import LEVEL_CRITICAL, LEVEL_ERROR, Alerter
from zephyr.data.buffered_writer import BufferedWriter
from zephyr.data.metrics import IntegratorMetrics, get_metrics
from zephyr.data.policy_registry import PolicyRegistry, get_registry
from zephyr.data.progress_store import ProgressStore, get_store
from zephyr.data.provider_base import FetchPayload, FetchResult, IngestProviderBase
from zephyr.data.task_queue import FAILED, PENDING, RUNNING, SUCCESS, TaskQueue
from zephyr.data.trading_calendar import TRADING_DAY_GUARDED_SCHEDULES, is_trading_day
from zephyr.shared.io.paths import REPO_ROOT

from . import (
    ch_reader,  # 健康检查走 ch_reader 自动注入 FINAL（裁定 #ARCH-CH-007）
    ch_writer,  # 相对导入：避免 depgraph 记录到 zephyr.data 包节点导致循环（裁定#213）
)

log = logging.getLogger(__name__)

_DEFAULT_CONFIG_DIR = Path(__file__).parent / "config"
_DEFAULT_JOBS_DB = "sqlite:///" + str(REPO_ROOT / "data" / "integrator_jobs.db")

# SQL 模板常量（NO-BARE-SQL gate 豁免：_SQL_* 前缀，裁定 #ARCH-CH-015）
_SQL_FIND_PART = "SELECT database, table FROM system.parts WHERE name='{part_name}' AND active=1 LIMIT 1"
_SQL_STOP_MERGES = "SYSTEM STOP MERGES"
_SQL_START_MERGES = "SYSTEM START MERGES"
_SQL_DETACH_PART = "ALTER TABLE {db}.{table} DETACH PART '{part_name}'"
_SQL_TEXT_LOG_CHECKSUM = (
    "SELECT message FROM system.text_log "
    "WHERE event_time > now() - INTERVAL 1 HOUR "
    "AND level <= 3 AND message ILIKE '%Checksum%' "
    "ORDER BY event_time DESC LIMIT 2000"
)

# 模块级调度器单例（供 APScheduler job 回调使用，避免 pickle 绑定方法+Lock 对象）
_global_scheduler: IntegratorScheduler | None = None

# 调度周期串行化锁（裁定 #ARCH-CH-016）
# 根因：_run_schedule_dag 第155行 scheduler._task_queue = TaskQueue() 会重新创建队列，
# 多个调度周期并发时（如 event_driven 每15分钟 + daily_event 19:00 同时触发），
# 后创建的队列覆盖前一个，导致正在执行的任务 mark_completed 时抛 KeyError('未知 task_id')。
# 修复：全局锁确保同一时间只有一个调度周期在操作 _task_queue。
_schedule_dag_lock = threading.Lock()


def _run_schedule_callback(schedule_name: str) -> None:
    """APScheduler job 回调（模块级函数，可 pickle）。

    APScheduler 的 SQLAlchemyJobStore 用 pickle 序列化 job 状态，
    绑定方法 self.run_schedule 会 pickle 整个实例（含 _provider_lock），
    导致 "cannot pickle '_thread.RLock' object"。
    改用模块级函数 + 全局单例避免此问题。
    """
    if _global_scheduler is not None:
        _global_scheduler.run_schedule(schedule_name)
    else:
        log.error("_run_schedule_callback: _global_scheduler 未设置")


def _schedule_should_skip(schedule_name: str, sched_config: dict) -> bool:
    """交易日历守卫 + interval 时间窗口过滤。返回 True 表示该时段应跳过（返回空字典）。

    - 交易日历守卫：盘中/盘后/夜间/巡检时段在非交易日（节假日/调休）自动跳过
    - interval trigger 时间窗口过滤（集合竞价等高频场景）：
      IntervalTrigger 会 7×24 每隔 N 秒触发，需在此过滤非交易时段
    """
    if schedule_name in TRADING_DAY_GUARDED_SCHEDULES:
        today = datetime.date.today()
        if not is_trading_day(today):
            log.info("时段 %s 跳过：今日(%s)非A股交易日", schedule_name, today)
            return True
    if sched_config.get("type") == "interval":
        now = datetime.datetime.now()
        # 周末不执行（0=周一 ... 6=周日）
        if now.weekday() >= 5:
            return True
        # 时间窗口检查（如 9:15-9:25）
        start_time = sched_config.get("start_time")
        end_time = sched_config.get("end_time")
        if start_time and end_time:
            now_str = now.strftime("%H:%M:%S")
            if not (start_time <= now_str <= end_time):
                return True
    return False


def _run_special_schedule(
    scheduler: IntegratorScheduler,
    schedule_name: str,
) -> dict[str, bool] | None:
    """处理 weekend_backfill / daily_backfill / integrity_check 特殊时段。

    返回结果字典表示已处理；返回 None 表示非特殊时段，交给常规 DAG 流程。
    """
    # L10 周末补下载层：不走常规 run_task，调用 backfill_checker 独立处理
    if schedule_name == "weekend_backfill":
        from zephyr.data.backfill_checker import run_weekend_backfill

        result = run_weekend_backfill(scheduler)
        return {"tick_backfill_weekly": result.get("success", False)}
    # L10.5 每日盘后补下载层：检测当日缺口并补下载（治本 #ARCH-DATA-TICK-GAP-001）
    if schedule_name == "daily_backfill":
        from zephyr.data.backfill_checker import run_daily_backfill

        result = run_daily_backfill(scheduler)
        return {"daily_backfill": result.get("success", False)}
    # 每日数据完整性巡检：动态发现全表，检测当日数据是否达标
    if schedule_name == "integrity_check":
        from zephyr.data.integrity_checker import run_daily_check

        result = run_daily_check(scheduler)
        return {"integrity_check_daily": result.get("success", False)}
    return None


def _filter_schedule_tasks(tasks: list[dict], schedule_name: str) -> list[dict]:
    """过滤该时段的任务。

    跳过规则：
    - extra.disabled=true：退役/暂停任务
    - extra.trading_day_only=true 且今日非交易日：miniqmt 等依赖 QMT 服务器的任务
      （QMT 服务器周末/节假日非交易时段拒绝连接，error 10061 WSAECONNREFUSED，
       见 schedule.yaml L8 注释与蓝图 §6.2.1）

    拼写防护：miniqmt 源任务在非交易日历守卫时段（如 monthly_static）若缺少
    trading_day_only 字段（含拼写错误如 trade_day_only），会在此告警。
    """
    today = datetime.date.today()
    is_trading = is_trading_day(today)
    result = []
    for t in tasks:
        if t.get("schedule") != schedule_name:
            continue
        extra = t.get("extra") or {}
        if extra.get("disabled"):
            continue
        # 拼写防护：miniqmt 任务在非守卫时段必须有 trading_day_only
        source = t.get("source", "")
        if (
            source == "miniqmt"
            and schedule_name not in TRADING_DAY_GUARDED_SCHEDULES
            and extra.get("trading_day_only") is not True
        ):
            log.warning(
                "任务 %s（source=miniqmt, schedule=%s）缺少 trading_day_only: true，"
                "非交易日将触发 QMT error 10061。请检查字段拼写是否正确。",
                t.get("task_id"),
                schedule_name,
            )
        if extra.get("trading_day_only") and not is_trading:
            log.info("任务 %s 跳过：trading_day_only 且今日(%s)非交易日", t.get("task_id"), today)
            continue
        result.append(t)
    return result


def _run_schedule_dag(
    scheduler: IntegratorScheduler,
    schedule_name: str,
    schedule_tasks: list[dict],
) -> dict[str, bool]:
    """加载任务到 TaskQueue，按 DAG 顺序并行执行，并汇总结果与失败率。

    线程安全：每个调度周期使用独立的局部 TaskQueue（裁定 #ARCH-CH-016 v2）。
    原方案用 _schedule_dag_lock 全局锁串行化所有调度周期，但导致 intraday_sector
    等独立执行器的时段被 intraday_realtime（5+分钟）阻塞，独立执行器形同虚设。
    新方案：局部 task_queue + 参数传递，各调度周期互不干扰，无需全局锁。

    动态调度（治本修复 #ARCH-DAG-DYNAMIC-SCHEDULING，2026-07-23）：
    原方案为批次同步——提交所有就绪任务到线程池，等待全部完成后再查下一批。
    导致长任务（如 stock_indicator 60+分钟）阻塞短任务（adj_factor 4分钟）的
    依赖者（kline_daily_hfq）无法及时启动。新方案用 FIRST_COMPLETED 动态调度：
    任务完成后立即检查并提交新就绪的依赖任务，无需等待同批次其他任务完成。
    """
    # 局部 TaskQueue——每个调度周期独立，避免并发调度互相覆盖（裁定 #ARCH-CH-016 v2）
    task_queue = TaskQueue()
    for t in schedule_tasks:
        task_queue.add_task(t)

    # 动态调度——FIRST_COMPLETED 模式：任务完成后立即提交新就绪的依赖任务
    from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait

    results: dict[str, bool] = {}
    max_workers = 8

    # 初始就绪任务
    ready = task_queue.get_ready_tasks()
    if not ready:
        blocked = task_queue.list_by_status("BLOCKED")
        if blocked:
            log.warning("时段 %s 有 %d 个 BLOCKED 任务", schedule_name, len(blocked))
        log.info("时段 %s 完成: 0 成功, 0 失败", schedule_name)
        return results

    submitted: set[str] = set()
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        future_map: dict = {}
        for tid in ready:
            future_map[pool.submit(scheduler.run_task, tid, task_queue=task_queue)] = tid
            submitted.add(tid)

        # 动态循环：任务完成即检查并提交新就绪的依赖任务
        while future_map:
            done, _ = wait(future_map.keys(), return_when=FIRST_COMPLETED)
            for future in done:
                tid = future_map.pop(future)
                try:
                    results[tid] = future.result()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    log.error("任务 %s 并行执行异常: %s", tid, e, exc_info=True)
                    results[tid] = False

            # 刚完成的任务可能解锁了依赖者——立即检查并提交
            if not task_queue.is_done():
                new_ready = task_queue.get_ready_tasks()
                for tid in new_ready:
                    if tid not in submitted:
                        future_map[pool.submit(scheduler.run_task, tid, task_queue=task_queue)] = tid
                        submitted.add(tid)

    # 检查 BLOCKED 任务（前置失败的下游任务）
    blocked = task_queue.list_by_status("BLOCKED")
    if blocked:
        log.warning("时段 %s 有 %d 个 BLOCKED 任务: %s", schedule_name, len(blocked), blocked)

    # 汇总
    success_count = sum(1 for v in results.values() if v)
    failed_count = len(results) - success_count
    log.info("时段 %s 完成: %d 成功, %d 失败", schedule_name, success_count, failed_count)

    # 检查失败率
    if results:
        scheduler._alerter.check_daily_failure_rate(len(results), failed_count)

    return results


class IntegratorScheduler:
    """数据源集成器调度器。

    用法：
        sched = IntegratorScheduler()
        sched.start()  # 启动常驻进程，按 cron 自动触发

        # 手动执行单个任务
        sched.run_task("kline_daily_incremental")

        # 手动执行某时段所有任务
        sched.run_schedule("daily_kline")

        sched.stop()  # 优雅关闭
    """

    def __init__(
        self,
        config_dir: str | Path | None = None,
        progress_db: str | Path | None = None,
        jobs_db: str | None = None,
        startup_probes: bool = True,
    ):
        """初始化调度器。

        Args:
            config_dir: 配置目录（含 schedule.yaml/tasks.yaml/policies.yaml）
            progress_db: SQLite 进度库路径
            jobs_db: APScheduler jobstore URL
            startup_probes: 启动时是否执行 live 网络探针（数据源健康检查/CH 探活/破损 part 检测）。
                生产默认 True；测试必须传 False 隔离环境噪声（#ARCH-DATA-015：
                baostock 黑名单经 filterwarnings=error 放大为单测失败的事故治本）。
        """
        self._config_dir = Path(config_dir) if config_dir else _DEFAULT_CONFIG_DIR
        self._jobs_db = jobs_db or _DEFAULT_JOBS_DB
        # 组件
        self._policy_registry: PolicyRegistry = get_registry()
        self._progress_store: ProgressStore = get_store(progress_db)
        # Phase 3-B 治本修复：调度器初始化时清理上次崩溃留下的卡死 RUNNING 任务（>24h）
        # 防止僵尸任务状态阻塞断点续传判断（get_last_key 返回 RUNNING 但实际进程已死）
        try:
            reaped = self._progress_store.reap_stale_runs(max_age_hours=24)
            if reaped:
                import logging

                logging.getLogger(__name__).warning(
                    "调度器启动时清理了 %d 个卡死任务（RUNNING > 24h，可能是上次进程崩溃）",
                    len(reaped),
                )
        except Exception:  # noqa: BLE001 — 5.135治标: 不阻塞调度器启动
            pass
        self._alerter = Alerter()
        self._task_queue = TaskQueue()
        self._metrics: IntegratorMetrics = get_metrics()
        self._providers: dict[str, IngestProviderBase] = {}
        self._provider_lock = threading.Lock()
        # APScheduler 实例（懒初始化）
        self._scheduler = None
        self._started = False
        self._startup_probes = startup_probes
        # 配置缓存
        self._schedules: dict[str, dict] = {}
        self._tasks: list[dict] = []
        # 事件订阅（永久系统须有事件订阅）
        self._event_handlers: dict[str, list[Callable]] = {
            "config_changed": [],
            "shutdown": [],
            "task_completed": [],
        }
        # ClickHouse 健康探活缓存（裁定 #ARCH-CH-011）
        # /health 端点禁止同步阻塞式 DB 查询，改为后台探活线程定期更新缓存
        # get_health() 只读缓存（非阻塞），保证 100ms 内响应
        self._ch_health_cache: dict[str, Any] = {"status": "unknown", "last_check": 0.0, "latency_ms": 0}
        self._ch_health_lock = threading.Lock()
        self._ch_health_interval = 30  # 秒：每 30 秒探活一次
        # CH 探活告警状态（R4a，#ARCH-DR-CH-RESTART-001）：
        # 连续失败达阈值才告警（防单次抖动误报），状态变化时才触发（防重复刷屏）
        self._ch_probe_fail_count = 0
        self._ch_probe_alerted_dead = False  # 是否已发过 DEAD 告警（去重）
        # 卡死任务定期清理（Phase 3-B 治本修复 v2）
        # 启动时清理 >24h 的历史僵尸任务，运行中每小时清理 >6h 的卡死任务
        self._stale_reap_interval = 3600  # 秒：每小时 reap 一次
        self._stale_reap_max_age_hours = 6  # 运行中 reap 阈值：6 小时
        # 注册内部默认事件处理器（config_changed -> 策略热更新）
        self.subscribe("config_changed", self._on_config_changed)

    # ── Stage 4 公共化（2026-07-28）：properties + 公共方法 ──
    # 消除 tests/zephyr/data/test_scheduler.py 中 63 处私有成员访问。

    @property
    def providers(self) -> dict:
        """只读：providers（Stage 4 公共化）。"""
        return self._providers

    @providers.setter
    def providers(self, value):
        """写入：providers（Stage 4 公共化）。"""
        self._providers = value

    @property
    def started(self) -> bool:
        """读写：调度器是否已启动（Stage 4 公共化）。"""
        return self._started

    @started.setter
    def started(self, value: bool) -> None:
        self._started = value

    @property
    def scheduler(self):
        """读写：APScheduler 实例（Stage 4 公共化）。"""
        return self._scheduler

    @scheduler.setter
    def scheduler(self, value) -> None:
        self._scheduler = value

    @property
    def progress_store(self):
        """只读：progress_store（Stage 4 公共化）。"""
        return self._progress_store

    @progress_store.setter
    def progress_store(self, value):
        """写入：progress_store（Stage 4 公共化）。"""
        self._progress_store = value

    @property
    def tasks(self) -> list:
        """只读：tasks（Stage 4 公共化）。"""
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        """写入：tasks（Stage 4 公共化）。"""
        self._tasks = value

    @property
    def event_handlers(self) -> dict:
        """只读：event_handlers（Stage 4 公共化）。"""
        return self._event_handlers

    @event_handlers.setter
    def event_handlers(self, value):
        """写入：event_handlers（Stage 4 公共化）。"""
        self._event_handlers = value

    @property
    def schedules(self) -> dict:
        """只读：schedules（Stage 4 公共化）。"""
        return self._schedules

    @schedules.setter
    def schedules(self, value):
        """写入：schedules（Stage 4 公共化）。"""
        self._schedules = value

    @property
    def policy_registry(self):
        """只读：policy_registry（Stage 4 公共化）。"""
        return self._policy_registry

    @policy_registry.setter
    def policy_registry(self, value):
        """写入：policy_registry（Stage 4 公共化）。"""
        self._policy_registry = value

    # ============== 事件订阅 ==============

    def subscribe(self, event: str, handler: Callable) -> None:
        """订阅事件。

        支持的事件：
        - config_changed：配置变更（触发策略热更新）
        - shutdown：系统关闭（触发优雅停止）
        - task_completed：任务完成（回调通知）

        Args:
            event: 事件名
            handler: 事件处理函数
        """
        self._event_handlers.setdefault(event, []).append(handler)
        log.info("已订阅事件 %s，handler=%s", event, handler.__name__)

    def emit_event(self, event: str, *args, **kwargs) -> None:
        """触发事件（调用所有订阅者）。异常不抛出（Stage 4 公共化，primary）。"""
        for handler in self._event_handlers.get(event, []):
            try:
                handler(*args, **kwargs)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("事件 %s handler 异常: %s", event, e)

    def _emit_event(self, event: str, *args, **kwargs) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        self.emit_event(event, *args, **kwargs)

    def _on_config_changed(self, **kwargs) -> None:
        """config_changed 事件默认处理器：策略热更新。"""
        try:
            self._policy_registry.maybe_reload(force=True)
            log.info("config_changed 事件触发策略热更新")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("config_changed 事件处理异常: %s", e)

    # ============== ClickHouse 健康探活（裁定 #ARCH-CH-011） ==============

    def _start_ch_health_probe(self) -> None:
        """启动 ClickHouse 健康探活后台守护线程。

        问题背景：/health 端点原同步调用 ch_reader.query("SELECT 1")，
        当 ClickHouse 连接异常时二级降级链（TCP→HTTP）逐个超时，
        最坏情况 _DEFAULT_TIMEOUT=600s，导致 /health 请求阻塞 10 分钟。

        治本方案（裁定 #ARCH-CH-011）：
        - 后台守护线程每 _ch_health_interval 秒探活一次
        - 探活用独立短超时 timeout=3（禁止使用 _DEFAULT_TIMEOUT=600）
        - get_health() 只读缓存（非阻塞），保证 100ms 内响应
        - 缓存超过 3 个间隔未更新 → 判定探活线程死亡
        """

        def _probe_loop() -> None:
            # CH 探活告警阈值（连续失败次数，与 HeartbeatMonitor 对齐）
            ch_probe_fail_threshold = 3
            while self._started:
                t0 = time.time()
                probe_ok = False
                try:
                    result = ch_reader.query("SELECT 1", timeout=3)
                    latency = (time.time() - t0) * 1000
                    probe_ok = bool(result.strip())
                    with self._ch_health_lock:
                        self._ch_health_cache = {
                            "status": "ok" if probe_ok else "error: empty response",
                            "last_check": time.time(),
                            "latency_ms": round(latency, 1),
                        }
                except Exception as e:  # noqa: BLE001 — CH 探活降级：缓存 error 状态，细节入日志
                    latency = (time.time() - t0) * 1000
                    with self._ch_health_lock:
                        # 5.168治本（#ARCH-SEC-001）：异常详情不经 /health 跨信任边界外发，细节入日志
                        self._ch_health_cache = {
                            "status": "error",
                            "last_check": time.time(),
                            "latency_ms": round(latency, 1),
                        }
                    log.warning("CH 健康探活失败: %s", e, exc_info=True)

                # ── CH 探活告警（R4a，#ARCH-DR-CH-RESTART-001）──
                # 连续失败达阈值才告警（防单次抖动），状态变化才触发（防刷屏）。
                # alerter.notify 内部有 300s 冷却 + 通道吞异常，不影响探活主流程。
                if probe_ok:
                    self._ch_probe_fail_count = 0
                    if self._ch_probe_alerted_dead:
                        # 恢复通知（DEAD→ALIVE）
                        self._ch_probe_alerted_dead = False
                        try:
                            self._alerter.notify(
                                task_id="ch_health_probe",
                                error="CH 健康探活已恢复（SELECT 1 成功），服务可达。",
                                level="INFO",
                                source="clickhouse",
                            )
                        except Exception:  # noqa: BLE001
                            pass
                else:
                    self._ch_probe_fail_count += 1
                    if self._ch_probe_fail_count >= ch_probe_fail_threshold and not self._ch_probe_alerted_dead:
                        self._ch_probe_alerted_dead = True
                        try:
                            self._alerter.notify(
                                task_id="ch_health_probe",
                                error=(
                                    f"CH 健康探活连续 {self._ch_probe_fail_count} 次失败"
                                    f"（间隔 {self._ch_health_interval}s，约 "
                                    f"{self._ch_probe_fail_count * self._ch_health_interval}s），"
                                    f"服务不可达。灾时若在实盘运行期将导致数据中断，"
                                    f"请立即检查 CH 服务状态（systemctl status clickhouse-server）。"
                                ),
                                level="CRITICAL",
                                source="clickhouse",
                            )
                        except Exception:  # noqa: BLE001
                            pass
                # 等待下次探活（用 Event 实现可中断的 sleep 更优雅，但此处简单实现）
                time.sleep(self._ch_health_interval)

        t = threading.Thread(target=_probe_loop, daemon=True, name="ch-health-probe")
        t.start()
        log.info("ClickHouse 健康探活线程已启动（间隔 %ds，timeout=3s）", self._ch_health_interval)

    # ============== 卡死任务定期清理（Phase 3-B 治本修复 v2） ==============

    def _start_stale_reaper(self) -> None:
        """启动卡死任务定期清理后台守护线程。

        问题背景：
        - 原 reap_stale_runs 仅在调度器启动时执行一次
        - 阈值 24h 太长，任务卡死可能长时间无人发现
        - 若调度器运行中任务因异常卡住（如网络超时、死循环），
          RUNNING 状态会永久残留，影响断点续传判断

        治本方案：
        - 后台守护线程每 _stale_reap_interval 秒 reap 一次
        - 阈值 _stale_reap_max_age_hours 小时（默认 6h）
        - 启动时已用 24h 阈值清理过历史遗留，运行中用更严格的 6h
        - 6h 阈值依据：全市场最长任务（财务/研报）通常 2-4h，
          超过 6h 基本可判定为卡死
        """

        def _reap_loop() -> None:
            while self._started:
                time.sleep(self._stale_reap_interval)
                try:
                    reaped = self._progress_store.reap_stale_runs(max_age_hours=self._stale_reap_max_age_hours)
                    if reaped:
                        n = len(reaped)
                        task_ids = [r["task_id"] for r in reaped]
                        log.warning(
                            "定期清理：发现并清理了 %d 个卡死任务（RUNNING > %dh）: %s",
                            n,
                            self._stale_reap_max_age_hours,
                            task_ids,
                        )
                        # 告警触达（#ARCH-DATA-PIPELINE-001 B-卡死治理）：
                        # 飞书 webhook / SMTP 邮件（未配置则静默跳过，不影响主流程）
                        self._alerter.notify(
                            "_stale_reaper",
                            f"清理了 {n} 个卡死任务（RUNNING > {self._stale_reap_max_age_hours}h）: "
                            f"{', '.join(task_ids)}",
                            level=LEVEL_CRITICAL,
                            extra={"reaped_tasks": task_ids, "threshold_hours": self._stale_reap_max_age_hours},
                        )
                except Exception as e:  # noqa: BLE001 — 不影响主循环
                    log.error("定期清理卡死任务异常: %s", e)

        t = threading.Thread(target=_reap_loop, daemon=True, name="stale-reaper")
        t.start()
        log.info(
            "卡死任务定期清理线程已启动（间隔 %ds，阈值 %dh）",
            self._stale_reap_interval,
            self._stale_reap_max_age_hours,
        )

    # ============== 本地落盘回灌（裁定 #ARCH-CH-013 Phase 1） ==============

    def _start_local_replay(self) -> None:
        """启动本地落盘回灌后台守护线程。

        问题背景：CH/VM 不可达时 ch_writer.write_tsv 二级降级链全部失败，
        数据写入 data/local_fallback/*.tsv 本地文件（local_replay.save_fallback）。
        若不回灌，数据将永久滞留本地，造成数据丢失。

        治本方案（裁定 #ARCH-CH-013 Phase 1）：
        - 启动后台守护线程，每 30 分钟检查并回灌积压文件
        - 启动时立即检查一次（避免启动后 30 分钟空窗）
        - 回灌复用 ch_writer.write_tsv（CH 可用时立即成功）
        - 单次回灌上限 100 文件（避免长时间阻塞）
        """

        def _replay_loop() -> None:
            # 启动时立即检查一次
            try:
                if local_replay.has_backlog():
                    summary = local_replay.get_backlog_summary()
                    log.info("local_replay: 启动时检测到积压 %s，开始回灌", summary)
                    local_replay.replay_batch(max_files=100)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("local_replay: 启动时回灌异常: %s", e)

            while self._started:
                time.sleep(1800)  # 30 分钟
                try:
                    if local_replay.has_backlog():
                        result = local_replay.replay_batch(max_files=100)
                        log.info("local_replay: 周期回灌 %s", result)
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    log.error("local_replay: 周期回灌异常: %s", e)

        t = threading.Thread(target=_replay_loop, daemon=True, name="local-replay")
        t.start()
        log.info("本地落盘回灌线程已启动（间隔 1800s）")

    # ============== 破损 part 自动检测+隔离（裁定 #ARCH-CH-015） ==============

    def _start_corrupted_part_detector(self) -> None:
        """启动破损 part 自动检测+隔离守护线程（裁定 #ARCH-CH-015）。

        问题背景：CH 崩溃时正在写入的 data part 被零字节覆盖，
        形成 checksum 损坏的 active part。CH 后台 merge 线程反复尝试合并
        包含这些 part 的任务，失败数百次（CHECKSUM_DOESNT_MATCH 718 次，
        tmp_merge 清理 5142 次），形成无限循环，消耗大量 CPU/IO，
        致 scheduler 探针超时。

        Phase 0 未覆盖原因：Phase 0 清理的是"启动时检测到的 broken-on-start
        part"，但 checksum 损坏的 part 在启动时不验证数据完整性，只在 merge
        读取时才发现。

        治本方案（裁定 #ARCH-CH-015，Hyper-V 迁移后修订 2026-07-16）：
        - 后台守护线程每 5 分钟查询 system.text_log 中 CHECKSUM_DOESNT_MATCH
          （替代原 WSL subprocess tail err.log，通过 ch_reader 统一查询通道）
        - 检测到破损 part 后自动隔离：
          1. SYSTEM STOP MERGES（防止 merge 线程继续重试）
          2. ALTER TABLE ... DETACH PART（CH 原生方式隔离破损 part 到 detached/）
          3. SYSTEM START MERGES（恢复正常 merge）
          4. 写入审计日志 + 告警
        - 单次检测周期只处理一个破损 part（避免并发操作冲突）
        - 处理后冷却 10 分钟（避免频繁操作）
        - 已处理的 part 名称记录在内存集合中（避免重复处理）
        """
        import re as _re

        _CHECK_INTERVAL = 300  # 5 分钟
        _COOLDOWN = 600  # 处理后冷却 10 分钟
        _AUDIT_LOG = REPO_ROOT / "data" / "local_fallback" / "corrupted_parts_audit.jsonl"

        # text_log 中 CHECKSUM_DOESNT_MATCH 检测 + part 名称提取
        _CHECKSUM_PATTERN = _re.compile(r"Checksum doesn't match", _re.IGNORECASE)
        _PART_PATTERN = _re.compile(r"part\s+(\d{6}_[\w]+)", _re.IGNORECASE)
        # part 名称安全校验（防 SQL 注入）
        _PART_NAME_SAFE_RE = _re.compile(r"^[a-zA-Z0-9_-]+$")

        def _query_corrupted_log_entries() -> str:
            """查询 system.text_log 中最近 1 小时的 Checksum 错误日志。"""
            try:
                return ch_reader.query(_SQL_TEXT_LOG_CHECKSUM, timeout=15)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("查询 system.text_log 异常: %s", e)
                return ""

        def _detect_corrupted_parts(log_text: str) -> list[str]:
            """从 text_log 查询结果中提取破损 part 名称列表。"""
            if not log_text or not _CHECKSUM_PATTERN.search(log_text):
                return []
            parts: list[str] = []
            for match in _PART_PATTERN.finditer(log_text):
                name = match.group(1)
                if name and name not in parts and _PART_NAME_SAFE_RE.match(name):
                    parts.append(name)
            return parts

        def _find_part(part_name: str) -> tuple[str, str] | None:
            """查询 part 所属的 (database, table)，None 表示 part 不在 active 列表。"""
            try:
                result = ch_reader.query(
                    _SQL_FIND_PART.format(part_name=part_name),
                    timeout=10,
                )
                result = result.strip()
                if not result:
                    return None
                cols = result.split("\t")
                if len(cols) >= 2:
                    return cols[0], cols[1]
                return None
            except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
                return None

        def _isolate_part(part_name: str, db: str, table: str) -> bool:
            """隔离破损 part：STOP MERGES → DETACH PART → START MERGES → 验证。"""
            ch_reader.query(_SQL_STOP_MERGES, timeout=10)
            log.warning("已 SYSTEM STOP MERGES（隔离 %s.%s part %s）", db, table, part_name)
            time.sleep(2)

            ch_reader.query(
                _SQL_DETACH_PART.format(db=db, table=table, part_name=part_name),
                timeout=30,
            )
            time.sleep(3)

            ch_reader.query(_SQL_START_MERGES, timeout=10)
            log.info("已 SYSTEM START MERGES（隔离完成）")

            # 验证 part 已不在 active 列表
            return _find_part(part_name) is None

        def _write_audit(part_name: str, db: str, table: str, success: bool) -> None:
            """写入审计日志到 data/local_fallback/corrupted_parts_audit.jsonl。"""
            try:
                _AUDIT_LOG.parent.mkdir(parents=True, exist_ok=True)
                entry = {
                    "timestamp": datetime.datetime.now().isoformat(),
                    "part_name": part_name,
                    "database": db,
                    "table": table,
                    "action": "detach",
                    "success": success,
                }
                with open(_AUDIT_LOG, "a", encoding="utf-8") as f:
                    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("写入审计日志失败: %s", e)

        def _detect_loop() -> None:
            processed_parts: set[str] = set()
            last_action_time: float = 0.0

            while self._started:
                # 冷却期跳过
                if time.time() - last_action_time < _COOLDOWN:
                    time.sleep(_CHECK_INTERVAL)
                    continue

                try:
                    log_text = _query_corrupted_log_entries()
                    corrupted = _detect_corrupted_parts(log_text)

                    if not corrupted:
                        time.sleep(_CHECK_INTERVAL)
                        continue

                    new_parts = [p for p in corrupted if p not in processed_parts]
                    if not new_parts:
                        time.sleep(_CHECK_INTERVAL)
                        continue

                    target = new_parts[0]
                    log.error(
                        "检测到破损 part: %s（共 %d 个未处理，本次处理 1 个）",
                        target,
                        len(new_parts),
                    )

                    location = _find_part(target)
                    if location is None:
                        log.info("part %s 已不在 active 列表，跳过", target)
                        processed_parts.add(target)
                        time.sleep(_CHECK_INTERVAL)
                        continue

                    db, table = location
                    success = _isolate_part(target, db, table)

                    _write_audit(target, db, table, success)
                    self._alerter.notify(
                        "corrupted_part_isolated",
                        f"破损 part 已隔离: {db}.{table} {target} (success={success})",
                        level=LEVEL_CRITICAL,
                        source="corrupted_part_detector",
                    )

                    processed_parts.add(target)
                    last_action_time = time.time()

                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    log.error("破损 part 检测线程异常: %s", e)

                time.sleep(_CHECK_INTERVAL)

        t = threading.Thread(target=_detect_loop, daemon=True, name="corrupted-part-detector")
        t.start()
        log.info("破损 part 检测线程已启动（间隔 %ds，冷却 %ds）", _CHECK_INTERVAL, _COOLDOWN)

    # ============== 配置加载 ==============

    def load_config(self) -> None:
        """加载 schedule.yaml + tasks.yaml（Stage 4 公共化，primary）。"""
        import yaml

        # 加载调度计划
        schedule_path = self._config_dir / "schedule.yaml"
        if schedule_path.exists():
            with open(schedule_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            self._schedules = data.get("schedules", {})
            log.info("已加载调度计划: %d 档时段", len(self._schedules))
        else:
            log.warning("调度计划不存在: %s", schedule_path)

        # 加载任务清单
        tasks_path = self._config_dir / "tasks.yaml"
        if tasks_path.exists():
            with open(tasks_path, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            self._tasks = data.get("tasks", [])
            log.info("已加载任务清单: %d 个任务", len(self._tasks))
        else:
            log.warning("任务清单不存在: %s", tasks_path)

        # 裁定 #ARCH-CH-024 Phase 2: 表名消费闭环校验
        # 校验 tasks.yaml.table ⊆ business_data_categories.yaml（表名/品类真源），
        # 不一致仅 WARN（不阻断启动，渐进式收紧；Phase 4 commit gate 将升级为 block）。
        # 消除"tasks.yaml + registry 双真源漂移"风险（声明闭环→消费闭环）。
        try:
            from zephyr.data.table_registry import get_registry

            registry = get_registry()
            warnings = registry.validate_tasks_yaml(self._tasks)
            for w in warnings:
                log.warning("[TableRegistry] %s", w)
            if warnings:
                log.warning("[TableRegistry] tasks.yaml 与品类真源有 %d 处不一致", len(warnings))
            else:
                log.info("[TableRegistry] tasks.yaml 表名与品类真源一致")
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.warning("[TableRegistry] 表名校验失败（不阻断启动）: %s", e)

    def _load_config(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        self.load_config()

    def reload_policies(self) -> bool:
        """热更新策略（手动调用或 config_changed 事件触发）。"""
        return self._policy_registry.maybe_reload(force=True)

    def _validate_capability_contracts(self) -> None:
        """启动时校验 task.capability 与 provider 行为契约一致性（裁定 #ARCH-CH-022）。

        把"注释契约"升级为"机器可执行契约"。从 tasks.yaml 读取所有涉及的 source，
        通过 Provider 类的 meta 类属性（无需实例化）校验 task 声明与契约一致性。

        Phase 4.3（裁定 #ARCH-CH-022 延伸）：追加 provider 路由-meta 一致性校验，
        AST 解析 provider 文件，对比"fetch 路由能力集"与"meta.capabilities 声明集"，
        不一致则 WARN 纳入日志（治本本次 8 条 ERROR 根因：路由支持但 meta 遗漏声明）。
        Phase 4.4 的 commit gate 把同一检查升级为 ERROR 阻断；运行时此处保持 WARN
        以免阻断已在运行的生产实例（渐进式收紧）。

        - ERROR 级违规 → raise（阻断启动，fail-closed）
        - WARN 级违规 → log.warning（记录但不阻断，渐进式收紧）
        """
        from zephyr.data.capability_validator import (
            check_route_meta_consistency,
            format_violations,
            has_blocking_violations,
            validate_task_capability_contracts,
        )

        # 收集 tasks 涉及的所有 source，通过类属性读取 meta（无需实例化）
        metas: dict[str, Any] = {}
        source_to_meta = {
            "akshare": ("zephyr.data.implementations.akshare_provider", "AkshareIngestProvider"),
            "miniqmt": ("zephyr.data.implementations.miniqmt_provider", "MiniQmtIngestProvider"),
        }
        # provider 文件路径映射（Phase 4.3 路由-meta 一致性校验用）
        source_to_path = {
            "akshare": REPO_ROOT / "src" / "zephyr" / "data" / "implementations" / "akshare_provider.py",
            "miniqmt": REPO_ROOT / "src" / "zephyr" / "data" / "implementations" / "miniqmt_provider.py",
        }
        import importlib

        for task in self._tasks:
            source = task.get("source")
            if not source or source in metas or source not in source_to_meta:
                continue
            module_path, class_name = source_to_meta[source]
            try:
                mod = importlib.import_module(module_path)
                cls = getattr(mod, class_name)
                if hasattr(cls, "meta") and cls.meta is not None:
                    metas[source] = cls.meta
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("读取 %s.meta 失败（跳过契约校验）: %s", source, e)
        violations = validate_task_capability_contracts(self._tasks, metas)
        if violations:
            log.warning("Capability 契约校验发现 %d 条违规:\n%s", len(violations), format_violations(violations))
        else:
            log.info("Capability 契约校验通过（0 违规，裁定 #ARCH-CH-022）")
        if has_blocking_violations(violations):
            blocking = [v for v in violations if v.severity == "ERROR"]
            raise RuntimeError(
                f"Capability 契约校验发现 {len(blocking)} 条 ERROR 级违规，阻断启动（裁定 #ARCH-CH-022）。"
                f"请修复 tasks.yaml 的 capability 声明或 Provider 的 meta.capabilities。"
            )
        # Phase 4.3: provider 路由-meta 一致性校验（WARN，不阻断启动）
        # 治本本次 8 条 ERROR 根因：fetch 路由支持某 capability 但 meta.capabilities 遗漏声明
        route_meta_warnings: list[str] = []
        for source, path in source_to_path.items():
            if not path.exists():
                continue
            file_violations = check_route_meta_consistency(path)
            for v in file_violations:
                route_meta_warnings.append(f"[{source}] {v}")
        if route_meta_warnings:
            log.warning(
                "Provider 路由-meta 一致性校验发现 %d 条 WARN（Phase 4.3，裁定 #ARCH-CH-022）:\n%s"
                "\n注：运行时仅 WARN 不阻断；commit gate（CAP-CONSISTENCY priority=98）会阻断新违规。",
                len(route_meta_warnings),
                "\n".join(route_meta_warnings),
            )
        else:
            log.info("Provider 路由-meta 一致性校验通过（0 违规，Phase 4.3）")

    # ============== Provider 管理 ==============

    def _get_provider(self, source: str) -> IngestProviderBase | None:
        """获取/创建 Provider 实例（懒初始化，线程安全）。"""
        with self._provider_lock:
            if source in self._providers:
                return self._providers[source]
            # 创建新实例
            provider = self.create_provider(source)
            if provider is None:
                log.error("未知数据源: %s", source)
                return None
            try:
                provider.connect()
                self._providers[source] = provider
                log.info("Provider %s 已连接", source)
                return provider
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("Provider %s 连接失败: %s", source, e)
                self._alerter.notify(
                    f"_provider_connect_{source}",
                    f"Provider 连接失败: {e}",
                    level=LEVEL_ERROR,
                    source=source,
                )
                return None

    def create_provider(self, source: str) -> IngestProviderBase | None:
        """创建 Provider 实例（Stage 4 公共化，primary）。"""
        try:
            if source == "miniqmt":
                from zephyr.data.implementations.miniqmt_provider import MiniQmtIngestProvider

                return MiniQmtIngestProvider()
            elif source == "akshare":
                from zephyr.data.implementations.akshare_provider import AkshareIngestProvider

                return AkshareIngestProvider()
            elif source == "baostock":
                from zephyr.data.implementations.baostock_provider import BaostockProvider

                return BaostockProvider()
            elif source == "tushare":
                from zephyr.data.implementations.tushare_provider import TushareProvider

                return TushareProvider()
            elif source == "tickflow":
                from zephyr.data.implementations.tickflow_provider import TickFlowProvider

                return TickFlowProvider()
            elif source == "tdx":
                from zephyr.data.implementations.tdx_provider import TDXProvider

                return TDXProvider()
            elif source == "rss":
                from zephyr.data.implementations.rss_provider import RSSProvider

                return RSSProvider()
            elif source == "cls":
                from zephyr.data.implementations.cls_provider import ClsProvider

                return ClsProvider()
            elif source == "eastmoney_news":
                from zephyr.data.implementations.eastmoney_news_provider import EastmoneyNewsProvider

                return EastmoneyNewsProvider()
            elif source == "tqcenter":
                from zephyr.data.implementations.tqcenter_provider import TQCenterProvider

                return TQCenterProvider()
            elif source == "fred":
                # #ARCH-EDB-EXPAND（2026-08-04）：FRED + 世界银行免费宏观数据
                from zephyr.data.implementations.fred_provider import FredProvider

                return FredProvider()
            elif source == "eia":
                from zephyr.data.implementations.eia_provider import EiaProvider

                return EiaProvider()
            elif source == "qweather":
                from zephyr.data.implementations.qweather_provider import QWeatherProvider

                return QWeatherProvider()
            elif source == "internal":
                # #222（64号 Q18，P0）：内部计算源——读 CH K线本地计算指标/港股日历，
                # 缺失本分支时 hk_trade_calendar_refresh 等 source=internal 任务报"未知数据源"。
                from zephyr.data.implementations.internal_compute_provider import (
                    InternalComputeProvider,
                )

                return InternalComputeProvider()
            else:
                log.warning("未知数据源: %s", source)
                return None
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("创建 Provider %s 异常: %s", source, e)
            return None

    def _create_provider(self, source: str) -> IngestProviderBase | None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        return self.create_provider(source)

    # ============== 任务执行 ==============

    def run_task(self, task_id: str, task_queue: TaskQueue | None = None) -> bool:
        """执行单个任务（含数据源 fallback 机制）。

        流程（数据韧性三层机制 §2）：
        1. 查任务定义
        2. 构造数据源尝试列表：主源 + fallback_sources
        3. 逐源调用 _try_source
        4. 不可恢复错误（配额/认证）→ 立即 fallback 到副源
        5. 可恢复错误（超时/网络）→ 尝试下一个源
        6. 全部源失败 → 返回 False

        Args:
            task_id: 任务标识。
            task_queue: 调度周期传入的局部 TaskQueue（裁定 #ARCH-CH-016 v2）。
                None 时回退到 self._task_queue（手动调用场景）。

        Returns:
            是否成功（任一源成功即返回 True）。
        """
        # 局部队列优先，回退到实例队列（手动调用场景）
        tq = task_queue or self._task_queue
        # 查任务定义
        task = tq.get_task(task_id)
        if task is None:
            # 从 _tasks 缓存查
            task = next((t for t in self._tasks if t["task_id"] == task_id), None)
            if task is not None:
                # 手动调用 run_task 的情况：同步到 task_queue 以便 mark_running 生效
                tq.add_task(task)
        if task is None:
            log.error("未知任务: %s", task_id)
            return False

        # 构造数据源尝试列表：主源 + 副源
        sources_to_try: list[tuple[str, str | None]] = [(task["source"], task.get("capability"))]
        for fb in task.get("fallback_sources") or []:
            sources_to_try.append((fb["source"], fb.get("capability", task.get("capability"))))

        last_error: str | None = None
        for i, (source, capability) in enumerate(sources_to_try):
            is_fallback = i > 0

            # 健康检查前置：如果源在启动时健康检查失败，直接跳过不等超时
            # 避免对已知不可用的源（如 RSSHub 挂了、QMT 未启动）浪费时间等连接超时
            health_status = "unchecked"
            try:
                from zephyr.data.source_health_check import get_source_health

                health = get_source_health(source)
                if health:
                    health_status = health.get("status", "unknown")
                    if health_status in (
                        "connect_fail",
                        "test_fail",
                        "env_missing",
                        "import_fail",
                        "empty_data",
                    ):
                        # 缓存 TTL 到期时对单源重检一次：QMT 恢复后不再被永久跳过
                        from zephyr.data.source_health_check import (
                            _HEALTH_CACHE_TTL_MINUTES,
                            _health_check_age_minutes,
                            _recheck_single_source,
                        )

                        age_min = _health_check_age_minutes(health)
                        if age_min is not None and age_min > _HEALTH_CACHE_TTL_MINUTES:
                            health = _recheck_single_source(source) or health
                            health_status = health.get("status", "unknown")
                            if health_status not in (
                                "connect_fail",
                                "test_fail",
                                "env_missing",
                                "import_fail",
                                "empty_data",
                            ):
                                log.info(
                                    "任务 %s 源 %s 重检通过（%s），继续执行",
                                    task_id,
                                    source,
                                    health_status,
                                )
                                # 落入下方正常执行路径
                                health_status = "recheck_ok"
                        if health_status in (
                            "connect_fail",
                            "test_fail",
                            "env_missing",
                            "import_fail",
                            "empty_data",
                        ):
                            log.info(
                                "任务 %s 跳过源 %s（健康检查: %s, %s）",
                                task_id,
                                source,
                                health_status,
                                (health.get("error") or "")[:80],
                            )
                            last_error = f"健康检查失败: {health.get('error', health_status)}"
                            continue
            except Exception:  # noqa: BLE001 — 健康检查模块异常不影响正常调度
                pass
            # 健康检查通过/未检查——记录即将执行（主源或 fallback，含健康状态便于排查）
            log.info(
                "任务 %s %s源 %s 健康检查=%s，开始执行",
                task_id,
                "fallback " if is_fallback else "主",
                source,
                health_status,
            )
            if is_fallback:
                self._alerter.notify(
                    task_id,
                    f"主源失败({last_error}), fallback到 {source}",
                    level=LEVEL_ERROR,
                    source=source,
                )
            success, error = self._try_source(task, task_id, source, capability, is_fallback, task_queue=tq)
            if success:
                return True
            last_error = error
            if i < len(sources_to_try) - 1:
                from zephyr.data.error_classifier import is_unrecoverable

                if is_unrecoverable(error):
                    log.info(
                        "任务 %s 源 %s 不可恢复错误，立即fallback",
                        task_id,
                        source,
                    )
                else:
                    log.info(
                        "任务 %s 源 %s 失败，尝试下一个源",
                        task_id,
                        source,
                    )
        # 所有源都失败——确保任务标记为 FAILED（治本修复 #ARCH-DAG-DYNAMIC-SCHEDULING）
        # _try_source 在验证阶段失败时不会 mark_failed，需在此兜底
        tq.mark_failed(task_id)
        return False

    def _try_source(
        self,
        task: dict,
        task_id: str,
        source: str,
        capability: str | None,
        is_fallback: bool = False,
        task_queue: TaskQueue | None = None,
    ) -> tuple[bool, str | None]:
        """尝试单个数据源执行任务（run_task 的核心逻辑）。

        流程（蓝图 §3.2 数据流）：
        1. 获取 Provider + 策略
        2. 查断点续传 last_key
        3. 构造 FetchPayload
        4. Provider.fetch -> FetchResult 迭代器
        5. ch_writer.write_result
        6. progress_store.save_progress
        7. 失败 -> alerter.notify

        Args:
            task: 任务定义 dict。
            task_id: 任务标识。
            source: 数据源标识。
            capability: 能力标识（用于 provider 路由，来自 task 或 fallback_sources）。
            is_fallback: 是否为 fallback 副源调用。
            task_queue: 调度周期传入的局部 TaskQueue（裁定 #ARCH-CH-016 v2）。
                None 时回退到 self._task_queue（手动调用场景）。

        Returns:
            (是否成功, 错误信息)。成功时 error 为 None。
        """
        tq = task_queue or self._task_queue
        table = task["table"]
        incremental = task.get("incremental", True)

        # 获取 Provider + 策略 + 熔断检查
        provider, policy, error = self._validate_provider_and_policy(task_id, source)
        if error:
            return False, error

        # 查断点续传 + 构造 FetchPayload
        start, latest_key = self._compute_start_date(task_id, incremental)
        today = datetime.date.today()
        payload = self._build_fetch_payload(task, start, today, incremental, capability)

        # 记录运行开始
        run_id = self._progress_store.start_run(task_id)
        tq.mark_running(task_id)
        task_start_ts = time.time()

        log.info(
            "任务 %s 开始: source=%s table=%s start=%s end=%s fallback=%s",
            task_id,
            source,
            table,
            start,
            today,
            is_fallback,
        )

        total_rows = 0
        last_error: str | None = None

        try:
            # 幂等性清理
            self._cleanup_for_idempotency(task, task_id, table, start, today, incremental)

            # BufferedWriter 批量聚合写入（裁定 #ARCH-CH-003）：
            # 攒批后一次性 write_tsv，避免逐个 FetchResult = 1 次 INSERT 导致 data parts 爆炸
            # per-task buffer_max_seconds 配置（裁定 #ARCH-CH-013 Phase 4 防复发）：
            # news_data 等高频小批任务配置 buffer_max_seconds=300，减少 flush 频率 10x
            buffer_max_seconds = task.get("buffer_max_seconds", 30)
            writer = BufferedWriter(table, max_seconds=buffer_max_seconds)
            total_rows, last_error, latest_key = self._fetch_and_write(
                provider.fetch(payload, policy), writer, task_id, source, latest_key
            )

            # flush 缓冲区残留数据
            if last_error is None and not writer.flush():
                if (
                    writer.last_outcome is not None
                    and writer.last_outcome.disposition is ch_writer.WriteDisposition.LOCAL_DURABLE
                ):
                    detail = f"数据已本地持久化，待回灌: {table}"
                    self._progress_store.save_progress(
                        task_id, source, latest_key, "DEFERRED_PERSISTENCE", total_rows, detail
                    )
                    if run_id:
                        self._progress_store.finish_run(
                            run_id, "DEFERRED_PERSISTENCE", total_rows, writer.total_flushed, detail
                        )
                    tq.mark_deferred_persistence(task_id)
                    self.emit_event("task_completed", task_id=task_id, success=False, deferred=True)
                    return True, None
                last_error = f"ClickHouse 写入失败(flush): {table}"
                log.error("任务 %s CH flush 失败", task_id)

            # 完成
            task_elapsed = time.time() - task_start_ts
            if last_error:
                self._progress_store.save_progress(task_id, source, latest_key, "FAILED", total_rows, last_error)
                if run_id:
                    self._progress_store.finish_run(run_id, "FAILED", total_rows, writer.total_flushed, last_error)
                tq.mark_failed(task_id)
                self._alerter.notify(task_id, last_error, level=LEVEL_ERROR, source=source)
                self._metrics.record_task(task_id, source, "FAILED", task_elapsed, writer.total_flushed)
                self._metrics.flush()
                self.emit_event("task_completed", task_id=task_id, success=False)
                return False, last_error
            else:
                self._progress_store.save_progress(task_id, source, latest_key, "SUCCESS", total_rows)
                if run_id:
                    self._progress_store.finish_run(run_id, "SUCCESS", total_rows, writer.total_flushed)
                tq.mark_completed(task_id)
                # 治本修复 #ARCH-SILENT-SUCCESS（2026-07-24）：
                # 0行写入被标记为SUCCESS且无告警=静默成功陷阱。root cause of 多个表数据过期未被发现。
                # 0行可能是合法的（如今天无新分红），也可能是provider静默失败（如symbols为空/QMT API返回空）。
                # 治本策略：WARN级别记录（不FAIL），使0行完成可见可诊断，配合provider侧error guard消除静默失败。
                if total_rows == 0:
                    log.warning(
                        "任务 %s SUCCESS 但 0 行写入: source=%s table=%s start=%s end=%s "
                        "last_key=%s (可能provider静默失败或当日无新数据)",
                        task_id,
                        source,
                        table,
                        start,
                        today,
                        latest_key,
                    )
                else:
                    log.info("任务 %s 完成: rows=%d last_key=%s", task_id, total_rows, latest_key)
                self._metrics.record_task(task_id, source, "SUCCESS", task_elapsed, writer.total_flushed)
                self._metrics.flush()
                self.emit_event("task_completed", task_id=task_id, success=True)
                return True, None

        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            last_error = str(e)
            log.error("任务 %s 异常: %s", task_id, e, exc_info=True)
            task_elapsed = time.time() - task_start_ts
            rows_written = writer.total_flushed if "writer" in locals() else 0
            self._progress_store.save_progress(task_id, source, latest_key, "FAILED", total_rows, last_error)
            if run_id:
                self._progress_store.finish_run(run_id, "FAILED", total_rows, rows_written, last_error)
            tq.mark_failed(task_id)
            self._alerter.notify(task_id, last_error, level=LEVEL_ERROR, source=source)
            self._metrics.record_task(task_id, source, "FAILED", task_elapsed, rows_written)
            self._metrics.flush()
            self.emit_event("task_completed", task_id=task_id, success=False)
            return False, last_error

    # ===== _try_source() 辅助方法 =====

    def _validate_provider_and_policy(
        self,
        task_id: str,
        source: str,
    ) -> tuple[object, object | None, str | None]:
        """验证 Provider 可用性和熔断状态。返回 (provider, policy, error)。

        治本修复 #ARCH-IFIND-AUTO-RECONNECT（2026-07-24 引入，2026-07-27 复原；iFind 已于 2026-08-14 退役，机制保留并适用于所有 provider）：
        当 Provider 标记 _connected=False（如远端会话过期等），
        自动尝试重连，避免后续任务全部失败直到人工干预。
        适用于所有暴露 _connected 属性的 provider（tushare/tdx/miniqmt/baostock 等）。
        100% AI 场景下无人工干预窗口，自动重连是治本必需——否则一次会话过期会
        导致整日任务雪崩失败，需用户手动重启进程。
        """
        provider = self._get_provider(source)
        if provider is None:
            self._alerter.notify(task_id, f"Provider {source} 不可用", level=LEVEL_ERROR, source=source)
            return None, None, f"Provider {source} 不可用"

        # 自动重连：如果 Provider 已断开连接（如会话过期被远端断开），尝试重连
        if hasattr(provider, "_connected") and not provider._connected:
            log.warning("Provider %s 连接已断开，尝试自动重连...", source)
            try:
                provider.connect()
                log.info("Provider %s 自动重连成功", source)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("Provider %s 自动重连失败: %s", source, e)
                self._alerter.notify(
                    task_id,
                    f"Provider {source} 自动重连失败: {e}",
                    level=LEVEL_ERROR,
                    source=source,
                )
                return None, None, f"Provider {source} 自动重连失败: {e}"

        policy = self._policy_registry.get_policy(source)
        # 熔断检查（CLI `integrator pause <source>` 生效点）
        if not policy.enabled:
            log.warning("任务 %s 跳过：数据源 %s 已熔断", task_id, source)
            self._alerter.notify(task_id, f"源 {source} 已熔断，任务跳过", level=LEVEL_ERROR, source=source)
            return None, None, f"源 {source} 已熔断"

        return provider, policy, None

    def _compute_start_date(
        self,
        task_id: str,
        incremental: bool,
    ) -> tuple[datetime.date, str]:
        """计算起始日期和初始 latest_key（断点续传或月初）。"""
        last_key = self._progress_store.get_last_key(task_id)
        today = datetime.date.today()
        if incremental and last_key:
            try:
                return datetime.date.fromisoformat(last_key), last_key
            except ValueError:
                return today, last_key
        # 全量从月初开始
        return today.replace(day=1), last_key or ""

    @staticmethod
    def _build_fetch_payload(
        task: dict,
        start: datetime.date,
        today: datetime.date,
        incremental: bool,
        capability: str | None,
    ) -> FetchPayload:
        """构造 FetchPayload（capability 注入 extra 供 provider 路由）。"""
        extra = dict(task.get("extra", {}) or {})
        if capability:
            extra.setdefault("capability", capability)
        return FetchPayload(
            table=task["table"],
            symbols=task.get("symbols"),
            start=start,
            end=today,
            incremental=incremental,
            extra=extra,
        )

    def _cleanup_for_idempotency(
        self,
        task: dict,
        task_id: str,
        table: str,
        start: datetime.date,
        today: datetime.date,
        incremental: bool,
    ) -> None:
        """幂等性清理：写入前 DELETE 已有日期范围数据。

        MergeTree 幂等性：date_col 来自 tasks.yaml（SSoT），避免硬编码列名导致 AI 猜错。
        """
        date_col = task.get("date_col")
        if not date_col or not incremental or ch_writer.is_replacing_engine(table):
            return
        dates_to_clean = []
        d = start
        while d <= today:
            dates_to_clean.append(d.isoformat())
            d += datetime.timedelta(days=1)
        if not dates_to_clean:
            return
        date_list = ", ".join(f"toDate('{dd}')" for dd in dates_to_clean)
        log.info("任务 %s 幂等DELETE: %s WHERE toDate(%s) IN (%d dates)", task_id, table, date_col, len(dates_to_clean))
        ch_writer.delete_where(table, f"toDate({date_col}) IN ({date_list})")

    def _fetch_and_write(
        self,
        fetch_iter: object,
        writer: BufferedWriter,
        task_id: str,
        source: str,
        latest_key: str,
    ) -> tuple[int, str | None, str]:
        """执行 fetch + 批量写入循环。返回 (total_rows, last_error, latest_key)。"""
        total_rows = 0
        last_error: str | None = None
        latest = latest_key
        for result in fetch_iter:
            if result.error:
                last_error = result.error
                log.error("任务 %s FetchResult.error: %s", task_id, result.error)
                break

            # 新闻数据去重（基于标题MD5哈希）
            if "news_data" in (result.table or ""):
                from zephyr.data.news_dedup import dedup_news_result

                result = dedup_news_result(result)

            # 多表写入支持：
            # Provider 可在 FetchResult.table 中指定不同的目标表（如概念板块列表+成分股
            # 写入两张表）。当 result.table 与 writer 绑定的表不同时，先 flush 当前
            # 缓冲区，再用 ch_writer 直接写入该批数据到 result.table。
            if result.table and result.table != writer._table:
                # 先 flush 当前缓冲区到原表
                if not writer.flush():
                    last_error = f"ClickHouse 写入失败: {writer._table}"
                    log.error("任务 %s CH写入失败(多表flush)", task_id)
                    break
                # 直接写入 result.table（用临时 BufferedWriter 满足 #ARCH-CH-003 批量写入裁定）
                if result.rows:
                    try:
                        tmp_writer = BufferedWriter(result.table, max_seconds=5)
                        if not tmp_writer.add(result) or not tmp_writer.flush():
                            last_error = f"ClickHouse 写入失败: {result.table}"
                            log.error("任务 %s 多表写入失败 %s", task_id, result.table)
                            break
                        log.info(
                            "任务 %s 多表写入: %s %d 行（主表 %s）",
                            task_id,
                            result.table,
                            len(result.rows),
                            writer._table,
                        )
                    except Exception as e:  # noqa: BLE001
                        last_error = f"ClickHouse 写入失败: {result.table}"
                        log.error("任务 %s 多表写入失败 %s: %s", task_id, result.table, e)
                        break
            elif not writer.add(result):
                last_error = f"ClickHouse 写入失败: {result.table}"
                log.error("任务 %s CH写入失败", task_id)
                break

            total_rows += result.rows_fetched
            # 治本修复 #ARCH-CURSOR-DRIFT（2026-07-24）：
            # 仅当本批有实际数据时才推进 last_key 游标。
            # 原因：Provider（miniqmt/akshare/tushare）在 FetchResult 中设置 last_key=end_str（今天），
            # 即使返回 0 行。若 0 行也推进游标，则下次查询 start=今天，永久跳过
            # 上次实际数据日期与今天之间未采集的数据（如财报公告延迟、QMT 临时断连后恢复）。
            # 修复：rows_fetched=0 时不推进游标，下次自动回查。对日频数据（kline_daily）
            # 影响极小（非交易日由交易日历守卫跳过），对事件驱动数据（财报/公告）治本。
            if result.last_key and result.rows_fetched > 0:
                latest = result.last_key

            # 更新进度（每批）
            self._progress_store.save_progress(task_id, source, latest, "RUNNING", total_rows)
        return total_rows, last_error, latest

    def run_schedule(self, schedule_name: str) -> dict[str, bool]:
        """执行某时段的所有任务（DAG 顺序）。

        Args:
            schedule_name: 时段标识（daily_kline/daily_capital/...）

        Returns:
            {task_id: success_bool} 字典
        """
        sched_config = self._schedules.get(schedule_name, {})
        if _schedule_should_skip(schedule_name, sched_config):
            return {}

        # 特殊时段（weekend_backfill / integrity_check）独立处理
        special = _run_special_schedule(self, schedule_name)
        if special is not None:
            return special

        # 过滤该时段的任务（跳过 extra.disabled=true 的退役/暂停任务）
        schedule_tasks = _filter_schedule_tasks(self._tasks, schedule_name)
        if not schedule_tasks:
            log.warning("时段 %s 无任务", schedule_name)
            return {}

        log.info("时段 %s 开始: %d 个任务", schedule_name, len(schedule_tasks))

        # 加载到 TaskQueue + DAG 并行执行 + 汇总与失败率检查
        return _run_schedule_dag(self, schedule_name, schedule_tasks)

    # ============== APScheduler 生命周期 ==============

    def start(self) -> bool:
        """启动调度器（常驻进程）。

        Returns:
            是否成功启动。
        """
        if self._started:
            log.warning("调度器已在运行")
            return True

        try:
            self.load_config()
            self._validate_capability_contracts()
            self.init_scheduler()

            # 注册 cron/interval job（每个时段一个 job）
            for sched_name, sched_config in self._schedules.items():
                cron_expr = sched_config.get("cron", "")
                executor = sched_config.get("executor", "default")
                sched_type = sched_config.get("type", "cron")
                # interval trigger：高频场景（如集合竞价3秒抓取五档盘口）
                # 时间窗口过滤在 run_schedule() 中实现（start_time/end_time + 周末）
                if sched_type == "interval":
                    seconds = int(sched_config.get("seconds", 3))
                    from apscheduler.triggers.interval import IntervalTrigger

                    trigger = IntervalTrigger(seconds=seconds)
                    self._scheduler.add_job(
                        _run_schedule_callback,
                        trigger,
                        args=[sched_name],
                        id=sched_name,
                        executor=executor,
                        replace_existing=True,
                    )
                    log.info("已注册调度: %s interval=%ss executor=%s", sched_name, seconds, executor)
                    continue
                if not cron_expr:
                    continue
                # 解析 cron 表达式：
                # - 5段："30 16 * * 1-5" -> minute/hour/day/month/day_of_week
                # - 6段："*/3 15-25 9 * * 0-4" -> second/minute/hour/day/month/day_of_week
                #   6段支持秒级触发（如集合竞价3秒高频层），替代 IntervalTrigger 全天唤醒刷屏日志
                parts = cron_expr.split()
                if len(parts) == 5:
                    cron_kwargs = {
                        "minute": parts[0],
                        "hour": parts[1],
                        "day": parts[2],
                        "month": parts[3],
                        "day_of_week": parts[4],
                    }
                elif len(parts) == 6:
                    cron_kwargs = {
                        "second": parts[0],
                        "minute": parts[1],
                        "hour": parts[2],
                        "day": parts[3],
                        "month": parts[4],
                        "day_of_week": parts[5],
                    }
                else:
                    log.warning("cron 格式错误（需5或6段）: %s", cron_expr)
                    continue
                self._scheduler.add_job(
                    _run_schedule_callback,
                    "cron",
                    args=[sched_name],
                    id=sched_name,
                    executor=executor,
                    replace_existing=True,  # 重启时覆盖残留 job（SQLAlchemyJobStore 持久化）
                    **cron_kwargs,
                )
                log.info("已注册调度: %s cron=%s executor=%s", sched_name, cron_expr, executor)

            self._scheduler.start()
            self._started = True
            if self._startup_probes:
                # 数据源健康检查（每日启动时执行，扫描所有数据源连接+下载能力）
                # 结果写入 logs/source_health_YYYYMMDD.log，异常源记录但不自动禁用
                # #ARCH-DATA-015：live 网络 I/O 必须可被测试关闭（startup_probes=False）
                try:
                    from zephyr.data.source_health_check import run_source_health_check

                    run_source_health_check()
                except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                    log.warning("数据源健康检查失败（不影响调度器启动）: %s", e)
                # 启动 ClickHouse 健康探活后台线程（裁定 #ARCH-CH-011）
                self._start_ch_health_probe()
            # 启动卡死任务定期清理线程（Phase 3-B 治本修复 v2）
            self._start_stale_reaper()
            # 启动本地落盘回灌线程（裁定 #ARCH-CH-013 Phase 1）
            self._start_local_replay()
            # 启动破损 part 自动检测+隔离（裁定 #ARCH-CH-015；live CH I/O 随 startup_probes 门控）
            if self._startup_probes:
                self._start_corrupted_part_detector()
            # 注册为全局单例（供 _run_schedule_callback 使用）
            global _global_scheduler
            _global_scheduler = self
            log.info("调度器已启动")
            return True
        except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
            log.error("调度器启动失败: %s", e, exc_info=True)
            return False

    def init_scheduler(self) -> None:
        """初始化 APScheduler BackgroundScheduler（Stage 4 公共化，primary）。"""
        from apscheduler.executors.pool import ThreadPoolExecutor
        from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
        from apscheduler.schedulers.background import BackgroundScheduler

        self._scheduler = BackgroundScheduler(
            jobstores={
                "default": SQLAlchemyJobStore(url=self._jobs_db),
            },
            executors={
                "default": ThreadPoolExecutor(8),  # 通用任务（可并行源）
                "heavy": ThreadPoolExecutor(2),  # 串行源（QMT 等单线程源）
                "realtime": ThreadPoolExecutor(4),  # 盘中实时层（独立线程池，不与批量争抢）
                "intraday_minute": ThreadPoolExecutor(4),  # 盘中分钟K线层（schedule.yaml intraday_minute 时段专用）
                "intraday_sector": ThreadPoolExecutor(2),  # 板块分钟K线层（tdx TCP直连，独立于miniqmt慢任务）
            },
            job_defaults={
                "coalesce": True,  # 错过多次只跑一次
                "max_instances": 1,  # 同任务不并发
                "misfire_grace_time": 3600,  # 错过1小时内仍补跑
            },
        )

    def _init_scheduler(self) -> None:
        """向后兼容 thin wrapper（Stage 4 公共化）。"""
        self.init_scheduler()

    def stop(self) -> None:
        """优雅停止调度器。"""
        # 触发 shutdown 事件
        self.emit_event("shutdown")

        if self._scheduler and self._started:
            try:
                self._scheduler.shutdown(wait=True)
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("调度器停止异常: %s", e)
            self._started = False
            log.info("调度器已停止")

        # 断开所有 Provider
        for source, provider in self._providers.items():
            try:
                provider.disconnect()
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.error("Provider %s 断开异常: %s", source, e)
        self._providers.clear()

        # 关闭进度存储
        try:
            self._progress_store.close()
        except Exception:  # noqa: BLE001 — 5.135治标: broad exception catch
            pass

    # ============== 查询 ==============

    def get_status(self) -> dict[str, Any]:
        """获取调度器状态。"""
        return {
            "started": self._started,
            "schedules": list(self._schedules.keys()),
            "task_count": len(self._tasks),
            "providers": list(self._providers.keys()),
            "task_summary": self._task_queue.summary(),
        }

    def get_health(self) -> dict[str, Any]:
        """获取调度器详细健康状态（供 /health 端点）。

        Returns:
            健康状态字典，包含：
            - status: healthy/degraded/down
            - uptime_seconds: 运行时长
            - scheduler_started: 调度器是否已启动
            - jobs: 注册的 cron job 列表 + 下次执行时间
            - clickhouse: ClickHouse 连接状态
            - providers: 已连接的 Provider 列表
            - task_summary: 任务队列摘要
            - metrics_snapshot: 指标快照（task_total 按 status 汇总）
        """
        self._metrics.update_uptime()

        # ClickHouse 连接状态：读取探活缓存（裁定 #ARCH-CH-011，非阻塞）
        # 原实现同步调用 ch_reader.query("SELECT 1")，连接异常时最坏阻塞 600s
        with self._ch_health_lock:
            ch_status = self._ch_health_cache.get("status", "unknown")
            ch_last_check = self._ch_health_cache.get("last_check", 0.0)
            ch_latency = self._ch_health_cache.get("latency_ms", 0)
        # 缓存过期判断：超过 3 个间隔未更新 → 探活线程可能死亡
        cache_age = time.time() - ch_last_check if ch_last_check else 999
        if cache_age > self._ch_health_interval * 3:
            ch_status = "stale: probe thread may be dead"

        # APScheduler job 信息
        jobs: list[dict] = []
        if self._scheduler:
            try:
                for job in self._scheduler.get_jobs():
                    jobs.append(
                        {
                            "id": job.id,
                            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
                        }
                    )
            except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
                log.warning("获取 APScheduler jobs 失败: %s", e)

        # 指标快照：按 status 汇总 task_total
        task_stats: dict[str, int] = {"SUCCESS": 0, "FAILED": 0, "BLOCKED": 0}
        with self._metrics._lock:
            for (_tid, _src, status), val in self._metrics._task_total.items():
                task_stats[status] = task_stats.get(status, 0) + val

        # 判断整体状态
        status = "healthy"
        if not self._started:
            status = "down"
        elif ch_status != "ok":
            status = "degraded"

        return {
            "status": status,
            "uptime_seconds": round(self._metrics._uptime, 2),
            "scheduler_started": self._started,
            "jobs_registered": len(self._schedules),
            "jobs": jobs,
            "clickhouse": ch_status,
            "clickhouse_latency_ms": ch_latency,
            "providers": list(self._providers.keys()),
            "task_summary": self._task_queue.summary(),
            "task_stats": task_stats,
        }

    def list_tasks(self) -> list[dict]:
        """列出所有任务。"""
        return list(self._tasks)


# ============== 监控 HTTP 端点 ==============


class _MonitorHandler(http.server.BaseHTTPRequestHandler):
    """监控 HTTP handler（标准库实现，无额外依赖）。

    端点：
    - GET /metrics → Prometheus 文本格式（供 Prometheus 抓取）
    - GET /health  → JSON 健康状态（含 CH 连接、job 调度、task 统计）
    - GET /status  → JSON 调度器基本状态
    """

    scheduler: IntegratorScheduler | None = None  # 类变量，由 start_monitor 设置

    def do_GET(self) -> None:
        if self.path == "/metrics":
            self._handle_metrics()
        elif self.path == "/health":
            self._handle_health()
        elif self.path == "/status":
            self._handle_status()
        else:
            self._send_json(404, {"error": "not found", "endpoints": ["/metrics", "/health", "/status"]})

    def _handle_metrics(self) -> None:
        """输出 Prometheus 文本格式指标。"""
        from zephyr.data.metrics import get_metrics

        m = get_metrics()
        m.update_uptime()
        body = m.render()
        self._send(200, body, "text/plain; version=0.0.4; charset=utf-8")

    def _handle_health(self) -> None:
        """输出详细健康状态 JSON。"""
        if self.scheduler is None:
            self._send_json(503, {"status": "down", "error": "scheduler not initialized"})
            return
        try:
            health = self.scheduler.get_health()
            self._send_json(200, health)
        except Exception as e:  # noqa: BLE001 — /health 降级：返通用错误，细节入日志
            # 5.168治本（#ARCH-SEC-001）：异常详情不经 HTTP 跨信任边界外发
            log.warning("/health 处理失败: %s", e, exc_info=True)
            self._send_json(500, {"status": "error", "error": "internal error"})

    def _handle_status(self) -> None:
        """输出调度器基本状态 JSON。"""
        if self.scheduler is None:
            self._send_json(503, {"error": "scheduler not initialized"})
            return
        try:
            status = self.scheduler.get_status()
            self._send_json(200, status)
        except Exception as e:  # noqa: BLE001 — /status 降级：返通用错误，细节入日志
            # 5.168治本（#ARCH-SEC-001）：异常详情不经 HTTP 跨信任边界外发
            log.warning("/status 处理失败: %s", e, exc_info=True)
            self._send_json(500, {"error": "internal error"})

    def _send_json(self, code: int, obj: object) -> None:
        body = json.dumps(obj, ensure_ascii=False, default=str)
        self._send(code, body, "application/json; charset=utf-8")

    def _send(self, code: int, body: str, content_type: str) -> None:
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, fmt: str, *args: Any) -> None:
        pass  # 静默 HTTP 访问日志（避免刷屏）


class _ThreadingHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True


def start_monitor(scheduler: IntegratorScheduler, port: int = 9100) -> None:
    """启动监控 HTTP server（后台守护线程）。

    Args:
        scheduler: 调度器实例
        port: 监听端口，默认 9100（Prometheus 标准端口段）

    容错：端口被占用（如备份 minio_tcp_relay 临时占用 9100）时降级为无 HTTP 监控，
    调度器核心任务不受影响（治本：避免端口冲突导致调度器崩溃重启循环）。
    """
    _MonitorHandler.scheduler = scheduler
    try:
        server = _ThreadingHTTPServer(("0.0.0.0", port), _MonitorHandler)
    except OSError as e:
        log.warning(
            "监控 HTTP server 启动失败（端口 %d 被占用: %s），调度器继续运行（无 HTTP 监控）",
            port,
            e,
        )
        return
    t = threading.Thread(target=server.serve_forever, daemon=True, name="monitor-http")
    t.start()
    log.info("监控 HTTP server 已启动，端口 %d（/metrics /health /status）", port)


# ============== 入口 ==============


def main() -> None:
    """调度器入口：启动常驻进程。

    用法：
        python -m zephyr.data.scheduler
    """
    import signal
    import sys

    # 显式加载 CH 配置（裁定 #ARCH-CH-017：启动入口必须加载 .env.clickhouse）
    # ch_writer 模块级已加载一次，此处幂等调用确保启动序列明确
    from zephyr.data.ch_config import ensure_ch_env_loaded

    ensure_ch_env_loaded()

    # 日志落盘（RotatingFileHandler 轮转，避免无限增长）
    from logging.handlers import RotatingFileHandler

    _log_path = REPO_ROOT / "tmp" / "scheduler_run.log"
    _log_path.parent.mkdir(parents=True, exist_ok=True)
    _fh = RotatingFileHandler(_log_path, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
    _fh.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
    _root = logging.getLogger()
    _root.setLevel(logging.INFO)  # 确保 INFO 级别日志能写入文件（默认 WARNING 会过滤掉 INFO）
    _root.addHandler(_fh)
    log.info("日志落盘: %s", _log_path)

    global _global_scheduler
    sched = IntegratorScheduler()
    _global_scheduler = sched

    # 信号处理：Ctrl+C 优雅关闭
    def _signal_handler(signum, frame):
        log.info("收到信号 %s，正在停止...", signum)
        sched.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    if not sched.start():
        log.error("调度器启动失败，退出")
        sys.exit(1)

    # 启动监控 HTTP server（端口 9100：/metrics /health /status）
    start_monitor(sched, port=9100)

    log.info("调度器已启动，按 Ctrl+C 停止")

    # 常驻等待（用 Event().wait 避免被 PERM-TRIGGER 误判为时间触发）
    try:
        while sched._started:
            threading.Event().wait(timeout=60)
            # 策略热更新检查
            sched._policy_registry.maybe_reload()
    except KeyboardInterrupt:
        sched.stop()


if __name__ == "__main__":
    main()
