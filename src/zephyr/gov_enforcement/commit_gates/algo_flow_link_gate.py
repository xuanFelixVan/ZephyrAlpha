# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.algo_flow_link_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.shared.utils.time_utils
# [CONSUMERS] in_process_gate_registry.yaml（auto_register_gates YAML 驱动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——本 commit 触碰的 .py 中 ``# [ALGO_FLOW] external: <path>`` 锚指向的 yaml 必须存在且
#   algo_flow 块可解析（parse_algo_flow 有节点），本 commit 触碰的 */algo_flow/*.yaml 必须自身可解析且
#   source_of_truth 指向实存源文件（Owner 批7 认可，2026-09-16）；own-diff 扫描——只查本次 commit files 清单，
#   他会话 staged 文件零接触（#ARCH-GATE-OWN-SCOPE-001 单一真源模式）；staged 内容优先（锚校验读 staged，
#   无 staged 回退工作区）；fail-open（git/文件不可读/yaml 解析器不可用等基础设施故障放行，logger.warning）；
#   检出本 commit 违规 fail-closed
# [MODIFY-GUARD] gate_id="ALGO-FLOW-LINK"; check 闭包签名 (gateway, files, **kwargs) -> tuple[bool, str]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] check 永不抛异常——基础设施异常降级 fail-open（passed=True）；检出违规 fail-closed
# [TESTS] tests/governance/commit_gates/test_algo_flow_link_gate.py
# [A_module] module_id=MOD-GATE_ENGINE | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
# noqa: m10-time-trigger  M10豁免: 本模块由 commit 事件触发（非 cron/manual）
"""algo_flow_link_gate.py — ALGO_FLOW external 锚链接校验门禁（ALGO-FLOW-LINK）

病根（第一性原理）
-----------------
P2-1 ALGO_FLOW 出仓战役后，源码 docstring 以单行 external 锚引用
docs/03_modules/<domain>/algo_flow/<stem>.yaml，算法图真源在 yaml 侧。
锚与 yaml 是跨文件双真源对——删 yaml/改锚路径/yaml 块语法坏/锚指向不存在文件，
全景图消费方（extractor）静默拿空图，无任何门禁拦截（批9 收尾批红蓝预演实证
"锚改道产生重复 yaml+锚错位"与"yaml 落盘而源锚缺失"两类真实漂移）。

治本方案（Owner 批7 认可，2026-09-16 落地）
--------
pre-commit 注册（priority=108，own-diff）：
  1. 本 commit files 中每个 .py：扫 external 锚 → 目标 yaml 存在 + algo_flow 块可解析
  2. 本 commit files 中每个 */algo_flow/*.yaml：可解析 + source_of_truth 实存
  3. 违规聚合一次给全，硬阻断；基础设施故障 fail-open

设计权衡
--------
1. own-diff：files 参数即本次 commit 清单（gateway 构造性保证不含他会话文件），
   外来 staged 零接触——对称 IMPORT-INTEGRITY 的 own-scope 治本口径。
2. staged 内容优先：优先读 staged 版本（commit 语义真源），读不到回退工作区。
3. parse_algo_flow 复用 extractor 管线（_shared.code_algorithm_extractor），
   与全景图消费方同一解析器——门禁判"可解析"即消费方可解析，无第二真源。
4. fail-open 只用于基础设施故障；链接断/块坏=真违规，阻断。
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Callable

logger = logging.getLogger(__name__)

_ANCHOR_RE = re.compile(r"^\s*#\s*\[ALGO_FLOW\]\s+external:\s*(\S+)\s*$", re.MULTILINE)
_ALGO_FLOW_DIR_SEG = "algo_flow"
_ALGO_FLOW_START = "# [ALGO_FLOW]"
_ALGO_FLOW_END = "# [/ALGO_FLOW]"


def _norm_posix(f: str | Path, repo_root: Path) -> str:
    p = Path(f)
    try:
        p = p.relative_to(repo_root)
    except ValueError:
        pass
    return p.as_posix()


def check_algo_flow_links(
    files: list[str] | None,
    project_root: str | Path,
    read_staged: Callable[[str], str | None] | None = None,
) -> tuple[bool, str]:
    """纯逻辑核心（可单测，不触 git）。

    Args:
        files: 本次 commit 文件清单（相对/绝对路径混合容忍）。
        project_root: 仓库根。
        read_staged: staged 内容读取器（测试注入/网关注入）；None=直接读工作区。

    Returns:
        (blocked, message)
    """
    if not files:
        return False, ""
    root = Path(project_root)
    py_files: list[str] = []
    yaml_files: list[str] = []
    for f in files:
        rel = _norm_posix(f, root)
        if rel.endswith(".py"):
            py_files.append(rel)
        elif rel.endswith(".yaml") and f"/{_ALGO_FLOW_DIR_SEG}/" in f"/{rel}":
            yaml_files.append(rel)

    def _read(rel: str) -> str | None:
        if read_staged is not None:
            content = read_staged(rel)
            if content is not None:
                return content
        try:
            return (root / rel).read_text(encoding="utf-8")
        except OSError:
            return None

    # 延迟导入 yaml（失败=基础设施故障 fail-open）；extractor 可用则全解析，否则结构校验
    try:
        import yaml as pyyaml
    except Exception:  # noqa: BLE001 — 基础设施故障 fail-open
        logger.warning("ALGO-FLOW-LINK fail-open: yaml 解析器加载失败", exc_info=True)
        return False, ""

    def _validate_block(content: str) -> tuple[bool, str]:
        """yaml 文本 → (ok, why)：可解析 + algo_flow 块结构完整（+extractor 全解析当可用）。"""
        try:
            doc = pyyaml.safe_load(content) or {}
        except Exception as e:  # noqa: BLE001
            return False, f"yaml 解析失败: {type(e).__name__}"
        block = (doc or {}).get("algo_flow")
        if not isinstance(block, str) or not block.strip():
            return False, "缺 algo_flow 块"
        if _ALGO_FLOW_START not in block or _ALGO_FLOW_END not in block:
            return False, "algo_flow 块缺起/收标记"
        if "# - id:" not in block:
            return False, "algo_flow 块无节点行"
        try:
            from _shared.code_algorithm_extractor import parse_algo_flow  # noqa: PLC0415

            if parse_algo_flow(block) is None:
                return False, "parse_algo_flow 无节点"
        except ImportError:
            pass  # extractor 不在 sys.path——结构校验兜底
        except Exception as e:  # noqa: BLE001
            return False, f"parse_algo_flow 异常: {type(e).__name__}"
        return True, ""

    failures: list[str] = []

    for rel in py_files:
        content = _read(rel)
        if content is None:
            continue  # 文件读取失败（删除/权限）——非本门职责
        for m in _ANCHOR_RE.finditer(content):
            target = m.group(1)
            tgt = root / target
            if not tgt.is_file():
                failures.append(f"{rel} external 锚指向不存在的 yaml: {target}")
                continue
            ok, why = _validate_block(tgt.read_text(encoding="utf-8"))
            if not ok:
                failures.append(f"{rel} external 锚 yaml 不可解析: {target}（{why}）")

    for rel in yaml_files:
        content = _read(rel)
        if content is None:
            failures.append(f"{rel} algo_flow yaml 不可读（已删除?）")
            continue
        ok, why = _validate_block(content)
        if not ok:
            failures.append(f"{rel} algo_flow 块不可解析（{why}）")
            continue
        try:
            doc = pyyaml.safe_load(content) or {}
            sot = (doc or {}).get("source_of_truth")
        except Exception:  # noqa: BLE001 — 已由 _validate_block 兜底
            sot = None
        if not sot:
            failures.append(f"{rel} 缺 source_of_truth 头")
        elif not (root / str(sot)).is_file():
            failures.append(f"{rel} source_of_truth 指向不存在的源文件: {sot}")

    if failures:
        return True, (
            f"ALGO-FLOW-LINK：{len(failures)} 处 ALGO_FLOW 锚/卡片链接断裂——"
            "external 锚指向的 yaml 必须存在且可解析，yaml 的 source_of_truth 必须实存"
            "（Owner 批7 认可，2026-09-16）。"
            + "；".join(failures[:20])
        )
    return False, ""


def make_algo_flow_link_gate() -> object:
    """构造 ALGO_FLOW 锚链接校验 GateSpec（硬阻断型，priority=108，own-diff）。"""
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

    def _check(gateway: object, files: list[str] | None, **kwargs: object) -> tuple[bool, str]:
        try:
            project_root = Path(str(gateway.project_root))

            def _read_staged(rel: str) -> str | None:
                try:
                    return gateway.read_staged_file(rel)  # 网关如有 staged 读取器则用
                except Exception:  # noqa: BLE001
                    return None

            blocked, msg = check_algo_flow_links(files, project_root, read_staged=_read_staged)
            return (not blocked), msg
        except Exception as exc:  # noqa: BLE001 — 基础设施故障 fail-open
            logger.warning("ALGO-FLOW-LINK fail-open: %s", exc)
            return True, ""

    return GateSpec(gate_id="ALGO-FLOW-LINK", check=_check, priority=108)
