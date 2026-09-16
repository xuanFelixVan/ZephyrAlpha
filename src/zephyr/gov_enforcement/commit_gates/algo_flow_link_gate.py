# [BLUEPRINT] MOD-GATE_ENGINE | docs/03_modules/_cross_layer/gate_engine/blueprint.md | §0.1
# [MODULE] zephyr.gov_enforcement.commit_gates.algo_flow_link_gate
# [DOMAIN] D_GOV_CODE_QUALITY
# [DEPENDENCIES] zephyr.gov_enforcement.rule_bridge.commit_gate_registry (GateSpec); zephyr.gov_enforcement.commit_gates._diff_helpers (_read_staged_file); zephyr.shared.utils.time_utils;
#   scripts.governance._shared.code_algorithm_extractor（解析+死块几何）; scripts.governance._shared.algo_flow_validate_marker（validate_graph 图判据真源）
# [CONSUMERS] in_process_gate_registry.yaml（auto_register_gates YAML 驱动注册）
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 硬阻断——本 commit 触碰的 .py 中 ``# [ALGO_FLOW] external: <path>`` 锚指向的 yaml 必须存在且
#   algo_flow 块可解析（parse_algo_flow 有节点）+ 图可达（validate_graph：节点 id 合法唯一/至少一条边/
#   边端点已定义/断点一致——图坏=全景图静默空图，判据真源在 algo_flow_validate_marker 不重写第二份），
#   本 commit 触碰的 */algo_flow/*.yaml 必须自身可解析且
#   source_of_truth 指向实存源文件（Owner 批7 认可，2026-09-16），且本 commit 触碰的 src/zephyr .py
#   不得在 module docstring 之外另留 ALGO_FLOW 机器块，
#   docstring 之内只允许一个载体（锚或块二选一，两处并存=永不被消费的副本=双真源；P2-1 死块批
#   2026-09-16 增、体内多块线 2026-09-17 增、锚块并存同日经红蓝实弹哑火后并入同一判据；
#   几何判据共用 extractor.algo_flow_dead_block_spans 与
#   extractor.duplicate_inline_algo_flow_spans，extractor 不可用=基础设施故障 fail-open）；
#   own-diff 扫描——只查本次 commit files 清单，
#   他会话 staged 文件零接触（#ARCH-GATE-OWN-SCOPE-001 单一真源模式）；staged 内容优先（锚校验读 staged，
#   经 _diff_helpers._read_staged_file=``git show :<path>``，无 staged 回退工作区）；
#   fail-open（git/文件不可读/yaml 解析器不可用等基础设施故障放行，logger.warning）；
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
  1. 本 commit files 中每个 .py：扫 external 锚 → 目标 yaml 存在 + algo_flow 块可解析 + 图可达
  2. 本 commit files 中每个 */algo_flow/*.yaml：可解析 + 图可达 + source_of_truth 实存
  3. 图可达判据 = algo_flow_validate_marker.validate_graph（id 合法唯一 / 至少一条边 /
     边端点已定义 / 断点边一致）——"可解析"曾经是太弱的门槛：2026-09-16 全仓普查实证
     "- id: I1 中文描述" 让 17 件节点 id 吞掉描述（mermaid 节点键含空格必炸 + 边端点全体悬空）、
     "# I1,I2 --> F1" 并列写法让 29 件边数静默归零、yaml 块标量的行首缩进让边行整体不匹配
     （三处都在 extractor 治本）——坏图在门禁全绿下存活，正是"假绿"类
  4. 本 commit files 中每个 src/zephyr .py：module docstring 之外不得另留 ALGO_FLOW 机器块
     （P2-1 死块普查实证：14 字段契约头里的副本所有读卡路径都看不见，锚+副本=双真源，
     184 件长期静默存活；几何判据与出仓器共用 extractor.algo_flow_dead_block_spans）
  5. 同件 docstring **之内**只允许一个 ALGO_FLOW 载体（锚或机器块二选一）：
     - 块+块：parse_algo_flow 只认首个起→止 对（§4.16），第 2 块连同其边段全体不可达，
       全景图显示半张图而作者以为显示整张；
     - 锚+块：锚已外链，写回的块永不被读卡路径消费=货真价实的第二真源——2026-09-17
       红蓝实弹 R2 经生产队列链路真落地（HEAD=b873ee71d3）暴露本形态原判据哑火，
       因原判据把锚行排除在候选外，"锚+一块"数出来只有 1，遂判合法。
     与死块同属"静默不可达"类、只是几何位置相反，故判据分家：
     extractor.duplicate_inline_algo_flow_spans（2026-09-17 普查 src/zephyr 3576 件
     体内多块=0、锚块并存=0，本判据是零存量防复发线）
  6. 违规聚合一次给全，硬阻断；基础设施故障 fail-open

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


def _load_graph_rules(root: Path) -> tuple[Callable, Callable, Callable, Callable] | None:
    """取判据真源 (parse_algo_flow, validate_graph, algo_flow_dead_block_spans,
    duplicate_inline_algo_flow_spans)。

    判据一律不在门禁内重写第二份：解析/图规则真源在 scripts/governance/_shared，
    几何规则真源在 extractor。找不到落点返回 None=基础设施故障降级。
    网关进程未必已把 scripts/governance 放进 sys.path——不补 bootstrap 判据会静默
    fail-open（与 import_integrity_gate 同源套路）。
    """
    import sys

    def _try():
        from _shared.algo_flow_validate_marker import validate_graph  # noqa: PLC0415
        from _shared.code_algorithm_extractor import (  # noqa: PLC0415
            algo_flow_dead_block_spans,
            duplicate_inline_algo_flow_spans,
            parse_algo_flow,
        )

        return parse_algo_flow, validate_graph, algo_flow_dead_block_spans, (
            duplicate_inline_algo_flow_spans
        )

    try:
        return _try()
    except ImportError:
        pass
    cands = (
        root / "scripts" / "governance",
        Path(__file__).resolve().parents[4] / "scripts" / "governance",
    )
    gov = next((c for c in cands if (c / "_shared" / "code_algorithm_extractor.py").is_file()), None)
    if gov is None:
        return None
    if str(gov) not in sys.path:
        sys.path.insert(0, str(gov))
    try:
        return _try()
    except ImportError:
        return None


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

    # 判据一次加载复用（sys.modules 已缓存，但每文件两轮 import 查找纯属浪费）
    rules = _load_graph_rules(root)
    if rules is None:
        logger.warning("ALGO-FLOW-LINK 判据降级：scripts/governance/_shared 不可达，仅结构校验")

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
        if rules is None:
            return True, ""  # extractor 不在 sys.path——结构校验兜底（判据不重写第二份）
        parse_algo_flow, validate_graph = rules[0], rules[1]
        try:
            data = parse_algo_flow(block)
        except Exception as e:  # noqa: BLE001
            return False, f"parse_algo_flow 异常: {type(e).__name__}"
        if data is None:
            return False, "parse_algo_flow 无节点"
        problems = validate_graph(data)
        if problems:
            return False, "推导图不可达：" + "；".join(problems[:4])
        return True, ""

    failures: list[str] = []

    def _dead_block_lines(content: str) -> list[int]:
        """docstring 外的 ALGO_FLOW 块起行（1 基）；判据不可用=基础设施故障放行。"""
        if rules is None:
            return []
        try:
            return [s + 1 for s, _e, _c in rules[2](content)]
        except Exception as e:  # noqa: BLE001
            logger.warning("ALGO-FLOW-LINK 双真源检出异常: %s", e)
            return []

    def _dup_inline_lines(content: str) -> list[int]:
        """docstring 内第 2+ 个 ALGO_FLOW 块起行（1 基）——与死块同族但几何位置相反。"""
        if rules is None:
            return []
        try:
            return [s + 1 for s, _e, _c in rules[3](content)]
        except Exception as e:  # noqa: BLE001
            logger.warning("ALGO-FLOW-LINK 体内多块检出异常: %s", e)
            return []

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
        if rel.startswith("src/zephyr/"):
            dead = _dead_block_lines(content)
            if dead:
                failures.append(
                    f"{rel} 有 {len(dead)} 处 ALGO_FLOW 机器块落在 module docstring 之外"
                    f"（起行 {dead[:3]}）——锚与体外副本并存=双真源，所有读卡路径只读 "
                    "docstring，副本永不被消费也永不更新；清偿："
                    f"python scripts/governance/d5_architecture/generators/externalize_algo_flow.py --file {rel}"
                )
            dup = _dup_inline_lines(content)
            if dup:
                failures.append(
                    f"{rel} 的 module docstring 内有 {len(dup)} 处多余 ALGO_FLOW 机器块"
                    f"（起行 {dup[:3]}）——一个 docstring 只能有一个 ALGO_FLOW 载体：parse_algo_flow "
                    "只认首个 起→止 对，其后每块连同自己的边段全体不可达；锚已在场外指真源，"
                    "体内再写块=永不被消费的副本。全景图显示半张图而作者以为显示整张，"
                    "与体外死块同属静默不可达类（只是几何位置相反，故判据分家）。清偿："
                    "把多块合并成单一块，或跑 externalize_algo_flow.py 外迁后留一行锚"
                )

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
    from zephyr.gov_enforcement.commit_gates._diff_helpers import _read_staged_file
    from zephyr.gov_enforcement.rule_bridge.commit_gate_registry import GateSpec

    def _check(gateway: object, files: list[str] | None, **kwargs: object) -> tuple[bool, str]:
        try:
            project_root = Path(str(gateway.project_root))

            def _read_staged(rel: str) -> str | None:
                """staged blob 真源（#ARCH-321 治本）。

                原写法调 ``gateway.read_staged_file``——网关无此方法，异常被宽 except
                吞掉后静默回退读磁盘：门禁判的于是是工作区内容，而 commit 落的是 index
                内容。staged≠磁盘（他会话 staged 未改、或本会话改完未 add）时双向误判，
                与 #ARCH-316 治的"观测面错位"同病。判据不重写第二份，复用同包
                ``_diff_helpers._read_staged_file``（``git show :<path>`` + run_git 双解码）。
                """
                return _read_staged_file(gateway, rel)

            blocked, msg = check_algo_flow_links(files, project_root, read_staged=_read_staged)
            return (not blocked), msg
        except Exception as exc:  # noqa: BLE001 — 基础设施故障 fail-open
            logger.warning("ALGO-FLOW-LINK fail-open: %s", exc)
            return True, ""

    return GateSpec(gate_id="ALGO-FLOW-LINK", check=_check, priority=108)
