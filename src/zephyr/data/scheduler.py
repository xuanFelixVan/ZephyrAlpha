# [BLUEPRINT] MOD-L00-004 | docs/03_modules/_domain_data/data_source_integrator_blueprint.md
# [MODULE] zephyr.data.scheduler
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.data.provider_base; zephyr.data.policy_registry; zephyr.data.progress_store; zephyr.data.ch_writer; zephyr.data.task_queue; zephyr.data.alerter; zephyr.data.implementations.{ifind,miniqmt,akshare}_provider; apscheduler(pip)
# [CONSUMERS] CLI(zephyr.data.cli 阶段3+); main()入口
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] APScheduler BackgroundScheduler常驻进程; 5档cron时段; DAG依赖(task_queue); per-source串行+跨源并行; 断点续传(progress_store); 失败告警(alerter); subscribe()事件订阅支持热更新
# [MODIFY-GUARD] none
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] run_task失败->返回False+alerter.notify; start/stop异常->log+不抛; 所有方法返回dict/bool不抛异常
# [TESTS] tests/zephyr/data/test_scheduler.py
# [A_module] module_id=MOD-L00-004-scheduler | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
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
import logging
import threading
import time
from pathlib import Path
from typing import Callable, Any

from zephyr.data.provider_base import DataSourceBase, FetchPayload, FetchResult
from zephyr.data.policy_registry import PolicyRegistry, get_registry
from zephyr.data.progress_store import ProgressStore, get_store
from zephyr.data.task_queue import TaskQueue, SUCCESS, FAILED, PENDING, RUNNING
from zephyr.data.alerter import Alerter, LEVEL_ERROR, LEVEL_CRITICAL
from zephyr.data import ch_writer
from zephyr.data.buffered_writer import BufferedWriter
from zephyr.data.metrics import IntegratorMetrics, get_metrics
from zephyr.shared.io.paths import REPO_ROOT

log = logging.getLogger(__name__)

_DEFAULT_CONFIG_DIR = Path(__file__).parent / "config"
_DEFAULT_JOBS_DB = "sqlite:///" + str(REPO_ROOT / "data" / "integrator_jobs.db")

# 模块级调度器单例（供 APScheduler job 回调使用，避免 pickle 绑定方法+Lock 对象）
_global_scheduler: "IntegratorScheduler | None" = None


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
    ):
        """初始化调度器。

        Args:
            config_dir: 配置目录（含 schedule.yaml/tasks.yaml/policies.yaml）
            progress_db: SQLite 进度库路径
            jobs_db: APScheduler jobstore URL
        """
        self._config_dir = Path(config_dir) if config_dir else _DEFAULT_CONFIG_DIR
        self._jobs_db = jobs_db or _DEFAULT_JOBS_DB
        # 组件
        self._policy_registry: PolicyRegistry = get_registry()
        self._progress_store: ProgressStore = get_store(progress_db)
        self._alerter = Alerter()
        self._task_queue = TaskQueue()
        self._metrics: IntegratorMetrics = get_metrics()
        self._providers: dict[str, DataSourceBase] = {}
        self._provider_lock = threading.Lock()
        # APScheduler 实例（懒初始化）
        self._scheduler = None
        self._started = False
        # 配置缓存
        self._schedules: dict[str, dict] = {}
        self._tasks: list[dict] = []
        # 事件订阅（永久系统须有事件订阅）
        self._event_handlers: dict[str, list[Callable]] = {
            "config_changed": [],
            "shutdown": [],
            "task_completed": [],
        }
        # 注册内部默认事件处理器（config_changed -> 策略热更新）
        self.subscribe("config_changed", self._on_config_changed)

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

    def _emit_event(self, event: str, *args, **kwargs) -> None:
        """触发事件（调用所有订阅者）。异常不抛出。"""
        for handler in self._event_handlers.get(event, []):
            try:
                handler(*args, **kwargs)
            except Exception as e:
                log.error("事件 %s handler 异常: %s", event, e)

    def _on_config_changed(self, **kwargs) -> None:
        """config_changed 事件默认处理器：策略热更新。"""
        try:
            self._policy_registry.maybe_reload(force=True)
            log.info("config_changed 事件触发策略热更新")
        except Exception as e:
            log.error("config_changed 事件处理异常: %s", e)

    # ============== 配置加载 ==============

    def _load_config(self) -> None:
        """加载 schedule.yaml + tasks.yaml。"""
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

    def reload_policies(self) -> bool:
        """热更新策略（手动调用或 config_changed 事件触发）。"""
        return self._policy_registry.maybe_reload(force=True)

    # ============== Provider 管理 ==============

    def _get_provider(self, source: str) -> DataSourceBase | None:
        """获取/创建 Provider 实例（懒初始化，线程安全）。"""
        with self._provider_lock:
            if source in self._providers:
                return self._providers[source]
            # 创建新实例
            provider = self._create_provider(source)
            if provider is None:
                log.error("未知数据源: %s", source)
                return None
            try:
                provider.connect()
                self._providers[source] = provider
                log.info("Provider %s 已连接", source)
                return provider
            except Exception as e:
                log.error("Provider %s 连接失败: %s", source, e)
                self._alerter.notify(
                    f"_provider_connect_{source}",
                    f"Provider 连接失败: {e}",
                    level=LEVEL_ERROR,
                    source=source,
                )
                return None

    def _create_provider(self, source: str) -> DataSourceBase | None:
        """创建 Provider 实例。"""
        try:
            if source == "ifind":
                from zephyr.data.implementations.ifind_provider import IFindProvider
                return IFindProvider()
            elif source == "miniqmt":
                from zephyr.data.implementations.miniqmt_provider import MiniQMTProvider
                return MiniQMTProvider()
            elif source == "akshare":
                from zephyr.data.implementations.akshare_provider import AKShareProvider
                return AKShareProvider()
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
            else:
                log.warning("未知数据源: %s", source)
                return None
        except Exception as e:
            log.error("创建 Provider %s 异常: %s", source, e)
            return None

    # ============== 任务执行 ==============

    def run_task(self, task_id: str) -> bool:
        """执行单个任务。

        流程（蓝图 §3.2 数据流）：
        1. 查任务定义
        2. 获取 Provider + 策略
        3. 查断点续传 last_key
        4. 构造 FetchPayload
        5. Provider.fetch -> FetchResult 迭代器
        6. ch_writer.write_result
        7. progress_store.save_progress
        8. 失败 -> alerter.notify

        Returns:
            是否成功。
        """
        # 查任务定义
        task = self._task_queue.get_task(task_id)
        if task is None:
            # 从 _tasks 缓存查
            task = next((t for t in self._tasks if t["task_id"] == task_id), None)
            if task is not None:
                # 手动调用 run_task 的情况：同步到 task_queue 以便 mark_running 生效
                self._task_queue.add_task(task)
        if task is None:
            log.error("未知任务: %s", task_id)
            return False

        source = task["source"]
        table = task["table"]
        incremental = task.get("incremental", True)

        # 获取 Provider
        provider = self._get_provider(source)
        if provider is None:
            self._alerter.notify(task_id, f"Provider {source} 不可用", level=LEVEL_ERROR, source=source)
            return False

        # 获取策略
        policy = self._policy_registry.get_policy(source)

        # 熔断检查（CLI `integrator pause <source>` 生效点）
        if not policy.enabled:
            log.warning("任务 %s 跳过：数据源 %s 已熔断", task_id, source)
            self._alerter.notify(
                task_id, f"源 {source} 已熔断，任务跳过", level=LEVEL_ERROR, source=source
            )
            self._task_queue.mark_failed(task_id)
            return False

        # 查断点续传
        last_key = self._progress_store.get_last_key(task_id)
        today = datetime.date.today()
        if incremental and last_key:
            try:
                start = datetime.date.fromisoformat(last_key)
            except ValueError:
                start = today
        else:
            start = today.replace(day=1)  # 全量从月初开始

        # 构造 FetchPayload
        payload = FetchPayload(
            table=table,
            symbols=task.get("symbols"),
            start=start,
            end=today,
            incremental=incremental,
            extra=task.get("extra", {}),
        )

        # 记录运行开始
        run_id = self._progress_store.start_run(task_id)
        self._task_queue.mark_running(task_id)
        task_start_ts = time.time()

        log.info("任务 %s 开始: source=%s table=%s start=%s end=%s",
                 task_id, source, table, start, today)

        total_rows = 0
        last_error: str | None = None
        latest_key = last_key or ""

        try:
            # BufferedWriter 批量聚合写入（裁定 #ARCH-CH-003）：
            # 攒批后一次性 write_tsv，避免逐个 FetchResult = 1 次 INSERT 导致 data parts 爆炸
            writer = BufferedWriter(table)
            for result in provider.fetch(payload, policy):
                if result.error:
                    last_error = result.error
                    log.error("任务 %s FetchResult.error: %s", task_id, result.error)
                    break

                # 攒批写入 ClickHouse（达 50000 行或 30 秒自动 flush）
                if not writer.add(result):
                    last_error = f"ClickHouse 写入失败: {result.table}"
                    log.error("任务 %s CH写入失败", task_id)
                    break

                total_rows += result.rows_fetched
                if result.last_key:
                    latest_key = result.last_key

                # 更新进度（每批）
                self._progress_store.save_progress(
                    task_id, source, latest_key, "RUNNING", total_rows
                )

            # flush 缓冲区残留数据
            if last_error is None and not writer.flush():
                last_error = f"ClickHouse 写入失败(flush): {table}"
                log.error("任务 %s CH flush 失败", task_id)

            # 完成
            task_elapsed = time.time() - task_start_ts
            if last_error:
                self._progress_store.save_progress(
                    task_id, source, latest_key, "FAILED", total_rows, last_error
                )
                if run_id:
                    self._progress_store.finish_run(run_id, "FAILED", total_rows, total_rows, last_error)
                self._task_queue.mark_failed(task_id)
                self._alerter.notify(task_id, last_error, level=LEVEL_ERROR, source=source)
                self._metrics.record_task(task_id, source, "FAILED", task_elapsed, total_rows)
                self._metrics.flush()
                self._emit_event("task_completed", task_id=task_id, success=False)
                return False
            else:
                self._progress_store.save_progress(
                    task_id, source, latest_key, "SUCCESS", total_rows
                )
                if run_id:
                    self._progress_store.finish_run(run_id, "SUCCESS", total_rows, total_rows)
                self._task_queue.mark_completed(task_id)
                log.info("任务 %s 完成: rows=%d last_key=%s", task_id, total_rows, latest_key)
                self._metrics.record_task(task_id, source, "SUCCESS", task_elapsed, total_rows)
                self._metrics.flush()
                self._emit_event("task_completed", task_id=task_id, success=True)
                return True

        except Exception as e:
            last_error = str(e)
            log.error("任务 %s 异常: %s", task_id, e, exc_info=True)
            task_elapsed = time.time() - task_start_ts
            self._progress_store.save_progress(
                task_id, source, latest_key, "FAILED", total_rows, last_error
            )
            if run_id:
                self._progress_store.finish_run(run_id, "FAILED", total_rows, total_rows, last_error)
            self._task_queue.mark_failed(task_id)
            self._alerter.notify(task_id, last_error, level=LEVEL_ERROR, source=source)
            self._metrics.record_task(task_id, source, "FAILED", task_elapsed, total_rows)
            self._metrics.flush()
            self._emit_event("task_completed", task_id=task_id, success=False)
            return False

    def run_schedule(self, schedule_name: str) -> dict[str, bool]:
        """执行某时段的所有任务（DAG 顺序）。

        Args:
            schedule_name: 时段标识（daily_kline/daily_capital/...）

        Returns:
            {task_id: success_bool} 字典
        """
        # 过滤该时段的任务
        schedule_tasks = [t for t in self._tasks if t.get("schedule") == schedule_name]
        if not schedule_tasks:
            log.warning("时段 %s 无任务", schedule_name)
            return {}

        log.info("时段 %s 开始: %d 个任务", schedule_name, len(schedule_tasks))

        # 加载到 TaskQueue
        self._task_queue = TaskQueue()
        for t in schedule_tasks:
            self._task_queue.add_task(t)

        # DAG 顺序执行
        results: dict[str, bool] = {}
        while not self._task_queue.is_done():
            ready = self._task_queue.get_ready_tasks()
            if not ready:
                # 无就绪任务但未完成 -> 可能有 BLOCKED 任务
                blocked = self._task_queue.list_by_status("BLOCKED")
                if blocked:
                    log.warning("时段 %s 有 %d 个 BLOCKED 任务", schedule_name, len(blocked))
                break
            for task_id in ready:
                success = self.run_task(task_id)
                results[task_id] = success

        # 汇总
        success_count = sum(1 for v in results.values() if v)
        failed_count = len(results) - success_count
        log.info("时段 %s 完成: %d 成功, %d 失败", schedule_name, success_count, failed_count)

        # 检查失败率
        if results:
            self._alerter.check_daily_failure_rate(len(results), failed_count)

        return results

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
            self._load_config()
            self._init_scheduler()

            # 注册 cron job（每个时段一个 job）
            for sched_name, sched_config in self._schedules.items():
                cron_expr = sched_config.get("cron", "")
                executor = sched_config.get("executor", "default")
                if not cron_expr:
                    continue
                # 解析 cron 表达式 "30 16 * * 1-5" -> minute/hour/day/month/day_of_week
                parts = cron_expr.split()
                if len(parts) != 5:
                    log.warning("cron 格式错误: %s", cron_expr)
                    continue
                cron_kwargs = {
                    "minute": parts[0],
                    "hour": parts[1],
                    "day": parts[2],
                    "month": parts[3],
                    "day_of_week": parts[4],
                }
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
            # 注册为全局单例（供 _run_schedule_callback 使用）
            global _global_scheduler
            _global_scheduler = self
            log.info("调度器已启动")
            return True
        except Exception as e:
            log.error("调度器启动失败: %s", e, exc_info=True)
            return False

    def _init_scheduler(self) -> None:
        """初始化 APScheduler BackgroundScheduler。"""
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
        from apscheduler.executors.pool import ThreadPoolExecutor

        self._scheduler = BackgroundScheduler(
            jobstores={
                "default": SQLAlchemyJobStore(url=self._jobs_db),
            },
            executors={
                "default": ThreadPoolExecutor(8),  # 通用任务（可并行源）
                "heavy": ThreadPoolExecutor(2),    # 串行源（iFind/QMT）
            },
            job_defaults={
                "coalesce": True,                  # 错过多次只跑一次
                "max_instances": 1,                # 同任务不并发
                "misfire_grace_time": 3600,        # 错过1小时内仍补跑
            },
        )

    def stop(self) -> None:
        """优雅停止调度器。"""
        # 触发 shutdown 事件
        self._emit_event("shutdown")

        if self._scheduler and self._started:
            try:
                self._scheduler.shutdown(wait=True)
            except Exception as e:
                log.error("调度器停止异常: %s", e)
            self._started = False
            log.info("调度器已停止")

        # 断开所有 Provider
        for source, provider in self._providers.items():
            try:
                provider.disconnect()
            except Exception as e:
                log.error("Provider %s 断开异常: %s", source, e)
        self._providers.clear()

        # 关闭进度存储
        try:
            self._progress_store.close()
        except Exception:
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

    def list_tasks(self) -> list[dict]:
        """列出所有任务。"""
        return list(self._tasks)


# ============== 入口 ==============

def main() -> None:
    """调度器入口：启动常驻进程。

    用法：
        python -m zephyr.data.scheduler
    """
    import signal
    import sys

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
