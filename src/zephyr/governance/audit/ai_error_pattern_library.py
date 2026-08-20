# [BLUEPRINT] MOD-GOV_ERROR_PATTERN_LIBRARY | docs/03_modules/_domain_governance/blueprint.md | §ARCH-PREVENTABILITY-LAYER-001 Phase 4 P4-1
# [MODULE] zephyr.governance.audit.ai_error_pattern_library
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES] zephyr.governance.audit.error_pattern_consumer_reconciler (compute_error_pattern_id); stdlib (json, logging, pathlib)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.session_worktree
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 只读查询接口——不修改源聚合文件；加载失败降级为空库（fail-open）；所有查询方法 O(1) 或 O(n)
# [MODIFY-GUARD] _DEFAULT_PATTERNS_SUBDIR / _DEFAULT_PATTERNS_FILENAME / _SOURCE_ACTION_HINTS
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 加载/解析失败降级为空库（is_empty=True），所有查询返回 None 或空列表
# [TESTS] tests/governance/audit/test_ai_error_pattern_library.py
# [A_module] module_id=MOD-GOV_ERROR_PATTERN_LIBRARY | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""

ai_error_pattern_library.py — AI 错误模式库（只读查询接口）。

P4-1（#ARCH-PREVENTABILITY-LAYER-001 Phase 4，2026-07-20）
----------------------------------------------------------
- **治本动机**：P4-1b ``error_pattern_consumer_reconciler`` 已将 AI 行为遥测
  JSONL 聚合到 ``.runtime/ai_error_patterns/aggregated_patterns.json``，但
  缺乏统一的查询接口供 session 启动 / gate 决策 / AI 反思使用。本模块是
  P4-1b 聚合输出的**只读消费者**，提供模式查询、匹配、Top N、修复建议
  等能力。
- **设计原则**：
  1. **只读**——绝不修改源聚合文件（写者是 P4-1b consumer，职责分离）
  2. **fail-open**——加载失败降级为空库，所有查询返回 None 或空列表，
     不阻断调用方（与 P4-1b 一致的失败语义）
  3. **O(1) 指纹查表**——``match_pattern`` 使用
     :func:`compute_error_pattern_id` 计算指纹后 dict 查表，无需遍历
  4. **rule-based 修复建议**——``suggest_action`` 基于模式的
     persistence/severity/source 推断修复策略（无 ML 依赖）
- **典型用法**::

      from zephyr.governance.audit.ai_error_pattern_library import (
          get_default_library,
      )

      lib = get_default_library()
      if not lib.is_empty:
          top = lib.top_patterns(n=5)
          for pat in top:
              print(pat.pattern_id, pat.count, lib.suggest_action(pat.pattern_id))

      # 在错误处理路径中匹配已知模式
      pat = lib.match_pattern("ConnectionError", "transient", "dependency")
      if pat:
          print(f"known pattern (count={pat.count}): {lib.suggest_action(pat.pattern_id)}")

- **与 P4-1b 的关系**：本模块是 P4-1b 聚合输出的下游消费者，无写入
  职责。P4-1b 每次 commit 触发全量重扫，覆盖更新
  ``aggregated_patterns.json``；本模块的 ``reload()`` 重新从磁盘加载。

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 错误模式聚合文件 JSON
#   fields: total_events/last_updated/patterns[]（pattern_id/error_type/persistence/source/count/expectation_dist/severity_dist 等）
#   code: .runtime/ai_error_patterns/aggregated_patterns.json L71-72
# - id: I2
#   name: 查询条件 参数组
#   fields: pattern_id 或 (error_type, persistence, source) 三元组 / TopN 的 n
#   code: get_pattern/find_patterns/match_pattern/top_patterns L284-332
# 层: 算法
# - id: A1
#   name_zh: ① 失败开放加载建索引
#   name_en: AIErrorPatternLibrary._load
#   intro: 读聚合 JSON 容错解析成模式列表并建指纹索引，坏了就降级空库
#   desc: 读文件→json.loads→逐条 ErrorPattern.from_dict（缺字段默认值/强转失败跳过）→无 pattern_id 脏数据跳过→建 {pid: pat} 索引；任何异常 return 空库
#   inputs: I1
#   outputs: 模式列表 + O(1) 索引
#   invariant: 只读不改源文件；fail-open 降级为空库
# - id: A2
#   name_zh: ② 三元组指纹匹配
#   name_en: match_pattern/is_known_pattern
#   intro: 用 错误类型×持续性×来源 算指纹直接查表认熟人
#   desc: compute_error_pattern_id(error_type, persistence, source) → dict.get O(1)，命中返回模式否则 None
#   inputs: I2 A1
#   outputs: ErrorPattern 或 None
# - id: A3
#   name_zh: ③ 属性过滤与 TopN
#   name_en: find_patterns/top_patterns
#   intro: 按维度过滤模式并按出现次数降序，或直接取前 N 名
#   desc: 三维度可选过滤（None 不过滤）→ count 降序；top_patterns 排序后切前 n
#   inputs: I2 A1
#   outputs: ErrorPattern 列表
# - id: A4
#   name_zh: ④ 规则修复建议
#   name_en: suggest_action/_suggest_action_for_pattern
#   intro: 按持续性和严重度套规则模板给修复建议，再叠加来源维度提示
#   desc: permanent+fatal/blocking→立即修复；permanent+degraded→排查根因；intermittent→监控复现；transient→重试退避/监控趋势；末尾拼 _SOURCE_ACTION_HINTS
#   inputs: I2 A1
#   outputs: 修复建议字符串（未知模式返回"未知模式，无可建议"）
# 层: 输出
# - id: O1
#   name_zh: 模式查询结果
#   name_en: ErrorPattern query results
#   intro: 单个模式或按 count 降序的模式列表，供 session 启动/gate 决策/AI 反思
#   downstream: zephyr.gov_enforcement.rule_bridge.session_worktree（[CONSUMERS] 头）
# - id: O2
#   name_zh: 修复建议文本
#   name_en: suggested action str
#   intro: 面向 AI/人的一句话修复策略建议
#   downstream: zephyr.gov_enforcement.rule_bridge.session_worktree（[CONSUMERS] 头）
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A2
# I2 --> A3
# I2 --> A4
# A1 --> A2
# A1 --> A3
# A1 --> A4
# A2 --> O1
# A3 --> O1
# A4 --> O2
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from zephyr.governance.audit.error_pattern_consumer_reconciler import (
    compute_error_pattern_id,
)

logger = logging.getLogger(__name__)

# 聚合文件默认位置（与 error_pattern_consumer_reconciler._OUTPUT_SUBDIR 一致）
_DEFAULT_PATTERNS_SUBDIR = Path(".runtime", "ai_error_patterns")
_DEFAULT_PATTERNS_FILENAME = "aggregated_patterns.json"


@dataclass
class ErrorPattern:
    """单个错误模式（聚合后的一条记录）。

    与 :func:`error_pattern_consumer_reconciler.aggregate_error_patterns`
    输出的 ``patterns[i]`` 字段一一对应。
    """

    pattern_id: str
    error_type: str
    persistence: str
    source: str
    count: int
    first_seen: str
    last_seen: str
    expectation_dist: dict[str, int] = field(default_factory=dict)
    severity_dist: dict[str, int] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ErrorPattern":
        """从聚合 JSON 的单条 dict 构造 ErrorPattern（fail-open）。

        缺失字段使用默认值，类型不匹配尝试强转，转换失败跳过该字段。
        """

        def _get_str(key: str, default: str = "") -> str:
            v = d.get(key, default)
            return str(v) if v is not None else default

        def _get_int(key: str, default: int = 0) -> int:
            v = d.get(key, default)
            try:
                return int(v) if v is not None else default
            except (TypeError, ValueError):
                return default

        def _get_dict(key: str) -> dict[str, int]:
            v = d.get(key, {})
            if not isinstance(v, dict):
                return {}
            out: dict[str, int] = {}
            for k, val in v.items():
                try:
                    out[str(k)] = int(val)
                except (TypeError, ValueError):
                    continue
            return out

        return cls(
            pattern_id=_get_str("pattern_id"),
            error_type=_get_str("error_type"),
            persistence=_get_str("persistence"),
            source=_get_str("source"),
            count=_get_int("count"),
            first_seen=_get_str("first_seen"),
            last_seen=_get_str("last_seen"),
            expectation_dist=_get_dict("expectation_dist"),
            severity_dist=_get_dict("severity_dist"),
        )

    @property
    def dominant_severity(self) -> str:
        """返回出现次数最多的 severity（平局取字典序最小）。"""
        if not self.severity_dist:
            return "unknown"
        # 平局时 max() 取首个最大——为稳定输出，按 (-count, key) 排序后取首
        return sorted(self.severity_dist.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    @property
    def unexpected_ratio(self) -> float:
        """返回 unexpected 占比（0.0~1.0）。

        无 expectation_dist 时返回 0.0。
        """
        if not self.expectation_dist:
            return 0.0
        total = sum(self.expectation_dist.values())
        if total <= 0:
            return 0.0
        return self.expectation_dist.get("unexpected", 0) / total


# source 维度补充建议（persistence×severity 主建议之外的可叠加 hint）
_SOURCE_ACTION_HINTS: dict[str, str] = {
    "dependency": "检查依赖服务状态与版本兼容性",
    "internal": "检查内部逻辑/配置/资源",
    "client": "检查客户端输入/请求格式",
    "server": "检查服务端负载/容量/配置",
}


def _suggest_action_for_pattern(pat: ErrorPattern) -> str:
    """基于模式属性推断修复建议（rule-based）。

    规则优先级（与 :data:`_SOURCE_ACTION_HINTS` 叠加）：
    1. permanent + fatal/blocking → 立即修复
    2. permanent + degraded → 排查根因
    3. intermittent → 监控 + 识别触发条件
    4. transient + blocking → 重试 + 指数退避
    5. transient + degraded → 监控趋势
    6. source 维度补充建议
    """
    sev = pat.dominant_severity
    persistence = pat.persistence
    source = pat.source

    if persistence == "permanent":
        if sev in ("fatal", "blocking"):
            main = "立即修复：permanent + {0} 错误必须阻断流水线".format(sev)
        elif sev == "degraded":
            main = "排查根因：permanent 错误意味着配置/逻辑缺陷"
        else:
            main = "排查 permanent 错误根因"
    elif persistence == "intermittent":
        main = "监控 + 识别触发条件：intermittent 错误需复现路径分析"
    elif persistence == "transient":
        if sev in ("fatal", "blocking"):
            main = "重试 + 指数退避：transient + {0} 错误可恢复".format(sev)
        elif sev == "degraded":
            main = "监控趋势：transient + degraded 错误观察是否升级"
        else:
            main = "观察 transient 错误趋势"
    else:
        main = "未知 persistence 类型，先分类错误"

    hint = _SOURCE_ACTION_HINTS.get(source)
    if hint:
        return f"{main}；{hint}"
    return main


class AIErrorPatternLibrary:
    """AI 错误模式库（只读查询接口）。

    加载失败降级为空库（fail-open），所有查询返回 None 或空列表。
    """

    def __init__(self, patterns_path: Path) -> None:
        self._path = patterns_path
        self._patterns: list[ErrorPattern] = []
        self._index: dict[str, ErrorPattern] = {}
        self._total_events: int = 0
        self._last_updated: int = 0
        self._load()

    # ── Stage 4 公共化（2026-07-29）：只读 properties ──
    @property
    def path(self):
        """只读：path（Stage 4 公共化）。"""
        return self._path

    @path.setter
    def path(self, value):
        """写入：path（Stage 4 公共化）。"""
        self._path = value

    def _load(self) -> None:
        """从磁盘加载聚合文件（fail-open）。

        文件不存在 / JSON 损坏 / 字段缺失一律降级为空库。
        """
        self._patterns = []
        self._index = {}
        self._total_events = 0
        self._last_updated = 0

        try:
            text = self._path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            logger.debug("ai_error_pattern_library: read %s failed (%s)", self._path, e)
            return

        try:
            data = json.loads(text)
        except json.JSONDecodeError as e:
            logger.warning("ai_error_pattern_library: parse %s failed (%s)", self._path, e)
            return

        if not isinstance(data, dict):
            logger.warning("ai_error_pattern_library: %s root is not dict", self._path)
            return

        try:
            self._total_events = int(data.get("total_events", 0))
        except (TypeError, ValueError):
            self._total_events = 0
        try:
            self._last_updated = int(data.get("last_updated", 0))
        except (TypeError, ValueError):
            self._last_updated = 0

        patterns_raw = data.get("patterns", [])
        if not isinstance(patterns_raw, list):
            logger.warning("ai_error_pattern_library: patterns field is not list")
            return

        for raw in patterns_raw:
            if not isinstance(raw, dict):
                continue
            pat = ErrorPattern.from_dict(raw)
            if not pat.pattern_id:
                continue  # 跳过无 pattern_id 的脏数据
            self._patterns.append(pat)
            self._index[pat.pattern_id] = pat

    def reload(self) -> None:
        """重新从磁盘加载（清除当前缓存）。"""
        self._load()

    def get_pattern(self, pattern_id: str) -> ErrorPattern | None:
        """按 pattern_id 查询（O(1)）。"""
        return self._index.get(pattern_id)

    def find_patterns(
        self,
        *,
        error_type: str | None = None,
        persistence: str | None = None,
        source: str | None = None,
    ) -> list[ErrorPattern]:
        """按属性过滤查询（O(n)）。

        所有参数均为可选，None 表示不过滤该维度。返回列表按 count 降序。
        """
        out: list[ErrorPattern] = []
        for pat in self._patterns:
            if error_type is not None and pat.error_type != error_type:
                continue
            if persistence is not None and pat.persistence != persistence:
                continue
            if source is not None and pat.source != source:
                continue
            out.append(pat)
        out.sort(key=lambda p: p.count, reverse=True)
        return out

    def top_patterns(self, n: int = 10) -> list[ErrorPattern]:
        """返回出现次数 Top N 的模式（按 count 降序）。"""
        if n <= 0:
            return []
        return sorted(self._patterns, key=lambda p: p.count, reverse=True)[:n]

    def match_pattern(
        self,
        error_type: str,
        persistence: str,
        source: str,
    ) -> ErrorPattern | None:
        """按 (error_type, persistence, source) 三元组匹配已知模式。

        使用 :func:`compute_error_pattern_id` 计算指纹后 dict 查表（O(1)）。
        三元组是错误模式最稳定身份标识，与 P4-1b 聚合逻辑一致。
        """
        pid = compute_error_pattern_id(error_type, persistence, source)
        return self._index.get(pid)

    def is_known_pattern(
        self,
        error_type: str,
        persistence: str,
        source: str,
    ) -> bool:
        """判断三元组是否为已知模式（O(1)）。"""
        return self.match_pattern(error_type, persistence, source) is not None

    def suggest_action(self, pattern_id: str) -> str:
        """返回该模式的修复建议（rule-based）。

        未知 pattern_id 返回"未知模式，无可建议"。
        """
        pat = self._index.get(pattern_id)
        if pat is None:
            return "未知模式，无可建议"
        return _suggest_action_for_pattern(pat)

    @property
    def total_patterns(self) -> int:
        """模式总数。"""
        return len(self._patterns)

    @property
    def total_events(self) -> int:
        """聚合事件总数（来自聚合文件的 total_events 字段）。"""
        return self._total_events

    @property
    def last_updated(self) -> int:
        """聚合文件最后更新时间（Unix 时间戳，0 表示未加载）。"""
        return self._last_updated

    @property
    def is_empty(self) -> bool:
        """库是否为空（加载失败或无模式时为 True）。"""
        return len(self._patterns) == 0


def get_default_library(project_root: Path | None = None) -> AIErrorPatternLibrary:
    """使用默认路径构造 AIErrorPatternLibrary。

    Args:
        project_root: 项目根目录。None 时使用当前工作目录。

    Returns:
        AIErrorPatternLibrary — 加载 ``<project_root>/.runtime/ai_error_patterns/aggregated_patterns.json``。
        文件不存在时返回空库（fail-open）。
    """
    root = Path(project_root) if project_root else Path.cwd()
    path = root / _DEFAULT_PATTERNS_SUBDIR / _DEFAULT_PATTERNS_FILENAME
    return AIErrorPatternLibrary(path)
