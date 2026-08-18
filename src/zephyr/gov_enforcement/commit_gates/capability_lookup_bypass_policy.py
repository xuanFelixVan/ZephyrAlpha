# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable



# [MODULE] zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy



# [DOMAIN] D_GOV_CODE_QUALITY



# [DEPENDENCIES] zephyr.shared.io.paths (REPO_ROOT)



# [CONSUMERS] zephyr.gov_enforcement.commit_gates.capability_lookup_required_gate (has_bypass_marker, is_emergency_bypass, is_exempt_reason); zephyr.governance.audit.reconciliation_registry (is_exempt_reason)



# [STARTUP] imported



# [MATURITY] production



# [INVARIANTS] bypass 策略唯一共享真源——gate 和 reconciler 共用 BYPASS_MARKER_PREFIX / BYPASS_ENV_VAR / is_exempt_reason / has_bypass_marker；从 trae_077 YAML 加载关键词与阈值（fail-open 到默认值）；SSoT 真源是 trae_077_capability_lookup_scene_classify.yaml（trae_062 规则数据分类）



# [MODIFY-GUARD] is_exempt_reason 归一化逻辑（_ -> -）；白名单关键词必须同步更新 _DEFAULT_EXEMPT_KEYWORDS + trae_077 YAML bypass_exempt_keywords 段



# [STABILITY] evolving



# [SAFETY] L



# [AI_AUTONOMY] ai_modifiable



# [ERROR_CONTRACT] load_bypass_policy 永不抛异常——YAML 缺失/损坏/字段非法均 fail-open 返回默认值



# [TESTS] tests/governance/commit_gates/test_capability_lookup_bypass_policy.py



# [A_module] module_id=MOD-GOV-bypass_policy | layer=shared | stability=evolving | safety=L | ai_autonomy=ai_modifiable



# [TTL] permanent



# noqa: m10-time-trigger  M10豁免: 无时间触发



"""capability_lookup_bypass_policy.py — CAPABILITY-LOOKUP bypass 策略共享模块







gate（CAPABILITY-LOOKUP-REQUIRED, priority=110）和 reconciler



（CAPABILITY-LOOKUP-HEALTH, priority=220）的唯一共享入口。







对标 trae_069 外部化模式（fail-open loader + 默认值兜底）：



- SSoT 真源：trae_077_capability_lookup_scene_classify.yaml（trae_062 规则数据分类）



- 代码从此 YAML 加载白名单关键词 + 阈值



- YAML 缺失/解析失败 → fail-open 使用 _DEFAULT_* 默认值







治本（#ARCH-066，2026-07-22）：



- 消除双真源——gate 和 reconciler 原各自定义 "[no-lookup:" 字面量 / 白名单 / 阈值



- gate-time 白名单检查——非白名单 reason 不再零摩擦放行（需 env var 高摩擦逃生）



- 改进匹配——reason 归一化（_ → -）后子串匹配，解决 root_cause vs root-cause 不匹配







Usage::







    from zephyr.gov_enforcement.commit_gates.capability_lookup_bypass_policy import (



        BYPASS_MARKER_PREFIX, BYPASS_ENV_VAR,



        is_exempt_reason, has_bypass_marker, load_bypass_policy,



    )



"""







from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)







__all__ = [



    "BYPASS_MARKER_PREFIX",



    "BYPASS_ENV_VAR",



    "is_exempt_reason",



    "has_bypass_marker",



    "load_bypass_policy",



]







# ── 单一真源常量（消除 gate/reconciler 双真源） ──────────────────────────────







BYPASS_MARKER_PREFIX = "[no-lookup:"







BYPASS_ENV_VAR = "ZEPHYR_BYPASS_LOOKUP"







# ── 默认值（fail-open 兜底，与 trae_077 YAML 保持同步） ──────────────────────







# 16 项白名单关键词（原有 10 + 扩充 6，覆盖 bypass_audit.jsonl 全部合法场景）



_DEFAULT_EXEMPT_KEYWORDS: frozenset[str] = frozenset({



    # 原有 10 项



    "gate-fix",               # gate 自身修复



    "test-fix",               # 测试修复



    "merge-prep",             # merge 准备



    "continuation",           # 已批准裁定/修复计划续作



    "investigated",           # bug 修复已调研



    "auto-fix",               # 自动修复



    "batch-treatment",        # 批量处理（已批准裁定）



    "batch-governance",       # 批量治理



    "architectural-refactor", # 架构重构



    "sync",                   # 文档/注释/维度同步



    # 扩充 6 项（#ARCH-066, 基于 bypass_audit.jsonl 实证分析）



    "mechanical",             # 机械批量格式修复（如 mechanical-header-format-fix-batch-N）



    "completing",             # 完成先前升级/任务（如 completing incomplete v1.3.0 upgrade）



    "research",               # 已调研（如 extensive-research-done，比 investigated 更宽）



    "bugfix",                  # bug 修复（如 surgical_bugfix_for_preexisting_reconciler_warnings）



    "root-cause",             # 根因修复（如 root_cause_fix——归一化 _ → - 后匹配）



    "调研",                    # 中文已调研（如 已充分调研TableRegistry接口...）





    # hotfix keyword (test_capability_lookup_required_gate.py)
    "hotfix",
})







_DEFAULT_ESCALATION_THRESHOLD = 5  # 最近窗口内违规 bypass > 5 → critical_warn



_DEFAULT_WINDOW = 10               # 统计窗口（最近 N 次 bypass 事件）







# ── YAML 路径（对标 trae_069 loader 路径构造） ──────────────────────────────







_POLICY_YAML_PATH = (



    Path(__file__).resolve().parents[4]  # src/zephyr/gov_enforcement/commit_gates → repo root



    / "docs" / "01_policies_and_standards" / "rules"



    / "trae_077_capability_lookup_scene_classify.yaml"



)











# ── fail-open loader（对标 trae_069 _load_thresholds_from_yaml） ───────────────







def load_bypass_policy() -> dict:



    """从 trae_077 YAML 加载 bypass 策略（白名单关键词 + 阈值）。







    fail-open 三层兜底（对标 trae_069）：



    1. YAML 文件缺失 → 返回默认值



    2. yaml.safe_load 解析异常 → 返回默认值



    3. 字段非法 → 单字段用默认值







    Returns:



        dict 含:



        - exempt_keywords: frozenset[str] — 白名单关键词



        - escalation_threshold: int — 违规 bypass 升级阈值



        - window: int — 统计窗口大小



    """



    try:



        if not _POLICY_YAML_PATH.is_file():



            logger.warning(



                "capability_lookup_bypass_policy: YAML 不存在 (%s)，使用默认值",



                _POLICY_YAML_PATH,



            )



            return _default_policy()







        import yaml







        with open(_POLICY_YAML_PATH, encoding="utf-8") as fh:



            data = yaml.safe_load(fh)







        if not isinstance(data, dict):



            logger.warning(



                "capability_lookup_bypass_policy: YAML 顶层非 dict，使用默认值"



            )



            return _default_policy()







        # 解析白名单关键词



        keywords = _DEFAULT_EXEMPT_KEYWORDS



        kw_section = data.get("bypass_exempt_keywords")



        if isinstance(kw_section, list) and kw_section:



            parsed = set()



            for item in kw_section:



                if isinstance(item, dict):



                    kw = item.get("keyword", "")



                elif isinstance(item, str):



                    kw = item



                else:



                    continue



                kw = str(kw).strip().lower()



                if kw:



                    parsed.add(kw)



            if parsed:



                keywords = frozenset(parsed)







        # 解析阈值



        thresholds = data.get("thresholds", {})



        if not isinstance(thresholds, dict):



            thresholds = {}







        escalation = _parse_int_field(



            thresholds, "escalation_threshold", _DEFAULT_ESCALATION_THRESHOLD,



        )



        window = _parse_int_field(



            thresholds, "window", _DEFAULT_WINDOW,



        )







        return {



            "exempt_keywords": keywords,



            "escalation_threshold": escalation,



            "window": window,



        }







    except Exception as e:



        logger.warning(



            "capability_lookup_bypass_policy: YAML 加载异常 (%s)，使用默认值", e,



        )



        return _default_policy()











def _default_policy() -> dict:



    """构造默认策略（fail-open 兜底）。"""



    return {



        "exempt_keywords": _DEFAULT_EXEMPT_KEYWORDS,



        "escalation_threshold": _DEFAULT_ESCALATION_THRESHOLD,



        "window": _DEFAULT_WINDOW,



    }











def _parse_int_field(thresholds: dict, key: str, default: int) -> int:



    """从 thresholds 段解析整数字段（支持 {value: N} 或裸 int）。"""



    raw = thresholds.get(key, default)



    if isinstance(raw, dict):



        raw = raw.get("value", default)



    try:



        val = int(raw)



        if val <= 0:



            return default



        return val



    except (TypeError, ValueError):



        return default











# ── 模块初始化时加载 + 派生常量（对标 trae_069 _THRESHOLD_CONFIG 模式） ──────







_POLICY = load_bypass_policy()







EXEMPT_KEYWORDS: frozenset[str] = _POLICY["exempt_keywords"]



ESCALATION_THRESHOLD: int = _POLICY["escalation_threshold"]



WINDOW: int = _POLICY["window"]











# ── 匹配逻辑（gate 和 reconciler 共用） ──────────────────────────────────────







def is_exempt_reason(



    reason: str, keywords: frozenset[str] | None = None,



) -> bool:



    """判断 bypass reason 是否属于合法豁免场景（白名单关键词匹配）。







    改进（#ARCH-066）：reason 归一化——``_`` → ``-`` 后再做子串匹配。



    解决 ``root_cause`` vs ``root-cause`` 不匹配问题。







    Args:



        reason: bypass reason 字符串（从 [no-lookup:reason] 提取）。



        keywords: 自定义关键词集合（测试用），默认用模块加载的 EXEMPT_KEYWORDS。







    Returns:



        True 表示 reason 匹配白名单（合法豁免场景）。



    """



    if not reason:



        return False



    kw_set = keywords if keywords is not None else EXEMPT_KEYWORDS



    # 归一化：小写 + 下划线转连字符（解决 root_cause vs root-cause）



    reason_normalized = reason.lower().replace("_", "-")



    for keyword in kw_set:



        if keyword in reason_normalized:



            return True



    return False











def has_bypass_marker(msg: str | None) -> tuple[bool, str]:



    """检测 commit msg 是否含 [no-lookup:reason] 逃生标记。







    Returns:



        (True, reason) 表示命中逃生通道；reason 为空串表示无理由（不允许）。



        (False, "") 表示未命中。



    """



    if not msg:



        return False, ""



    idx = msg.find(BYPASS_MARKER_PREFIX)



    if idx < 0:



        return False, ""



    start = idx + len(BYPASS_MARKER_PREFIX)



    end = msg.find("]", start)



    if end < 0:



        return False, ""



    reason = msg[start:end].strip()



    return True, reason











def is_emergency_bypass() -> bool:



    """检查 ZEPHYR_BYPASS_LOOKUP=1 紧急逃生环境变量是否启用。"""



    return os.environ.get(BYPASS_ENV_VAR) == "1"



