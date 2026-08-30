# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.translation_coverage_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec, is_test_exempt); zephyr.shared.io.paths (REPO_ROOT); scripts.governance._shared.module_translation_loader (get_module_translation, is_generic_plain_zh, is_generic_plain_suffix)
# [CONSUMERS] zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 检测 staged 新增 .py 文件（src/zephyr/ + scripts/ 下，tests/ 豁免）在 module_translation_registry.yaml 有非空且非通用模板的 plain_zh 大白话简介；翻译真源不可达时 fail-open（环境异常非违规，对标 NEW-FILE-DEPGRAPH-ENFORCEMENT）；_OBSERVATION_PERIOD=False 硬阻断模式（2026-08-02 观察期结束，drift 已清零转 fail-closed）；只读查询（loader 只读 YAML）；bootstrap 豁免——只检测本次 commit 新增文件，现有全量条目不受影响
# [MODIFY-GUARD] gate_id="TRANSLATION-COVERAGE"；check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——YAML/git/loader 异常降级为 fail-open（passed=True，logger.warning）；检出违规则 fail-closed 硬阻断（passed=False，_OBSERVATION_PERIOD=False 2026-08-02 转硬阻断）
# [TESTS] tests/governance/commit_gates/test_translation_coverage_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""
translation_coverage_gate.py — 新建 .py 文件大白话简介覆盖率门禁（TRANSLATION-COVERAGE）

检测 staged 新增 .py 文件（src/zephyr/ + scripts/ 下，tests/ 豁免）在翻译真源
``module_translation_registry.yaml`` 中是否有**非空且非通用模板**的 plain_zh 大白话简介。

病根（第一性原理）
-----------------
节点标签质量治理把全量条目的 plain_zh 合格率提到 100%（0 通用模板），但治标不治本——
新模块仍可持续制造缺口：AI 新建 .py 文件时不写大白话简介，事后靠审计→批量修→提交补救。
100% AI 开发下，事后治理永远滞后于缺口制造。本 gate 把"新模块必有大白话简介"从君子协定
升级为提交时技术强制（对标 NEW-FILE-DEPGRAPH-ENFORCEMENT 把 L1 铁律升级为技术强制）。

真源边界（SSoT 分类铁律 TRAE-062）
----------------------------------
模块翻译属**规则数据** → 真源是 YAML 文件。本 gate 只读 YAML 校验，不写。配套写入工具
``scripts/governance/d3_metadata/add_module_translation.py`` 是 YAML 合规写入入口。
与 depgraph（架构数据，DB 真源）正交，互不写入。

治本方案（四层防御 Layer 2）
------------------------
本 gate 是 Layer 2（提交时硬阻断），与 Layer 0（add_module_translation.py 合规写入工具）、
Layer 1（apply_depgraph.py 登记时 warn）、Layer 4（post-commit reconciler 存量对账）配合
（is_generic 质量检测内嵌于本 gate 与 Layer 4 reconciler，非独立层；canonical Layer 0/1/2/4）：
  1. ``git diff --cached --name-only --diff-filter=A`` 获取 staged 新增 .py 文件
  2. 过滤范围：src/zephyr/ 或 scripts/ 下，tests/ 豁免（对标 NEW-FILE-DEPGRAPH-ENFORCEMENT）
  3. 对每个新 .py 查翻译真源：entry 存在 + plain_zh 非空 + CJK≥8 + 非通用模板
  4. 违规 → 阻断（观察期 warn），提示 AI 运行 add_module_translation.py

设计权衡
--------
1. **硬阻断模式（_OBSERVATION_PERIOD=False，2026-08-02 转正）**：观察期已结束——
   Step 1 收窄范围（豁免 tests/demos/test_ 文件）+ Step B 补齐 108 条 missing 简介，
   drift_report 三类漂移全清零，无误报风险。违规时 return (False, msg) 阻断提交。
   （对标 GATE-DEBT-BRIDGE/GATE-SILENT-DEGRADATION 的 warn→hard 分阶段模式。）
2. **范围与 depgraph gate 同**（src/zephyr/+scripts/，tests 豁免）：depgraph 已要求这些 .py
   登记节点，节点必有简介是自然延伸，两 gate 同范围保证一致性。
3. **fail-open on loader error**：YAML 不可达时不阻断（环境异常非违规，对标 depgraph gate）。
4. **bootstrap 豁免**：只检测本次 commit 新增文件，现有全量条目不受影响。
5. **priority=59**：在 NEW-FILE-DEPGRAPH-ENFORCEMENT(58) 之后、CREATE-GUARD(60) 之前
   ——depgraph 结构登记检查应先于翻译完整性检查（先确认是节点，再要求节点有简介）。
6. **质量检测复用 loader**：is_generic_plain_zh/is_generic_plain_suffix 与生成器候选链
   同一真源，防 AI 填"提供包入口和模块加载功能"糊弄。

Usage::

    from zephyr.gov_enforcement.commit_gates.translation_coverage_gate import (
        make_translation_coverage_gate,
    )

    registry.register(make_translation_coverage_gate())
    # commit() 内部：registry.check_all(gateway, files, session_id=sid, ...)

# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: 模块内部数据
#   fields: 无公共形参/无再导出（AST 事实）
#   code: translation_coverage_gate.py
# 层: 算法
# - id: A1
#   name_zh: ① make_translation_coverage_gate
#   name_en: make_translation_coverage_gate
#   intro: 构造新建 .py 文件大白话简介覆盖率门禁 GateSpec。
#   desc: 构造新建 .py 文件大白话简介覆盖率门禁 GateSpec。 Returns: GateSpec(gate_id="TRANSLATION-COVERAGE", priorit…；源码 L280-L347
#   inputs: 无参数
#   outputs: GateSpec
# 层: 输出
# - id: O1
#   name_zh: GateSpec
#   name_en: GateSpec
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: zephyr.gov_enforcement.rule_bridge.git_commit_gateway.GitCommitGateway.__init__
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# A1 --> O1
"""

from __future__ import annotations

import logging
import os
import re
import sys

from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec, is_test_exempt

logger = logging.getLogger(__name__)

__all__ = ["make_translation_coverage_gate"]

# 观察期开关（治本防上线即卡死）：True=违规则 warn 不阻断；False=违规则硬阻断。
# 2026-08-02 观察期结束转硬阻断：drift_report 已清零（missing/short/generic 全 0），
# 范围收窄（Step 1）+ 存量补齐（Step B）均已完成，无误报风险。
_OBSERVATION_PERIOD = False

# plain_zh 最低 CJK 字符数（与 add_module_translation.py 写入工具一致，防过短无信息简介）
_MIN_CJK = 8

# 范围限定：src/zephyr/ + scripts/ 下的 .py 能力模块（tests/demos/test_ 文件豁免）
_SRC_ZEPHYR_PREFIX = "src/zephyr/"
_SCRIPTS_PREFIX = "scripts/"


def _is_in_scope(file_path: str) -> bool:
    """判断 file_path 是否在检测范围内（能力模块，需大白话简介）。

    范围：src/zephyr/ + scripts/ 下的 .py 能力模块。豁免（非能力模块，不需要大白话简介）：
      - tests/ 路径段（is_test_exempt 单一真源，含 scripts/tests/）—— 测试脚本
      - demos/ 路径段 —— 演示脚本
      - test_*.py / *_test.py 文件名 —— 测试文件（任意层级，含 backup/test_*、construction/test_*）
      - __init__.py —— 包初始化，不构成独立模块
      - _archive/ —— 归档废弃代码

    治本（2026-08-02，#ARCH-TRANSLATION-SCOPE-NARROW）：原范围过宽——scripts/tests/*、
    scripts/demos/*、scripts/backup/test_* 等测试/演示脚本被误判为需翻译的能力模块，
    在 reconciler 侧制造漂移误报（reconciler 还漏调 is_test_exempt，gate 与 reconciler
    两处 _is_in_scope 反方向不一致）。现统一收窄。本函数与
    translation_coverage_reconciler._is_in_scope MUST 保持一致（同范围铁律——两处复制
    而非共享是为了避免 governance.audit → gov_enforcement 的跨域依赖，同步靠测试覆盖保证）。

    注意：scripts/backup/ch_vm_ssh.py（无 test_ 前缀，有 blueprint MOD-INF-043）、
    scripts/ide_health_service.py、scripts/record_session_start_commit.py 等真能力脚本
    不命中任何豁免规则，仍在范围内（需大白话简介）。
    """
    # 只检测 .py 文件（翻译注册表面向 Python 模块）
    if not file_path.endswith(".py"):
        return False
    # tests/ 路径段（含 scripts/tests/）—— is_test_exempt 单一真源
    if is_test_exempt(file_path):
        return False
    # demos/ 路径段——演示脚本，非能力模块
    _norm = file_path.replace("\\", "/")
    if "demos" in _norm.split("/"):
        return False
    # test_*.py / *_test.py 文件名——测试文件（任意层级）
    _base = _norm.rsplit("/", 1)[-1]
    if _base.startswith("test_") or _base.endswith("_test.py"):
        return False
    # 包初始化 + 归档
    if file_path.endswith("__init__.py"):
        return False
    if "/_archive/" in file_path or file_path.startswith("_archive/"):
        return False
    return file_path.startswith(_SRC_ZEPHYR_PREFIX) or file_path.startswith(_SCRIPTS_PREFIX)


def _cjk_len(s: str) -> int:
    """统计 CJK 字符数（大白话最低信息量基线）。"""
    return len(re.findall(r"[\u4e00-\u9fff]", s or ""))


def _get_staged_new_py_files(gateway) -> list[str] | None:
    """获取 staged 新增 .py 文件列表（--diff-filter=A），过滤到 in-scope。

    对标 NEW-FILE-DEPGRAPH-ENFORCEMENT._get_staged_new_py_files。git diff 失败/异常
    时返回 None（fail-open 检测器失效）。
    """
    try:
        diff_result = gateway.run_git(["git", "diff", "--cached", "--name-only", "--diff-filter=A"])
        if diff_result.returncode != 0:
            logger.warning(
                "TRANSLATION-COVERAGE gate fail-open: git diff 失败(rc=%d)，检测器失效。",
                diff_result.returncode,
            )
            return None
        new_files: list[str] = []
        for line in diff_result.stdout.strip().splitlines():
            if not line.strip():
                continue
            file_path = line.strip().replace("\\", "/")
            if not file_path.endswith(".py"):
                continue
            if not _is_in_scope(file_path):
                continue
            new_files.append(file_path)
        return new_files
    except Exception as e:  # noqa: BLE001 — 5.135治标: broad exception catch
        logger.warning(
            "TRANSLATION-COVERAGE gate fail-open: git diff 异常(%s: %s)，检测器失效。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return None


def _check_translation_entry(file_path: str) -> str:
    """查翻译真源，返回违规类别（空串=合规）。

    懒加载 loader（跨 src/scripts 边界，对标 generate_domain_doc.py 的 sys.path 注入模式），
    避免注册时 import 失败。loader 不可达时返回 "__OPEN__"（fail-open，不阻断）。

    Returns:
        ``""``=合规；``"missing"``=无 entry 或 plain_zh 空；``"short"``=CJK 不足；
        ``"generic"``=通用模板；``"__OPEN__"``=loader 不可达（fail-open）。
    """
    try:
        from zephyr.shared.io.paths import REPO_ROOT

        _shared_dir = str(REPO_ROOT / "scripts" / "governance")
        if _shared_dir not in sys.path:
            sys.path.insert(0, _shared_dir)
        from _shared.module_translation_loader import (
            get_module_translation,
            is_generic_plain_suffix,
            is_generic_plain_zh,
        )
    except Exception as e:  # noqa: BLE001 — loader 不可达=环境异常，fail-open
        logger.warning(
            "TRANSLATION-COVERAGE gate fail-open: 翻译 loader 不可达(%s: %s)。",
            type(e).__name__,
            e,
            exc_info=True,
        )
        return "__OPEN__"

    try:
        trans = get_module_translation(file_path)
        if not trans:
            return "missing"
        plain = (trans.get("plain_zh") or "").strip()
        if not plain:
            return "missing"
        if _cjk_len(plain) < _MIN_CJK:
            return "short"
        if is_generic_plain_zh(plain):
            return "generic"
        name_zh = (trans.get("name_zh") or "").strip()
        if name_zh and is_generic_plain_suffix(plain, name_zh):
            return "generic"
        return ""
    except Exception as e:  # noqa: BLE001 — loader 查询异常=环境异常，fail-open
        logger.warning(
            "TRANSLATION-COVERAGE gate fail-open: 翻译查询异常(%s: %s) file=%s。",
            type(e).__name__,
            e,
            file_path,
            exc_info=True,
        )
        return "__OPEN__"


def _format_violation_detail(missing: list[str], short: list[str], generic: list[str]) -> str:
    """格式化违规详情字符串（每类限制显示数量）。"""
    parts: list[str] = []
    if missing:
        shown = missing[:5]
        suffix = f" (还有 {len(missing) - 5} 个)" if len(missing) > 5 else ""
        parts.append(f"无 plain_zh 简介[{', '.join(shown)}{suffix}]")
    if short:
        shown = short[:5]
        suffix = f" (还有 {len(short) - 5} 个)" if len(short) > 5 else ""
        parts.append(f"plain_zh CJK<{_MIN_CJK}[{', '.join(shown)}{suffix}]")
    if generic:
        shown = generic[:5]
        suffix = f" (还有 {len(generic) - 5} 个)" if len(generic) > 5 else ""
        parts.append(f"plain_zh 是通用模板[{', '.join(shown)}{suffix}]")
    return "；".join(parts)


def make_translation_coverage_gate() -> GateSpec:
    """构造新建 .py 文件大白话简介覆盖率门禁 GateSpec。

    Returns:
        GateSpec(gate_id="TRANSLATION-COVERAGE", priority=59)。
        priority=59——在 NEW-FILE-DEPGRAPH-ENFORCEMENT(58) 之后、CREATE-GUARD(60) 之前
        （先确认 depgraph 结构登记，再要求翻译完整性）。
    """

    def _check(gateway, files: list[str], **kwargs) -> tuple[bool, str]:
        # 1. 非 Zephyr 项目 skip（对标 NEW-FILE-DEPGRAPH-ENFORCEMENT）
        _governance_dir = gateway.project_root / "scripts" / "governance" / "d1_structure"
        if not _governance_dir.is_dir():
            return True, "non-Zephyr project (no scripts/governance/d1_structure), skipping TRANSLATION-COVERAGE"

        # 2. 获取 staged 新增 .py 文件（None=fail-open 检测器失效）
        new_py_files = _get_staged_new_py_files(gateway)
        if not new_py_files:
            return True, ""

        # 3. 只检测本次 commit 文件中的新增 .py（对标 depgraph gate 治本 2026-06-30）
        commit_files_rel: set[str] = set()
        for f in files:
            try:
                rel = os.path.relpath(f, str(gateway.project_root)).replace("\\", "/")
                commit_files_rel.add(rel)
            except (ValueError, OSError):
                continue
        new_py_files = [f for f in new_py_files if f in commit_files_rel]
        if not new_py_files:
            return True, ""

        # 4. 逐个查翻译真源
        missing: list[str] = []
        short: list[str] = []
        generic: list[str] = []
        for file_path in new_py_files:
            result = _check_translation_entry(file_path)
            if result == "__OPEN__":
                continue  # loader 不可达 → fail-open 此文件
            if result == "missing":
                missing.append(file_path)
            elif result == "short":
                short.append(file_path)
            elif result == "generic":
                generic.append(file_path)

        total = len(missing) + len(short) + len(generic)
        if not total:
            return True, ""

        # 5. 违规处理
        detail = _format_violation_detail(missing, short, generic)
        msg = (
            f"TRANSLATION-COVERAGE: {total} 个新建 .py 文件在翻译真源"
            f"（module_translation_registry.yaml）缺合格 plain_zh 大白话简介。"
            f"修复：python scripts/governance/d3_metadata/add_module_translation.py "
            f"--path <file_path> --domain <D_*> --name-zh <中文名> --plain-zh <大白话简介>。"
            f"详情: {detail}"
        )
        if _OBSERVATION_PERIOD:
            # 观察期：warn 不阻断（防上线即卡死其他 session），醒目日志 + stderr
            logger.warning("[OBSERVATION] %s", msg)
            print(f"[TRANSLATION-COVERAGE][OBSERVATION-WARN] {msg}", file=sys.stderr)
            return True, ""
        return False, msg

    return GateSpec(gate_id="TRANSLATION-COVERAGE", check=_check, priority=59)
