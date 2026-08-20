# [BLUEPRINT] MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR | docs/03_modules/_domain_governance/blueprint.md | §ARCH-TOOL-HEALTH-V1 Phase 5b
# [MODULE] zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.reconciliation_registry (ReconcileResult, ReconcilerSpec, _write_reconcile_report); zephyr.gov_enforcement.rule_enforcement.adaptive_threshold (AdaptiveThreshold, ThresholdMode — P3-1 接入); zephyr.governance.audit.health_score_calculator (calculate_health_score — P3-3 接入); stdlib (json, logging, subprocess, time, pathlib)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] post-commit 事件触发（任何 commit 都触发，滥用监控是全局关注）；reconciler 永不抛异常（异常降级为 warn）；只读 post_commit_guard/commit_gateway_audit 报告，不修改它们；P3-1 有效阈值 = max(adaptive, static)，防止自适应阈值低于静态下限掩盖真实恶化；P3-6 baseline 持久化失败不阻断 reconciler（fail-open）；P3-3 综合评分 >0.7 critical_warn / >0.9 block_next（post-commit 无法 block，降级为 critical_warn + 横幅，提示 PAUSE subsequent commits）；P3-3 评分失败降级 health_score=0.0（fail-open，不阻断 reconciler）
# [MODIFY-GUARD] GATE_ID / PRIORITY / 阈值常量 / ADAPTIVE_FACTOR / BASELINE_WINDOW_DAYS / BLOCK_NEXT_SCORE / CRITICAL_WARN_SCORE
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] reconcile 永不抛异常——读取/解析失败降级为 ReconcileResult(action="warn")
# [TESTS] tests/governance/audit/test_commit_gateway_abuse_monitor_reconciler.py
# [A_module] module_id=MOD-GOV_COMMIT_GATEWAY_ABUSE_MONITOR | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: reconciler 是 commit 事件触发(非 cron/manual)
"""

commit_gateway_abuse_monitor_reconciler.py — commit gateway 持续滥用监控（ARCH-TOOL-HEALTH-V1 Phase 5b，2026-07-19）。

post-commit 事件触发，扫描 ``.runtime/reconcile_reports/`` 下 ``post_commit_guard_*``
与 ``commit_gateway_audit_*`` 报告 + ``git log`` 中 emergency 标记，检测 **持续滥用模式**
（24h/7d 长窗口），补强 POST-COMMIT-GUARD 的 1h 短窗口盲区。

P3-6 + P3-1 扩展（#ARCH-PREVENTABILITY-LAYER-001 Phase 3，2026-07-20）
-------------------------------------------------------------------
- **P3-6**: 7d baseline 持久化到 ``.runtime/abuse_monitor/abuse_baseline.json``。
  每次 reconcile 后将今日 6 维 metrics 追加到 baseline（同日覆盖，7d 滚动窗口裁剪）。
  系统层状态（类似 session_registry.json），由 reconciler 维护。
- **P3-1**: 接入 ``AdaptiveThreshold``（P3-0 双模式扩展），从历史 7d baseline 计算
  EWMA 自适应阈值。最终有效阈值 = max(adaptive, static)，防止自适应阈值低于静态
  下限掩盖真实恶化（ruling §5.3 风险治本）。自适应阈值基于历史 baseline（不含今日），
  避免当日计数自我影响阈值。

治本动机（第一性原理）
--------------------
POST-COMMIT-GUARD（Phase 5a，裁定 B）在 per-commit 层做 per-hour aggregate 阈值阻断
（默认 10/h）——能捕获**短时高频**滥用。但有 3 类**持续低频**滥用 per-hour 阈值永远抓不到：

1. **持续 warn-only 低频**：5/h × 24h = 120 次 warn-only，但每小时都 <10 不触发 block
2. **emergency_commit 持续滥用**：[GW:*:emergency] 是合法逃生通道，但 5/天 × 7天 = 35 次
   = 系统性问题（应为罕见逃生，非日常工具）
3. **forged_gw_marker 持续低频**：3/天 × 7天 = 21 次伪造 = 严重治理失效（任何伪造都是
   intentional，不应有"低频容忍"）

reconciler 是 post-commit（commit 已入历史不可逆），故只能 warn / critical_warn，
不能 block。但 critical_warn 会打印横幅强制 AI 看到，确保失败不被忽视。

六维滥用检测（warn-only，阈值见下方常量）
-----------------------------------------
1. **warn_only sustained (24h)**: >50 warn_only 事件/24h = 持续低频逃生通道滥用
2. **emergency_commit abuse (24h)**: >5 [GW:*:emergency] commits/24h = 逃生通道日常化
3. **allow_overlap abuse (7d)**: >30 次真实 allow_overlap=True 提交/7d（gate 层审计
   ``.runtime/gate_audit/allow_overlap_usage.jsonl`` 计数）= 逃生通道日常化
4. **forged_gw_marker rate (24h)**: >3 forged_gw_marker/24h = 严重伪造（任何伪造都 serious）
5. **non-GW commit sustained (24h)**: >10 non-GW commits/24h（commit_gw_audit violations
   sum）= 持续绕过 GitCommitGateway
6. **force_merge abuse (7d)**: >5 次真实 force=True session_worktree_merge/7d（gate 层审计
   ``.runtime/gate_audit/force_merge_usage.jsonl`` 计数）= pre-merge gate sys.path 问题
   或 worktree 基础设施故障（#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 v1.3.0 扩展，2026-07-21）

判定
----
- 0 个维度触发 → clean
- 1-2 个维度触发 → warn
- 3+ 个维度触发 OR forged_gw_marker 维度触发 → critical_warn（横幅强制 AI 看到）

priority=875（晚于 git_performance_monitor(870)，早于 remediation_progress(900)）

Usage
-----
::

    from zephyr.governance.audit.commit_gateway_abuse_monitor_reconciler import (
        make_commit_gateway_abuse_monitor_reconciler,
    )

    registry.register(make_commit_gateway_abuse_monitor_reconciler(gateway))

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 网关对账报告 JSON
#   fields: post_commit_guard_*（7d）+ commit_gateway_audit_*（24h）报告
#   code: read_json_reports L391（.runtime/reconcile_reports/）
# - id: I2
#   name: git log 提交信息
#   fields: [GW:*:emergency] 标记 + [SCENARIO:] 场景标记（24h）
#   code: count_emergency_commits L426
# - id: I3
#   name: gate 层逃生通道审计 JSONL
#   fields: allow_overlap_usage.jsonl + force_merge_usage.jsonl（7d 时间戳计数）
#   code: count_allow_overlap_usage L472 / count_force_merge_usage L505
# - id: I4
#   name: 滥用阈值真源 YAML
#   fields: 6 维阈值（warn_only/emergency/allow_overlap/forged/non_gw/force_merge）
#   code: load_thresholds_from_yaml L134（trae_069_commit_gateway_abuse_thresholds.yaml）
# - id: I5
#   name: 7d 滥用基线
#   fields: 每日 6 维计数历史 daily_records
#   code: load_baseline L242（.runtime/abuse_monitor/abuse_baseline.json）
# 层: 算法
# - id: A1
#   name_zh: ① 阈值加载 fail-open
#   name_en: load_thresholds_from_yaml
#   intro: 从 YAML 读 6 维阈值，缺失或非法值回退代码内默认值
#   desc: SSoT 铁律：阈值真源是 YAML；逐维校验 int>=0，异常整体回退 DEFAULT_THRESHOLDS
#   inputs: I4
#   outputs: 6 维静态阈值 dict
# - id: A2
#   name_zh: ② 六维滥用计数采集
#   name_en: read_json_reports + count_emergency_commits + count_allow_overlap_usage + count_force_merge_usage
#   intro: 从报告/git log/审计 JSONL 三处采集 24h 与 7d 窗口的真实滥用计数
#   desc: 报告按 timestamp 过滤；emergency 按 scenario!=production 豁免；审计 JSONL 逐行计时间窗内记录；全部 fail-open 归 0
#   inputs: I1 I2 I3
#   outputs: 6 维原始计数
# - id: A3
#   name_zh: ③ EWMA 自适应阈值计算
#   name_en: compute_adaptive_thresholds
#   intro: 用 7d 历史基线算自适应阈值，防止静态阈值掩盖渐进恶化
#   desc: AdaptiveThreshold COUNT 模式 observe_count 逐日观测，阈值=EWMA×1.5；有效阈值=max(adaptive, static)
#   inputs: I5 A1
#   outputs: 6 维自适应阈值 dict
# - id: A4
#   name_zh: ④ 六维滥用分类判定
#   name_en: classify_abuse
#   intro: 逐维比对计数与有效阈值，超阈即记入触发维度
#   desc: 有效阈值=max(adaptive,static)；non_gw 按 commit hash 去重计数；纯函数无副作用
#   inputs: A2 A3 A1
#   outputs: dimensions_triggered + details + metrics
# - id: A5
#   name_zh: ⑤ 基线滚动持久化
#   name_en: record_daily_metrics
#   intro: 把今日 6 维计数写回 baseline，同日覆盖并裁剪 7d 外旧记录
#   desc: date 去重保留最新；timestamp>=now-7d 裁剪；写失败仅 warning 不阻断
#   inputs: A4
#   outputs: 更新后 daily_records（写回 abuse_baseline.json）
# - id: A6
#   name_zh: ⑥ 综合评分分级判定
#   name_en: _reconcile
#   intro: 健康度评分优先分级，post-commit 无法 block 一律降级为告警
#   desc: health_score>0.9 → critical_warn（提示 PAUSE）；>0.7 → critical_warn；否则 forged 触发或 3+ 维 → critical_warn，1-2 维 → warn，0 维 → clean
#   inputs: A4 A5
#   outputs: ReconcileResult(clean/warn/critical_warn)
#   invariant: reconciler 永不抛异常；post-commit 不能 block
# 层: 输出
# - id: O1
#   name_zh: 对账结果 ReconcileResult
#   name_en: ReconcileResult
#   intro: clean/warn/critical_warn 三档结果（gate_id=GATE-COMMIT-GW-ABUSE-MONITOR）
#   downstream: GitCommitGateway MOD-INF-035
# - id: O2
#   name_zh: 滥用监控报告与基线落盘
#   name_en: commit_gateway_abuse_monitor 报告 + abuse_baseline.json
#   intro: 每次 reconcile 落盘审计报告供趋势追踪，baseline 供次日自适应阈值自消费
#   downstream: .runtime/reconcile_reports/（趋势追踪）+ 本模块 A3 自消费
# [/ALGO_FLOW]
#
# 边:
# I4 --> A1
# I1 --> A2
# I2 --> A2
# I3 --> A2
# I5 --> A3
# A1 --> A3
# A1 --> A4
# A2 --> A4
# A3 --> A4
# A4 --> A5
# A4 --> A6
# A5 --> O2
# A6 --> O1
# A6 --> O2
"""

from __future__ import annotations

import json
import logging
import subprocess
import time
from pathlib import Path

from zephyr.gov_enforcement.rule_enforcement.adaptive_threshold import (
    AdaptiveThreshold,
    ThresholdMode,
)
from zephyr.governance.audit.health_score_calculator import calculate_health_score
from zephyr.governance.audit.reconciliation_registry import (
    ReconcileResult,
    ReconcilerSpec,
    _write_reconcile_report,
)
from zephyr.shared.infra.process_pool import run_subprocess_hidden

logger = logging.getLogger(__name__)

GATE_ID = "GATE-COMMIT-GW-ABUSE-MONITOR"
# priority=875: 晚于 git_performance_monitor(870)，早于 remediation_progress(900)
PRIORITY = 875

# === 六维滥用阈值（warn-only，reconciler 不能 block post-commit）===
# P3-1 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
# 阈值真源已提取到 trae_069_commit_gateway_abuse_thresholds.yaml（SSoT 铁律：
# 规则数据真源是 YAML 文件）。代码常量改为从此文件加载（fail-open：
# YAML 缺失/解析失败时使用代码内默认值，不阻断 reconciler）。
#
# 历史（裁定 R3/R5/R6 + P1 治本链）：
#   2026-07-19: 原阈值散落在代码常量（WARN_ONLY_24H_THRESHOLD = 50 等）
#   2026-07-20 P1-4: emergency 10→5 回滚（heartbeat 已落地 + scenario 过滤已引入）
#   2026-07-20 P3-1: 提取到 YAML，代码常量改为 load_thresholds_from_yaml() 返回值
THRESHOLDS_YAML_PATH = (
    Path(__file__).resolve().parents[4]  # src/zephyr/governance/audit → repo root
    / "docs"
    / "01_policies_and_standards"
    / "rules"
    / "trae_069_commit_gateway_abuse_thresholds.yaml"
)

# 代码内默认值（YAML 缺失/解析失败时 fallback，与 P1 治本后的值一致）
# v1.3.0（2026-07-21）: 新增 force_merge_abuse_7d 维度（#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 6 维扩展）
DEFAULT_THRESHOLDS = {
    "warn_only_sustained_24h": 50,
    "emergency_commit_abuse_24h": 5,
    "allow_overlap_abuse_7d": 30,
    "forged_gw_marker_rate_24h": 3,
    "non_gw_commit_sustained_24h": 10,
    "force_merge_abuse_7d": 5,
}


def load_thresholds_from_yaml() -> dict[str, int]:
    """从 trae_069_commit_gateway_abuse_thresholds.yaml 加载阈值（P3-1 治本）。

    SSoT 铁律（trae_062）：规则数据真源是 YAML 文件。本函数从 YAML 加载阈值，
    替代原硬编码常量。fail-open：YAML 缺失/解析失败时返回 DEFAULT_THRESHOLDS
    （不阻断 reconciler，但记录 WARNING）。

    Returns:
        dict[str, int] — 6 维阈值字典，key 为维度名，value 为阈值 int。
    """
    try:
        if not THRESHOLDS_YAML_PATH.exists():
            logger.warning(
                "P3-1: thresholds YAML not found at %s, using defaults",
                THRESHOLDS_YAML_PATH,
            )
            return dict(DEFAULT_THRESHOLDS)
        import yaml

        with THRESHOLDS_YAML_PATH.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        thresholds_section = data.get("thresholds", {})
        result: dict[str, int] = {}
        for dim_name in DEFAULT_THRESHOLDS:
            dim_config = thresholds_section.get(dim_name, {})
            value = dim_config.get("value", DEFAULT_THRESHOLDS[dim_name])
            if not isinstance(value, int) or value < 0:
                logger.warning(
                    "P3-1: invalid threshold for %s (%r), using default %d",
                    dim_name,
                    value,
                    DEFAULT_THRESHOLDS[dim_name],
                )
                value = DEFAULT_THRESHOLDS[dim_name]
            result[dim_name] = value
        return result
    except Exception as e:  # noqa: BLE001 — YAML 加载失败不阻断 reconciler
        logger.warning(
            "P3-1: failed to load thresholds YAML (%s), using defaults",
            e,
        )
        return dict(DEFAULT_THRESHOLDS)


# 启动时加载阈值（fail-open：YAML 缺失时使用默认值）
_THRESHOLD_CONFIG = load_thresholds_from_yaml()

# 维度1: warn_only 持续低频（24h）——per-hour POST-COMMIT-GUARD 阈值 10/h 抓不到 5/h 持续
WARN_ONLY_24H_THRESHOLD = _THRESHOLD_CONFIG["warn_only_sustained_24h"]
# 维度2: emergency_commit 滥用（24h）—— P1-4 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）
# 历史：原阈值 5 → bc3cad107c 放松到 30（掩盖滥用）→ R1 回滚到 10（过渡期 2026-07-19~2026-08-02）
# P1-4 治本（2026-07-20）：heartbeat 已落地（#ARCH-HEARTBEAT-001），R1 过渡期不再需要。
# 同时 P1-3 已引入 scenario 过滤，dogfood/test/governance_fix 不计入 24h 计数，
# production 场景的真实 emergency_commit 应 < 5/24h（GitCommitGateway timeout 治本前允许极值）。
# 直接回滚到 5（原值）。
EMERGENCY_24H_THRESHOLD = _THRESHOLD_CONFIG["emergency_commit_abuse_24h"]
# 维度3: allow_overlap 滥用（7d）——gw_env=1 warn_only 持续 7d = session 注册表 bug
ALLOW_OVERLAP_7D_THRESHOLD = _THRESHOLD_CONFIG["allow_overlap_abuse_7d"]
# 维度4: forged_gw_marker 伪造率（24h）——任何伪造都 serious，3/天即 critical
FORGED_24H_THRESHOLD = _THRESHOLD_CONFIG["forged_gw_marker_rate_24h"]
# 维度5: non-GW commit 持续率（24h）——commit_gw_audit violations sum
NON_GW_24H_THRESHOLD = _THRESHOLD_CONFIG["non_gw_commit_sustained_24h"]
# 维度6: force_merge 滥用（7d）—— #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 6 维扩展（2026-07-21）
# session_worktree_merge(force=True) 逃生通道日常化 = pre-merge gate sys.path 问题
# 或 worktree 基础设施故障的信号。gate 层审计 .runtime/gate_audit/force_merge_usage.jsonl 计数。
FORCE_MERGE_7D_THRESHOLD = _THRESHOLD_CONFIG["force_merge_abuse_7d"]

# 时间窗口（秒）
_WINDOW_24H_SECONDS = 24 * 3600
_WINDOW_7D_SECONDS = 7 * 24 * 3600

# git log 超时（秒）
_GIT_LOG_TIMEOUT = 15

# === P3-6: 7d baseline 持久化（#ARCH-PREVENTABILITY-LAYER-001 Phase 3）===
# 系统层状态：6 维每日计数历史，由 reconciler 维护（类似 session_registry.json）。
# 存放在 .runtime/abuse_monitor/ 子目录（避免直写 .runtime 根，遵循 trae_071 三级分类）。
# 用途：P3-1 接入 AdaptiveThreshold 的 7d EWMA 基线数据源。
BASELINE_WINDOW_DAYS = 7  # 滚动保留 7d
_BASELINE_VERSION = "1.0"
# P3-1: AdaptiveThreshold factor（基线 × factor = 告警阈值，留 50% 余量给正常波动）
ADAPTIVE_FACTOR = 1.5

# === P3-3: 综合评分阈值（#ARCH-PREVENTABILITY-LAYER-001 Phase 3）===
# 基于健康度评分（health_score_calculator.calculate_health_score）的综合判定阈值。
# - score > BLOCK_NEXT_SCORE (0.9): 系统性失控，应 block_next session。
#   reconciler 是 post-commit 无法 block（commit 已入历史不可逆），降级为
#   critical_warn + 横幅强制 AI 看到，并提示应暂停后续 commit 排查根因。
# - score > CRITICAL_WARN_SCORE (0.7): 多维度叠加恶化，critical_warn 强制 AI 看到。
# - score <= CRITICAL_WARN_SCORE: 落入既有 1-2 维度 warn / clean 逻辑。
BLOCK_NEXT_SCORE = 0.9
CRITICAL_WARN_SCORE = 0.7

# metrics key 映射：classify_abuse 返回的简化 key → DEFAULT_THRESHOLDS 的标准 dim_name。
# baseline 文件按标准 dim_name 存储（与 trae_069 YAML 的 thresholds 段对齐）。
_METRICS_KEY_MAP = {
    "warn_only_24h": "warn_only_sustained_24h",
    "emergency_commit_24h": "emergency_commit_abuse_24h",
    "allow_overlap_7d": "allow_overlap_abuse_7d",
    "forged_gw_marker_24h": "forged_gw_marker_rate_24h",
    "non_gw_commit_24h": "non_gw_commit_sustained_24h",
    "force_merge_7d": "force_merge_abuse_7d",
}
# 反向映射：标准 dim_name → classify_abuse 的 metrics key（用于 compute_adaptive_thresholds）
_METRICS_KEY_MAP_REVERSE = {v: k for k, v in _METRICS_KEY_MAP.items()}


def _baseline_file(repo_root: Path) -> Path:
    """baseline 文件路径：.runtime/abuse_monitor/abuse_baseline.json。"""
    return repo_root / ".runtime" / "abuse_monitor" / "abuse_baseline.json"


def load_baseline(repo_root: Path) -> dict:
    """加载 7d baseline state（P3-6）。

    fail-open：文件缺失/解析失败返回空结构（reconciler 降级为无 baseline 不影响）。

    Returns:
        dict — {"version": str, "last_updated": int, "daily_records": list[dict]}
        每条 daily_record 形如：
            {"date": "YYYY-MM-DD", "timestamp": int, "metrics": {dim_name: count, ...}}
    """
    bf = _baseline_file(repo_root)
    if not bf.exists():
        return {"version": _BASELINE_VERSION, "last_updated": 0, "daily_records": []}
    try:
        data = json.loads(bf.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or "daily_records" not in data:
            return {"version": _BASELINE_VERSION, "last_updated": 0, "daily_records": []}
        return data
    except (OSError, json.JSONDecodeError) as e:
        logger.warning("P3-6: load baseline failed (%s), using empty", e)
        return {"version": _BASELINE_VERSION, "last_updated": 0, "daily_records": []}


def _save_baseline(repo_root: Path, baseline: dict) -> None:
    """持久化 baseline state（P3-6）。

    fail-open：写入失败仅记 warning（reconciler 永不抛异常）。
    """
    bf = _baseline_file(repo_root)
    try:
        bf.parent.mkdir(parents=True, exist_ok=True)
        bf.write_text(json.dumps(baseline, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as e:
        logger.warning("P3-6: save baseline failed: %s", e)


def record_daily_metrics(
    repo_root: Path,
    metrics: dict,
    now_ts: int,
) -> list[dict]:
    """将今日 6 维 metrics 追加到 baseline 并保留 7d 滚动窗口（P3-6）。

    同日多次记录覆盖（按 date 去重，保留最新），超过 7d 的旧记录裁剪。

    Args:
        repo_root: 仓库根路径。
        metrics: 6 维今日计数 dict（key 为 dim_name，value 为 int）。
            期望 key 与 DEFAULT_THRESHOLDS 一致。
        now_ts: 当前 Unix 时间戳。

    Returns:
        list[dict] — 更新后的 daily_records（7d 滚动窗口）。
    """
    baseline = load_baseline(repo_root)
    records = baseline.get("daily_records", [])
    if not isinstance(records, list):
        records = []

    # UTC date 字符串作为 dedup key（reconciler 跨时区运行可能产生不同 date，但同一日只保留最新）
    today_str = time.strftime("%Y-%m-%d", time.gmtime(now_ts))

    # 提取 6 维计数（按标准 dim_name 存储，metrics 中是简化 key，需映射）
    daily_metrics = {
        dim_name: int(metrics.get(src_key, metrics.get(dim_name, 0))) for src_key, dim_name in _METRICS_KEY_MAP.items()
    }

    # 同日覆盖：若已存在 today_str 记录，更新之；否则追加新记录
    new_record = {
        "date": today_str,
        "timestamp": now_ts,
        "metrics": daily_metrics,
    }
    found = False
    for i, rec in enumerate(records):
        if isinstance(rec, dict) and rec.get("date") == today_str:
            records[i] = new_record
            found = True
            break
    if not found:
        records.append(new_record)

    # 裁剪 7d 滚动窗口（按 timestamp 排序后保留最新 N 条）
    cutoff_ts = now_ts - BASELINE_WINDOW_DAYS * 24 * 3600
    records = [r for r in records if isinstance(r, dict) and r.get("timestamp", 0) >= cutoff_ts]
    records.sort(key=lambda r: r.get("timestamp", 0))

    baseline["version"] = _BASELINE_VERSION
    baseline["last_updated"] = now_ts
    baseline["daily_records"] = records
    _save_baseline(repo_root, baseline)
    return records


def compute_adaptive_thresholds(daily_records: list[dict]) -> dict:
    """从 7d baseline 计算各维度的自适应阈值（P3-1）。

    接入 AdaptiveThreshold（P3-0）：为 6 维各自创建 COUNT 模式 state，
    static_floor = 静态阈值（防止阈值过低掩盖问题），factor = ADAPTIVE_FACTOR。
    遍历 baseline 7d daily_records 调 observe_count，最后 get_threshold 得到
    自适应阈值 = max(ewma * factor, static_floor)。

    Args:
        daily_records: 7d baseline daily_records 列表（由 record_daily_metrics 返回）。

    Returns:
        dict — {dim_name: adaptive_threshold}，6 维自适应阈值。
        若 daily_records 为空，返回空 dict（调用方降级为纯静态阈值）。
    """
    if not daily_records:
        return {}

    at = AdaptiveThreshold()
    # 为 6 维配置 COUNT 模式：static_floor = 静态阈值（防自适应阈值低于下限）
    for dim_name, static_value in DEFAULT_THRESHOLDS.items():
        at.set_count_config(
            dim_name,
            static_floor=float(static_value),
            factor=ADAPTIVE_FACTOR,
        )

    # 遍历 7d daily_records，按 dim_name 调 observe_count
    for record in daily_records:
        if not isinstance(record, dict):
            continue
        rec_metrics = record.get("metrics", {})
        if not isinstance(rec_metrics, dict):
            continue
        for dim_name in DEFAULT_THRESHOLDS:
            count = rec_metrics.get(dim_name, 0)
            try:
                at.observe_count(dim_name, float(count))
            except (TypeError, ValueError):
                continue  # 跳过无效计数

    # 获取 6 维自适应阈值
    return {dim_name: at.get_threshold(dim_name) for dim_name in DEFAULT_THRESHOLDS}


def _reports_dir(repo_root: Path) -> Path:
    """reconcile_reports 目录路径：.runtime/reconcile_reports/。"""
    return repo_root / ".runtime" / "reconcile_reports"


def read_json_reports(repo_root: Path, prefix: str, since_ts: int) -> list[dict]:
    """读取指定前缀的报告文件，返回 timestamp >= since_ts 的报告列表。

    fail-open：目录不存在/读取失败返回空列表（滥用检测降级为无数据不触发）。

    Args:
        repo_root: 仓库根路径。
        prefix: 报告文件名前缀（如 "post_commit_guard" / "commit_gateway_audit"）。
        since_ts: Unix 时间戳，仅返回 timestamp >= since_ts 的报告。

    Returns:
        报告字典列表（每条含解析后的 timestamp 字段）。损坏的 JSON 跳过。
    """
    rdir = _reports_dir(repo_root)
    if not rdir.exists():
        return []
    reports: list[dict] = []
    try:
        for path in rdir.glob(f"{prefix}_*.json"):
            try:
                raw = path.read_text(encoding="utf-8")
                data = json.loads(raw)
            except (OSError, json.JSONDecodeError):
                continue  # 跳过损坏文件
            ts = data.get("timestamp", 0)
            if not isinstance(ts, (int, float)):
                continue
            if ts >= since_ts:
                reports.append(data)
    except OSError as e:
        logger.warning("commit_gateway_abuse_monitor: read %s reports failed: %s", prefix, e)
        return []
    return reports


def count_emergency_commits(repo_root: Path, since_hours: int) -> int:
    """统计最近 N 小时内 production 场景的 emergency_commit 数（维度2 真源）。

    emergency_commit 是 P2-1 合法逃生通道，但反复使用 = 系统性问题。

    P1-3 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
    按 scenario 过滤——只统计 commit message 含 [SCENARIO:production] 或
    不含 [SCENARIO:...] 标记的 emergency_commit（向后兼容）。
    dogfood / test / governance_fix 场景豁免，避免治本工作污染 24h 滥用计数。

    fail-open：git log 失败返回 0（降级为不触发维度2）。
    """
    try:
        result = run_subprocess_hidden(
            ["git", "log", f"--since={since_hours} hours ago", "--format=%B%x1f"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=_GIT_LOG_TIMEOUT,
        )
        if result.returncode != 0:
            return 0
        # %x1f (unit separator) 分隔 commit bodies
        count = 0
        for body in result.stdout.split("\x1f"):
            if "[GW:" not in body or "emergency" not in body:
                continue
            # P1-3: scenario 过滤——非 production 场景豁免
            # 向后兼容：无 [SCENARIO:...] 标记视为 production（旧 commit）
            if "[SCENARIO:" in body:
                # 提取 scenario 值
                start = body.find("[SCENARIO:") + len("[SCENARIO:")
                end = body.find("]", start)
                if end > start:
                    scenario = body[start:end].strip()
                    if scenario != "production":
                        continue  # dogfood/test/governance_fix 豁免
            count += 1
        return count
    except (subprocess.TimeoutExpired, Exception) as e:  # noqa: BLE001 — 计数失败不阻断
        logger.warning("commit_gateway_abuse_monitor: count emergency commits failed: %s", e)
        return 0


def count_allow_overlap_usage(repo_root: Path, since_ts: int) -> int:
    """统计 7d 窗口内真实 allow_overlap=True 提交数（维度3 真源）。

    治本（2026-07-20，sess-23300-20260720092540）：原实现以 post_commit_guard
    warn_only(gw_env=1) 事件反推 allow_overlap 滥用，混入 merge 后 reconciler
    auto-commit 的注册表生命周期伪影（1829/7d 持续误报，结构性必然超阈值）。
    改为读取 gate 层审计 ``.runtime/gate_audit/allow_overlap_usage.jsonl``
    （commit_gate_registry.check_all 在 allow_overlap=True 时落盘），只计真实逃生。

    fail-open：文件缺失/解析失败返回 0（无审计=无证据，不误报）。
    """
    audit_file = repo_root / ".runtime" / "gate_audit" / "allow_overlap_usage.jsonl"
    if not audit_file.exists():
        return 0
    count = 0
    try:
        with audit_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if int(rec.get("timestamp", 0)) >= since_ts:
                    count += 1
    except OSError as e:
        logger.warning("commit_gateway_abuse_monitor: read allow_overlap audit failed: %s", e)
        return 0
    return count


def count_force_merge_usage(repo_root: Path, since_ts: int) -> int:
    """统计 7d 窗口内真实 force=True session_worktree_merge 调用数（维度6 真源）。

    #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 6 维扩展（2026-07-21）：
    对标 count_allow_overlap_usage，读取 gate 层审计
    ``.runtime/gate_audit/force_merge_usage.jsonl``
    （session_worktree._audit_force_merge_usage 在 force=True 时落盘），
    只计真实 force_merge 逃生通道使用。

    fail-open：文件缺失/解析失败返回 0（无审计=无证据，不误报）。
    """
    audit_file = repo_root / ".runtime" / "gate_audit" / "force_merge_usage.jsonl"
    if not audit_file.exists():
        return 0
    count = 0
    try:
        with audit_file.open(encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if int(rec.get("timestamp", 0)) >= since_ts:
                    count += 1
    except OSError as e:
        logger.warning("commit_gateway_abuse_monitor: read force_merge audit failed: %s", e)
        return 0
    return count


def classify_abuse(
    post_commit_reports: list[dict],
    audit_reports: list[dict],
    emergency_count: int,
    now_ts: int,
    allow_overlap_count: int = 0,
    adaptive_thresholds: dict | None = None,
    force_merge_count: int = 0,
) -> dict:
    """六维滥用分类（纯函数，无副作用，便于单测）。

    P3-1 扩展（#ARCH-PREVENTABILITY-LAYER-001 Phase 3）：
    若传入 adaptive_thresholds，最终阈值 = max(adaptive, static)。
    防止自适应阈值低于静态下限掩盖真实恶化（ruling §5.3 风险治本）。

    v1.3.0 扩展（#ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001，2026-07-21）：
    新增维度6 force_merge_abuse_7d——session_worktree_merge(force=True) 逃生通道
    日常化检测。对标 allow_overlap 维度实现模式（gate 层审计 JSONL 计数）。

    Args:
        post_commit_reports: 7d 内的 post_commit_guard 报告列表。
        audit_reports: 24h 内的 commit_gateway_audit 报告列表。
        emergency_count: 24h 内 emergency_commit 数量。
        now_ts: 当前 Unix 时间戳。
        allow_overlap_count: 7d 内真实 allow_overlap=True 提交数（gate 层审计，
            由调用方经 count_allow_overlap_usage 传入）。
        adaptive_thresholds: P3-1 自适应阈值 dict（{dim_name: threshold}）。
            None 或空 dict 时降级为纯静态阈值（向后兼容）。
        force_merge_count: 7d 内真实 force=True session_worktree_merge 调用数
           （gate 层审计，由调用方经 count_force_merge_usage 传入）。

    Returns:
        {
            "dimensions_triggered": list[str],  # 触发的维度名
            "details": list[str],               # 每个维度的告警消息
            "metrics": dict,                    # 所有维度的原始数值 + 阈值（供报告落盘）
        }
    """
    # 计算各窗口的 since_ts
    since_24h = now_ts - _WINDOW_24H_SECONDS

    # === 维度1: warn_only 持续低频（24h）===
    warn_only_24h = sum(
        1
        for r in post_commit_reports
        if r.get("timestamp", 0) >= since_24h
        and r.get("action") == "warn_only"
        and r.get("violation") == "unregistered_session_id"
    )

    # === 维度3: allow_overlap 滥用（7d）—— gate 层审计真实计数（由调用方传入）===
    allow_overlap_7d = allow_overlap_count

    # === 维度6: force_merge 滥用（7d）—— gate 层审计真实计数（由调用方传入）===
    # #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 6 维扩展（2026-07-21）
    force_merge_7d = force_merge_count

    # === 维度4: forged_gw_marker 伪造率（24h）===
    forged_24h = sum(
        1
        for r in post_commit_reports
        if r.get("timestamp", 0) >= since_24h and r.get("violation") == "forged_gw_marker"
    )

    # === 维度5: non-GW commit 持续率（24h）——按 commit hash distinct 计数 ===
    # P3 (2026-07-20): 治本——原 sum(violations_count) 会重复计数（audit_window=20,
    # 多个报告覆盖同一 commit,导致 non_gw_24h 膨胀）。改为收集 violations[].hash
    # 去重后计数,精确反映 24h 内实际 non-GW commit 数。
    non_gw_hashes: set[str] = set()
    for r in audit_reports:
        if r.get("timestamp", 0) >= since_24h:
            vlist = r.get("violations", [])
            if isinstance(vlist, list):
                for v in vlist:
                    if isinstance(v, dict):
                        h = v.get("hash")
                        if h:
                            non_gw_hashes.add(h)
    non_gw_24h = len(non_gw_hashes)

    # === 维度2: emergency_commit 滥用（24h）—— 由调用方传入 emergency_count ===

    # P3-1: 计算有效阈值 = max(adaptive, static)
    # adaptive_thresholds 的 key 是标准 dim_name（与 DEFAULT_THRESHOLDS 一致）
    adaptive = adaptive_thresholds or {}

    def _effective(static_val: int, dim_name: str) -> int:
        """P3-1: 有效阈值 = max(adaptive, static)，防止自适应阈值低于静态下限。"""
        ad_val = adaptive.get(dim_name, 0.0)
        try:
            return max(int(static_val), int(ad_val))
        except (TypeError, ValueError):
            return static_val

    eff_warn_only = _effective(WARN_ONLY_24H_THRESHOLD, "warn_only_sustained_24h")
    eff_emergency = _effective(EMERGENCY_24H_THRESHOLD, "emergency_commit_abuse_24h")
    eff_allow_overlap = _effective(ALLOW_OVERLAP_7D_THRESHOLD, "allow_overlap_abuse_7d")
    eff_forged = _effective(FORGED_24H_THRESHOLD, "forged_gw_marker_rate_24h")
    eff_non_gw = _effective(NON_GW_24H_THRESHOLD, "non_gw_commit_sustained_24h")
    eff_force_merge = _effective(FORCE_MERGE_7D_THRESHOLD, "force_merge_abuse_7d")

    dimensions_triggered: list[str] = []
    details: list[str] = []

    if warn_only_24h > eff_warn_only:
        dimensions_triggered.append("warn_only_sustained_24h")
        details.append(
            f"warn_only 持续低频: {warn_only_24h}/24h > {eff_warn_only} 阈值"
            f"（static={WARN_ONLY_24H_THRESHOLD}, adaptive={adaptive.get('warn_only_sustained_24h', 0):.1f}）"
            f"——POST-COMMIT-GUARD per-hour 阈值抓不到的持续逃生通道滥用"
        )

    if emergency_count > eff_emergency:
        dimensions_triggered.append("emergency_commit_abuse_24h")
        details.append(
            f"emergency_commit 滥用: {emergency_count}/24h > {eff_emergency} 阈值"
            f"（static={EMERGENCY_24H_THRESHOLD}, adaptive={adaptive.get('emergency_commit_abuse_24h', 0):.1f}）"
            f"——逃生通道日常化（应为罕见），排查 session_worktree_merge 跨进程失效根因"
        )

    if allow_overlap_7d > eff_allow_overlap:
        dimensions_triggered.append("allow_overlap_abuse_7d")
        details.append(
            f"allow_overlap 滥用: {allow_overlap_7d}/7d > {eff_allow_overlap} 阈值"
            f"（static={ALLOW_OVERLAP_7D_THRESHOLD}, adaptive={adaptive.get('allow_overlap_abuse_7d', 0):.1f}）"
            f"——逃生通道日常化（gate 层审计真实计数），排查为何频繁 HELD-OVERLAP 撞车"
        )

    if forged_24h > eff_forged:
        dimensions_triggered.append("forged_gw_marker_rate_24h")
        details.append(
            f"forged_gw_marker 伪造率: {forged_24h}/24h > {eff_forged} 阈值"
            f"（static={FORGED_24H_THRESHOLD}, adaptive={adaptive.get('forged_gw_marker_rate_24h', 0):.1f}）"
            f"——严重治理失效（任何伪造都是 intentional），需立即排查"
        )

    if non_gw_24h > eff_non_gw:
        dimensions_triggered.append("non_gw_commit_sustained_24h")
        details.append(
            f"non-GW commit 持续率: {non_gw_24h}/24h > {eff_non_gw} 阈值"
            f"（static={NON_GW_24H_THRESHOLD}, adaptive={adaptive.get('non_gw_commit_sustained_24h', 0):.1f}）"
            f"——持续绕过 GitCommitGateway，排查 --no-verify 滥用或 commit-tree 绕过"
        )

    # 维度6: force_merge 滥用（7d）—— #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 扩展（2026-07-21）
    if force_merge_7d > eff_force_merge:
        dimensions_triggered.append("force_merge_abuse_7d")
        details.append(
            f"force_merge 滥用: {force_merge_7d}/7d > {eff_force_merge} 阈值"
            f"（static={FORCE_MERGE_7D_THRESHOLD}, adaptive={adaptive.get('force_merge_abuse_7d', 0):.1f}）"
            f"——session_worktree_merge(force=True) 逃生通道日常化，"
            f"排查 pre-merge gate sys.path 问题或 worktree 基础设施故障"
        )

    return {
        "dimensions_triggered": dimensions_triggered,
        "details": details,
        "metrics": {
            "warn_only_24h": warn_only_24h,
            "emergency_commit_24h": emergency_count,
            "allow_overlap_7d": allow_overlap_7d,
            "forged_gw_marker_24h": forged_24h,
            "non_gw_commit_24h": non_gw_24h,
            "force_merge_7d": force_merge_7d,
            "thresholds": {
                "warn_only_24h": WARN_ONLY_24H_THRESHOLD,
                "emergency_commit_24h": EMERGENCY_24H_THRESHOLD,
                "allow_overlap_7d": ALLOW_OVERLAP_7D_THRESHOLD,
                "forged_gw_marker_24h": FORGED_24H_THRESHOLD,
                "non_gw_commit_24h": NON_GW_24H_THRESHOLD,
                "force_merge_7d": FORCE_MERGE_7D_THRESHOLD,
            },
            # P3-1: 记录有效阈值与自适应阈值（供报告落盘 + 趋势追踪）
            "effective_thresholds": {
                "warn_only_24h": eff_warn_only,
                "emergency_commit_24h": eff_emergency,
                "allow_overlap_7d": eff_allow_overlap,
                "forged_gw_marker_24h": eff_forged,
                "non_gw_commit_24h": eff_non_gw,
                "force_merge_7d": eff_force_merge,
            },
            "adaptive_thresholds": {dim: float(adaptive.get(dim, 0.0)) for dim in DEFAULT_THRESHOLDS},
        },
    }


def make_commit_gateway_abuse_monitor_reconciler(gateway: "object") -> ReconcilerSpec:
    """构造 GATE-COMMIT-GW-ABUSE-MONITOR post-commit 持续滥用监控 reconciler。

    Args:
        gateway: GitCommitGateway 实例（仅用其 project_root）。

    Returns:
        ReconcilerSpec(gate_id=GATE_ID, priority=PRIORITY)。
        trigger 永远返回 True（任何 commit 都触发滥用监控——全局关注）。
    """
    project_root = gateway.project_root

    def _trigger(committed_files: list[str]) -> bool:
        # 任何 commit 都触发——滥用监控是全局关注，不限文件类型
        return True

    def _reconcile(committed_files: list[str], session_id: str) -> ReconcileResult:
        try:
            now_ts = int(time.time())
            since_24h = now_ts - _WINDOW_24H_SECONDS
            since_7d = now_ts - _WINDOW_7D_SECONDS

            # 1. 读取 7d 内的 post_commit_guard 报告（覆盖维度1/3/4）
            post_commit_reports = read_json_reports(
                project_root,
                "post_commit_guard",
                since_7d,
            )

            # 2. 读取 24h 内的 commit_gateway_audit 报告（覆盖维度5）
            audit_reports = read_json_reports(
                project_root,
                "commit_gateway_audit",
                since_24h,
            )

            # 3. 统计 24h 内 emergency_commit 数量（覆盖维度2）
            emergency_count = count_emergency_commits(project_root, 24)

            # 3.5 统计 7d 内真实 allow_overlap=True 使用次数（覆盖维度3 真源）
            # P1-1 治本（#ARCH-RECONCILER-HEALTH-WARN-ROOT-CAUSE-001）：
            # 原实现未调用 count_allow_overlap_usage，allow_overlap_count 默认 0，
            # 导致维度3 永远不触发（实际误报来自 L214 之前的 warn_only+gw_env=1 反推）。
            # 现改为读取 gate 层审计 .runtime/gate_audit/allow_overlap_usage.jsonl
            allow_overlap_count = count_allow_overlap_usage(project_root, since_7d)

            # 3.5b 统计 7d 内真实 force=True session_worktree_merge 调用数（覆盖维度6 真源）
            # #ARCH-GATE-ABUSE-SYSTEMIC-AUDIT-001 6 维扩展（2026-07-21）：
            # 对标 allow_overlap，读取 gate 层审计 .runtime/gate_audit/force_merge_usage.jsonl
            force_merge_count = count_force_merge_usage(project_root, since_7d)

            # 3.6 P3-1: 加载历史 baseline（不含今日）→ 计算自适应阈值
            # 自适应阈值基于历史 7d EWMA，今日计数稍后由 record_daily_metrics 追加。
            # 这样自适应阈值反映"历史基线"，不包含今日（避免当日计数自我影响阈值）。
            historical_baseline = load_baseline(project_root)
            historical_records = historical_baseline.get("daily_records", [])
            adaptive_thresholds = compute_adaptive_thresholds(historical_records)

            # 4. 六维分类（P3-1: 传入 adaptive_thresholds，有效阈值 = max(adaptive, static)）
            classification = classify_abuse(
                post_commit_reports,
                audit_reports,
                emergency_count,
                now_ts,
                allow_overlap_count=allow_overlap_count,
                adaptive_thresholds=adaptive_thresholds,
                force_merge_count=force_merge_count,
            )

            triggered = classification["dimensions_triggered"]
            details = classification["details"]
            metrics = classification["metrics"]

            # 4.5 P3-6: 将今日 6 维 metrics 追加到 baseline（7d 滚动窗口持久化）
            # 注意：必须在 classify_abuse 之后调用，因为 metrics 是今日计数。
            # record_daily_metrics 内部会裁剪 7d 旧记录并 save。
            try:
                record_daily_metrics(project_root, metrics, now_ts)
            except Exception as e:  # noqa: BLE001 — baseline 持久化失败不阻断 reconciler
                logger.warning("P3-6: record daily metrics failed: %s", e)

            # 4.6 P3-3: 计算 6 维加权健康度评分
            # 综合评分 >0.7 critical_warn, >0.9 block_next（post-commit 无法 block，
            # 降级为 critical_warn + 横幅）。阈值用 metrics["effective_thresholds"]
            # （P3-1: 有效阈值 = max(adaptive, static)），确保评分基于生效阈值。
            effective_thresholds = metrics.get("effective_thresholds") or metrics.get("thresholds", {})
            try:
                health = calculate_health_score(metrics, effective_thresholds)
                health_score = health.score
                health_triggered = health.triggered_dimensions
            except Exception as e:  # noqa: BLE001 — 评分失败不阻断 reconciler
                logger.warning("P3-3: calculate_health_score failed: %s", e)
                health_score = 0.0
                health_triggered = []

            # 5. 落盘审计报告（无论是否触发滥用都记录，供趋势追踪）
            report = {
                "gate_id": GATE_ID,
                "session_id": session_id,
                "dimensions_triggered": triggered,
                "metrics": metrics,
                "details": details,
                "post_commit_reports_read": len(post_commit_reports),
                "audit_reports_read": len(audit_reports),
                # P3-1: 记录自适应阈值是否启用（供报告消费方判断阈值来源）
                "adaptive_enabled": bool(adaptive_thresholds),
                "baseline_records_count": len(historical_records),
                # P3-3: 综合健康度评分（0.0=完全健康, 1.0=完全失控）
                "health_score": round(health_score, 4),
                "health_triggered_dimensions": health_triggered,
            }
            report_path, write_err = _write_reconcile_report(
                project_root,
                "commit_gateway_abuse_monitor",
                report,
            )
            if write_err:
                return ReconcileResult(
                    action="warn",
                    detail=f"abuse monitor done but report write failed: {write_err}",
                    gate_id=GATE_ID,
                )

            # 6. 判定 action（P3-3: 综合评分优先于维度计数判定）
            # 6.1 P3-3: block_next 阈值（>0.9）— post-commit 降级为 critical_warn + 横幅
            if health_score > BLOCK_NEXT_SCORE:
                return ReconcileResult(
                    action="critical_warn",
                    detail=(
                        f"ABUSE BLOCK_NEXT (health_score={health_score:.3f} > {BLOCK_NEXT_SCORE}): "
                        f"systemic abuse across multiple dimensions "
                        f"(triggered={triggered}, health_triggered={health_triggered}). "
                        f"PAUSE subsequent commits and investigate root cause. "
                        + "; ".join(details)
                        + f" (report={report_path.name})"
                    ),
                    gate_id=GATE_ID,
                )

            # 6.2 P3-3: critical_warn 阈值（>0.7）— 多维度叠加恶化
            if health_score > CRITICAL_WARN_SCORE:
                return ReconcileResult(
                    action="critical_warn",
                    detail=(
                        f"ABUSE CRITICAL (health_score={health_score:.3f} > {CRITICAL_WARN_SCORE}): "
                        f"multi-dimensional deterioration "
                        f"(triggered={triggered}, health_triggered={health_triggered}). "
                        + "; ".join(details)
                        + f" (report={report_path.name})"
                    ),
                    gate_id=GATE_ID,
                )

            # 6.3 既有逻辑：维度计数判定
            if not triggered:
                return ReconcileResult(
                    action="clean",
                    detail=(
                        f"abuse monitor clean: warn_only={metrics['warn_only_24h']}/24h, "
                        f"emergency={metrics['emergency_commit_24h']}/24h, "
                        f"allow_overlap={metrics['allow_overlap_7d']}/7d, "
                        f"forged={metrics['forged_gw_marker_24h']}/24h, "
                        f"non_gw={metrics['non_gw_commit_24h']}/24h, "
                        f"force_merge={metrics['force_merge_7d']}/7d, "
                        f"health_score={health_score:.3f}, "
                        f"report={report_path.name}"
                    ),
                    gate_id=GATE_ID,
                )

            # forged_gw_marker 触发 OR 3+ 维度 → critical_warn（横幅强制 AI 看到）
            forged_triggered = "forged_gw_marker_rate_24h" in triggered
            if forged_triggered or len(triggered) >= 3:
                return ReconcileResult(
                    action="critical_warn",
                    detail=(
                        f"ABUSE DETECTED ({len(triggered)} dimensions, health_score={health_score:.3f}): "
                        + "; ".join(details)
                        + f" (report={report_path.name})"
                    ),
                    gate_id=GATE_ID,
                )

            # 1-2 维度 → warn
            return ReconcileResult(
                action="warn",
                detail=(
                    f"abuse monitor warn ({len(triggered)} dimensions, health_score={health_score:.3f}): "
                    + "; ".join(details)
                    + f" (report={report_path.name})"
                ),
                gate_id=GATE_ID,
            )
        except Exception as e:  # noqa: BLE001 — reconciler 永不抛异常
            logger.warning("commit_gateway_abuse_monitor reconciler failed: %s", e)
            return ReconcileResult(
                action="warn",
                detail=f"monitor failed: {e}",
                gate_id=GATE_ID,
            )

    return ReconcilerSpec(
        gate_id=GATE_ID,
        trigger=_trigger,
        reconcile=_reconcile,
        priority=PRIORITY,
        file_ops=frozenset({"read", "write"}),
    )


# === Reverse-hierarchy backward-compat aliases (R5 private-assert elimination) ===
# Public names above are the primary API. These _-prefixed aliases are kept
# for backward compatibility with any external importer that still references them.
_ALLOW_OVERLAP_7D_THRESHOLD = ALLOW_OVERLAP_7D_THRESHOLD
_ADAPTIVE_FACTOR = ADAPTIVE_FACTOR
_BASELINE_WINDOW_DAYS = BASELINE_WINDOW_DAYS
_BLOCK_NEXT_SCORE = BLOCK_NEXT_SCORE
_CRITICAL_WARN_SCORE = CRITICAL_WARN_SCORE
_EMERGENCY_24H_THRESHOLD = EMERGENCY_24H_THRESHOLD
_FORGED_24H_THRESHOLD = FORGED_24H_THRESHOLD
_FORCE_MERGE_7D_THRESHOLD = FORCE_MERGE_7D_THRESHOLD
_GATE_ID = GATE_ID
_NON_GW_24H_THRESHOLD = NON_GW_24H_THRESHOLD
_PRIORITY = PRIORITY
_WARN_ONLY_24H_THRESHOLD = WARN_ONLY_24H_THRESHOLD
_THRESHOLDS_YAML_PATH = THRESHOLDS_YAML_PATH
_DEFAULT_THRESHOLDS = DEFAULT_THRESHOLDS
_load_thresholds_from_yaml = load_thresholds_from_yaml
_load_baseline = load_baseline
_read_json_reports = read_json_reports
_count_emergency_commits = count_emergency_commits
_count_allow_overlap_usage = count_allow_overlap_usage
_count_force_merge_usage = count_force_merge_usage
_classify_abuse = classify_abuse
_compute_adaptive_thresholds = compute_adaptive_thresholds
_record_daily_metrics = record_daily_metrics
